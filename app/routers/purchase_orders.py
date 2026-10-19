"""采购订单：创建 / 收货入库（联动库存、成本、应付账款、流水）/ 列表。"""

import json
from decimal import Decimal, ROUND_HALF_UP

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlmodel import Session, select, update

from app.database import get_session
from app.deps import Actor, RequirePermission # 🌟 引入细粒度权限
from app.models import AutoPart, InventoryTransaction, PurchaseOrder, Supplier
from app.schemas import CreatePurchaseOrderRequest
from app.services.numbering import make_po_no
from app.services.audit import log_action

router = APIRouter(tags=["采购"])


@router.post("/api/purchase-orders")
@router.post("/api/purchase-orders/create")
def create_purchase_order(
    payload: CreatePurchaseOrderRequest,
    actor: Actor = Depends(RequirePermission("procurement:view")), # 🌟 暂用 view 作为采购权限，如果有 manage 请替换
    session: Session = Depends(get_session),
):
    # 1. 供应商不存在则自动建档
    supplier_name = payload.supplier_name.strip()
    supplier = session.exec(select(Supplier).where(Supplier.name == supplier_name)).first()
    if not supplier:
        supplier = Supplier(name=supplier_name, contact_person="默认联系人", debt_usd=0.0)
        session.add(supplier)
        session.flush()

    # 🌟 核心修复：使用 Decimal 累加总金额，防止精度丢失
    total_amount_cents = 0
    items_snapshot = []
    
    for item in payload.items:
        d_price = Decimal(str(item.unit_price))
        d_qty = Decimal(str(item.quantity))
        # 每行金额四舍五入到分，再累加
        line_total = (d_price * d_qty).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        total_amount_cents += int(line_total * 100)
        
        items_snapshot.append(item.model_dump())

    total_amount_usd = total_amount_cents / 100
    po_no = make_po_no()

    po = PurchaseOrder(
        po_no=po_no,
        supplier_id=supplier.id,
        status="PENDING",
        total_amount_usd=total_amount_usd,
        items_json=json.dumps(items_snapshot, ensure_ascii=False),
    )
    session.add(po)

    log_action(
        session=session,
        username=actor.username,
        role=actor.role,
        action="CREATE_PURCHASE_ORDER",
        details=f"创建采购单: {po_no}, 供应商: {supplier_name}, 预估总价: ${total_amount_usd:.2f}",
    )

    session.commit()
    session.refresh(po)
    return {"status": "success", "po_id": po.id, "po_no": po_no, "message": "采购订单创建成功（待收货入库）"}


@router.post("/api/purchase-orders/{po_id}/receive")
def receive_purchase_order(
    po_id: int, 
    actor: Actor = Depends(RequirePermission("procurement:view")), # 🌟 加上权限
    session: Session = Depends(get_session)
):
    try:
        # 🌟 核心修复 1：使用原子性 Update 抢占状态，防止并发“双重入库”
        # 只有状态为 PENDING 的才能被修改为 RECEIVING，如果两个请求同时进来，只有一个能 rowcount == 1
        claimed = session.exec(
            update(PurchaseOrder)
            .where(PurchaseOrder.id == po_id, PurchaseOrder.status == "PENDING")
            .values(status="RECEIVING")
        )
        if claimed.rowcount == 0:
            # 重新查一下，判断具体原因
            po_check = session.get(PurchaseOrder, po_id)
            if not po_check:
                raise HTTPException(status_code=404, detail="采购订单不存在")
            raise HTTPException(status_code=400, detail="该采购订单已经被收货或正在处理中，请勿重复操作")

        po = session.get(PurchaseOrder, po_id)

        # 2. 解析采购单明细
        try:
            items_data = json.loads(po.items_json) if po.items_json else []
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"解析采购单明细失败: {e}")

        supplier = session.get(Supplier, po.supplier_id)
        
        # 3. 逐项更新库存 / 写入流水
        total_order_amount_cents = 0

        for item_dict in items_data:
            oem = item_dict.get("oem")
            name = item_dict.get("name")
            quantity = item_dict.get("quantity", 0)
            
            # 🌟 核心修复 2：从 JSON 取出来的金额也必须用 Decimal 转换
            unit_price = float(item_dict.get("unit_price", 0.0))
            d_price = Decimal(str(unit_price))
            d_qty = Decimal(str(quantity))
            
            line_total = (d_price * d_qty).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            total_order_amount_cents += int(line_total * 100)

            part = session.exec(select(AutoPart).where(AutoPart.oem == oem)).first()

            if part:
                # 🌟 核心修复 3：只增加库存，【绝对不要】覆盖原零售价！成本价应记录在流水或单独字段里。
                session.exec(
                    update(AutoPart)
                    .where(AutoPart.oem == oem)
                    .values(stock=AutoPart.stock + quantity)
                )
            else:
                # 库里还没有这个配件时自动建档，此时没有售价，暂时把进货价当作售价占位
                session.add(AutoPart(
                    name=name,
                    oem=oem,
                    stock=quantity,
                    price=unit_price, 
                ))

            session.add(InventoryTransaction(
                part_oem=oem,
                part_name=name,
                type="PURCHASE_RECEIVE",
                quantity=quantity,
                unit_price=unit_price,
                total_amount=float(line_total),
                customer_or_supplier=supplier.name if supplier else "Unknown Supplier",
            ))

        # 4. 累加供应商应付账款
        if supplier:
            total_order_amount = total_order_amount_cents / 100
            session.exec(
                update(Supplier)
                .where(Supplier.id == supplier.id)
                .values(debt_usd=func.coalesce(Supplier.debt_usd, 0.0) + total_order_amount)
            )

        # 5. 采购单状态置为已收货
        po.status = "received"
        session.add(po)

        # 6. 原子提交
        session.commit()

        log_action(
            session=session,
            username=actor.username,
            role=actor.role,
            action="RECEIVE_PURCHASE_ORDER",
            details=f"采购收货完成: {po.po_no}, 供应商: {supplier.name if supplier else '未知'}, 总金额: ${total_order_amount_cents / 100:.2f}",
        )

        return {
            "status": "success",
            "po_id": po_id,
            "message": "收货成功：库存已增加、流水已记录、供应商应付账款已累加！",
        }

    except HTTPException:
        session.rollback()
        raise
    except Exception as e:
        session.rollback()
        print(f"❌ 采购收货发生严重异常，已执行事务回滚。错误详情: {e}")
        raise HTTPException(status_code=500, detail=f"收货处理失败，已安全回滚: {str(e)}")


@router.get("/api/purchase-orders")
def get_purchase_orders(
    session: Session = Depends(get_session),
    actor: Actor = Depends(RequirePermission("procurement:view")) # 🌟 加上权限
):
    """采购订单列表（按创建时间倒序）。"""
    return session.exec(select(PurchaseOrder).order_by(PurchaseOrder.id.desc())).all()