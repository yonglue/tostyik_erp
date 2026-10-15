"""采购订单：创建 / 收货入库（联动库存、成本、应付账款、流水）/ 列表。"""

import json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlmodel import Session, select, update

from app.database import get_session
from app.deps import Actor, get_current_actor
from app.models import AutoPart, InventoryTransaction, PurchaseOrder, Supplier
from app.schemas import CreatePurchaseOrderRequest
from app.services.numbering import make_po_no
from app.services.audit import log_action

router = APIRouter(tags=["采购"])


@router.post("/api/purchase-orders")
@router.post("/api/purchase-orders/create")
def create_purchase_order(
    payload: CreatePurchaseOrderRequest,
    actor: Actor = Depends(get_current_actor),
    session: Session = Depends(get_session),
):
    # 1. 供应商不存在则自动建档，避免"找不到记录"报错
    supplier_name = payload.supplier_name.strip()
    supplier = session.exec(select(Supplier).where(Supplier.name == supplier_name)).first()
    if not supplier:
        supplier = Supplier(name=supplier_name, contact_person="默认联系人", debt_usd=0.0)
        session.add(supplier)
        # 只 flush 取 id：新供应商也并入本单事务，建单失败时不会留下孤立供应商
        session.flush()

    total_amount = sum(item.unit_price * item.quantity for item in payload.items)
    po_no = make_po_no()
    items_snapshot = [item.model_dump() for item in payload.items]

    po = PurchaseOrder(
        po_no=po_no,
        supplier_id=supplier.id,
        status="PENDING",
        total_amount_usd=total_amount,
        items_json=json.dumps(items_snapshot, ensure_ascii=False),
    )
    session.add(po)

    log_action(
        session=session,
        username=actor.username,
        role=actor.role,
        action="CREATE_PURCHASE_ORDER",
        details=f"创建采购单: {po_no}, 供应商: {supplier_name}, 预估总价: ${total_amount:.2f}",
    )

    session.commit()
    session.refresh(po)
    return {"status": "success", "po_id": po.id, "po_no": po_no, "message": "采购订单创建成功（待收货入库）"}


@router.post("/api/purchase-orders/{po_id}/receive")
def receive_purchase_order(po_id: int, session: Session = Depends(get_session)):
    try:
        # 1. 查找采购订单
        po = session.get(PurchaseOrder, po_id)
        if not po:
            raise HTTPException(status_code=404, detail="采购订单不存在")

        if po.status == "received":
            raise HTTPException(status_code=400, detail="该采购订单已经完成收货，请勿重复操作")

        # 2. 解析采购单中用 JSON 存储的商品明细
        try:
            items_data = json.loads(po.items_json) if po.items_json else []
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"解析采购单明细失败: {e}")

        # 3. 查找对应的供应商
        supplier = session.get(Supplier, po.supplier_id)

        total_order_amount = 0.0

        # 4. 逐项更新库存 / 售价、写入库存流水
        for item_dict in items_data:
            oem = item_dict.get("oem")
            name = item_dict.get("name")
            quantity = item_dict.get("quantity", 0)
            unit_price = item_dict.get("unit_price", 0.0)

            item_total = quantity * unit_price
            total_order_amount += item_total

            part = session.exec(select(AutoPart).where(AutoPart.oem == oem)).first()

            if part:
                # 用 SQL 级自增，避免与其它出入库并发时丢失更新
                session.exec(
                    update(AutoPart)
                    .where(AutoPart.oem == oem)
                    .values(stock=AutoPart.stock + quantity, price=unit_price)
                )
            else:
                # 库里还没有这个配件时自动建档
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
                total_amount=item_total,
                customer_or_supplier=supplier.name if supplier else "Unknown Supplier",
            ))

        # 5. 累加供应商应付账款
        if supplier:
            # SQL 级累加（coalesce 兼容历史 NULL），避免同一供应商并发收货时丢失应付账款
            session.exec(
                update(Supplier)
                .where(Supplier.id == supplier.id)
                .values(debt_usd=func.coalesce(Supplier.debt_usd, 0.0) + total_order_amount)
            )

        # 6. 采购单置为已收货
        po.status = "received"
        session.add(po)

        # 7. 原子提交：要么全成功，要么全不生效
        session.commit()

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
def get_purchase_orders(session: Session = Depends(get_session)):
    """采购订单列表（按创建时间倒序）。"""
    return session.exec(select(PurchaseOrder).order_by(PurchaseOrder.id.desc())).all()
