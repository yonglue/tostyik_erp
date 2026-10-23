"""采购订单：创建 / 收货入库（联动库存、成本、应付账款、流水）/ 列表。"""

import json
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select, update

from app.database import get_session
from app.deps import Actor, RequirePermission
from app.models import AutoPart, InventoryTransaction, PurchaseOrder, Supplier, SupplierPaymentRecord
from app.schemas import CreatePurchaseOrderRequest, SupplierPaymentPayload
from app.services.numbering import make_po_no
from app.services.audit import log_action
from app.services.fx import to_usd

router = APIRouter(tags=["采购"])


# ──────────────────────────── 供应商接口 ────────────────────────────
class SupplierCreatePayload(BaseModel):
    name: str
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None

class SupplierUpdatePayload(BaseModel):
    name: str
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None


@router.get("/api/suppliers")
def get_suppliers(
    session: Session = Depends(get_session),
    actor: Actor = Depends(RequirePermission("procurement:view"))
):
    """获取所有供应商列表"""
    return session.exec(select(Supplier).order_by(Supplier.name)).all()


@router.post("/api/suppliers")
def create_supplier(
    payload: SupplierCreatePayload,
    session: Session = Depends(get_session),
    actor: Actor = Depends(RequirePermission("procurement:manage"))
):
    """新建供应商"""
    existing = session.exec(select(Supplier).where(Supplier.name == payload.name)).first()
    if existing:
        raise HTTPException(status_code=400, detail="该供应商名称已存在")
    
    sup = Supplier(
        name=payload.name,
        contact_person=payload.contact_person or "",
        phone=payload.phone or "",
        address=payload.address or "",
        debt_usd=0.0
    )
    session.add(sup)
    session.commit()
    session.refresh(sup)
    return sup


@router.put("/api/suppliers/{supplier_id}")
def update_supplier(
    supplier_id: int,
    payload: SupplierUpdatePayload,
    session: Session = Depends(get_session),
    actor: Actor = Depends(RequirePermission("procurement:manage"))
):
    """修改供应商"""
    sup = session.get(Supplier, supplier_id)
    if not sup:
        raise HTTPException(status_code=404, detail="供应商不存在")
        
    if sup.name != payload.name:
        existing = session.exec(select(Supplier).where(Supplier.name == payload.name)).first()
        if existing:
            raise HTTPException(status_code=400, detail="该供应商名称已存在")
            
    sup.name = payload.name
    sup.contact_person = payload.contact_person or ""
    sup.phone = payload.phone or ""
    sup.address = payload.address or ""
    
    session.add(sup)
    session.commit()
    session.refresh(sup)
    return sup


@router.delete("/api/suppliers/{supplier_id}")
def delete_supplier(
    supplier_id: int,
    session: Session = Depends(get_session),
    actor: Actor = Depends(RequirePermission("procurement:manage"))
):
    """删除供应商（带有安全检查）"""
    sup = session.get(Supplier, supplier_id)
    if not sup:
        raise HTTPException(status_code=404, detail="供应商不存在")
        
    if sup.debt_usd > 0:
        raise HTTPException(status_code=400, detail=f"该供应商尚有应付欠款 ${sup.debt_usd:.2f}，无法删除！")
        
    has_po = session.exec(select(PurchaseOrder).where(PurchaseOrder.supplier_id == supplier_id)).first()
    if has_po:
        raise HTTPException(status_code=400, detail="该供应商存在历史采购单，为保证数据完整性，禁止删除！")

    session.delete(sup)
    session.commit()
    return {"status": "success", "message": "供应商已删除"}


# ──────────────────────────── 供应商付款 ────────────────────────────
@router.post("/api/suppliers/{supplier_id}/pay")
def pay_supplier(
    supplier_id: int,
    payload: SupplierPaymentPayload,
    session: Session = Depends(get_session),
    actor: Actor = Depends(RequirePermission("procurement:manage")),
):
    sup = session.get(Supplier, supplier_id)
    if not sup:
        raise HTTPException(status_code=404, detail="供应商不存在")

    # 🌟 强制使用服务端权威汇率折算，忽略前端传入的 exchange_rate
    try:
        amount_usd, rate_snapshot = to_usd(payload.amount_paid, payload.currency)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    if amount_usd <= 0:
        raise HTTPException(status_code=400, detail="付款金额必须大于 0")

    current_debt = Decimal(str(sup.debt_usd or 0)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    if amount_usd > current_debt:
        raise HTTPException(status_code=400, detail=f"付款金额 ${amount_usd:.2f} 超过欠款 ${current_debt:.2f}")

    # 原子扣减应付账款，防并发冲突
    paid = session.exec(
        update(Supplier)
        .where(
            Supplier.id == sup.id,
            func.coalesce(Supplier.debt_usd, 0.0) >= float(amount_usd),
        )
        .values(
            debt_usd=func.round(
                func.coalesce(Supplier.debt_usd, 0.0) - float(amount_usd), 2
            )
        )
        .execution_options(synchronize_session=False)
    )
    if paid.rowcount != 1:
        session.rollback()
        raise HTTPException(status_code=409, detail="应付账款已变化，请刷新后重试")

    record = SupplierPaymentRecord(
        supplier_id=sup.id,
        supplier_name=sup.name,
        amount_usd=float(amount_usd),
        currency=payload.currency.strip().upper(),
        original_amount=float(payload.amount_paid),
        exchange_rate=float(rate_snapshot.rate) if rate_snapshot else 1.0,
        payment_method=payload.payment_method,
        reference_no=payload.reference_no,
        notes=payload.notes,
    )
    session.add(record)
    session.commit()

    rate_desc = f"，汇率 {rate_snapshot.rate}（{rate_snapshot.source}）" if rate_snapshot else ""
    log_action(
        session, actor.username, actor.role, "SUPPLIER_PAYMENT",
        f"向供应商 {sup.name} 付款: ${amount_usd:.2f} USD（原币 {payload.amount_paid} {payload.currency}{rate_desc}）",
    )
    return {"status": "success", "message": "付款成功", "amount_usd": float(amount_usd)}


# ──────────────────────────── 采购订单接口 ────────────────────────────
@router.post("/api/purchase-orders")
@router.post("/api/purchase-orders/create")
def create_purchase_order(
    payload: CreatePurchaseOrderRequest,
    actor: Actor = Depends(RequirePermission("procurement:view")),
    session: Session = Depends(get_session),
):
    supplier_name = payload.supplier_name.strip()
    if not supplier_name:
        supplier_name = "默认供应商 / 散客"
        
    supplier = session.exec(select(Supplier).where(Supplier.name == supplier_name)).first()
    if not supplier:
        supplier = Supplier(name=supplier_name, contact_person="默认联系人", debt_usd=0.0)
        session.add(supplier)
        session.flush()

    po_no = payload.po_no.strip() if payload.po_no and payload.po_no.strip() else make_po_no()
    
    existing_po = session.exec(select(PurchaseOrder).where(PurchaseOrder.po_no == po_no)).first()
    if existing_po:
        raise HTTPException(status_code=400, detail=f"采购单号 {po_no} 已存在，请更换其他单号")

    total_amount_cents = 0
    items_snapshot = []
    
    for item in payload.items:
        d_price = Decimal(str(item.unit_price))
        d_qty = Decimal(str(item.quantity))
        line_total = (d_price * d_qty).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        total_amount_cents += int(line_total * 100)
        
        snapshot = item.model_dump()
        snapshot["unit_price"] = float(item.unit_price)
        items_snapshot.append(snapshot)

    total_amount_usd = total_amount_cents / 100

    po = PurchaseOrder(
        po_no=po_no,
        supplier_id=supplier.id,
        status="PENDING",
        total_amount_usd=total_amount_usd,
        items_json=json.dumps(items_snapshot, ensure_ascii=False),
    )
    session.add(po)
    session.commit()
    session.refresh(po)
    po_id = po.id

    log_action(
        session=session,
        username=actor.username,
        role=actor.role,
        action="CREATE_PURCHASE_ORDER",
        details=f"创建采购单: {po_no}, 供应商: {supplier_name}, 预估总价: ${total_amount_usd:.2f}",
    )

    return {"status": "success", "po_id": po_id, "po_no": po_no, "message": "采购订单创建成功（待收货入库）"}


@router.put("/api/purchase-orders/{po_id}/cancel")
def cancel_purchase_order(
    po_id: int,
    session: Session = Depends(get_session),
    actor: Actor = Depends(RequirePermission("procurement:view"))
):
    po = session.get(PurchaseOrder, po_id)
    if not po:
        raise HTTPException(status_code=404, detail="采购单不存在")
    if po.status != "PENDING":
        raise HTTPException(status_code=400, detail="只有待收货的订单才能作废")
    
    po.status = "CANCELLED"
    session.add(po)
    session.commit()
    
    log_action(session, actor.username, actor.role, "CANCEL_PURCHASE_ORDER", f"作废采购单: {po.po_no}")
    return {"status": "success", "message": "采购单已作废"}


@router.post("/api/purchase-orders/{po_id}/receive")
def receive_purchase_order(
    po_id: int, 
    actor: Actor = Depends(RequirePermission("procurement:view")),
    session: Session = Depends(get_session)
):
    try:
        claimed = session.exec(
            update(PurchaseOrder)
            .where(PurchaseOrder.id == po_id, PurchaseOrder.status == "PENDING")
            .values(status="RECEIVING")
        )
        if claimed.rowcount == 0:
            po_check = session.get(PurchaseOrder, po_id)
            if not po_check:
                raise HTTPException(status_code=404, detail="采购订单不存在")
            raise HTTPException(status_code=400, detail="该采购订单已经被收货或正在处理中，请勿重复操作")

        po = session.get(PurchaseOrder, po_id)

        try:
            items_data = json.loads(po.items_json) if po.items_json else []
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"解析采购单明细失败: {e}")

        supplier = session.get(Supplier, po.supplier_id)
        total_order_amount_cents = 0

        for item_dict in items_data:
            oem = (item_dict.get("oem") or "").strip()
            name = (item_dict.get("name") or "").strip() or oem
            if not oem:
                raise HTTPException(status_code=400, detail=f"采购单 {po.po_no} 存在缺少 OEM 的明细")

            try:
                d_qty = Decimal(str(item_dict.get("quantity")))
                d_price = Decimal(str(item_dict.get("unit_price")))
            except (ArithmeticError, TypeError, ValueError):
                raise HTTPException(status_code=400, detail=f"采购单明细数值非法（OEM={oem}）")

            if d_qty <= 0 or d_qty != d_qty.to_integral_value():
                raise HTTPException(status_code=400, detail=f"明细数量必须为正整数（OEM={oem}）")
            if d_price <= 0:
                raise HTTPException(status_code=400, detail=f"明细单价必须大于 0（OEM={oem}）")

            quantity = int(d_qty)
            unit_price = float(d_price)
            line_total = (d_price * d_qty).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            total_order_amount_cents += int(line_total * 100)

            # 查找已有商品
            part = session.exec(
                select(AutoPart).where(AutoPart.oem == oem, AutoPart.brand == (item_dict.get("brand") or "GENERAL"))
            ).first()

            if part:
                # 🌟 加权平均成本（原子更新，防止并发丢失）
                stock_expr = func.coalesce(AutoPart.stock, 0)
                new_cost_expr = func.round(
                    (
                        stock_expr * func.coalesce(AutoPart.cost_price, 0.0)
                        + quantity * unit_price
                    ) * 1.0 / (stock_expr + quantity),
                    4,
                )
                changed = session.exec(
                    update(AutoPart)
                    .where(
                        AutoPart.id == part.id,
                        func.coalesce(AutoPart.stock, 0) + quantity > 0,
                    )
                    .values(
                        stock=AutoPart.stock + quantity,
                        cost_price=new_cost_expr,
                    )
                    .execution_options(synchronize_session=False)
                )
                if changed.rowcount != 1:
                    raise HTTPException(status_code=409, detail=f"商品 {oem} 库存状态异常，请重试")
            else:
                # 🚫 新商品不直接用进价当售价，置 0 强制后台定价，避免毛利为 0
                session.add(AutoPart(
                    name=name,
                    oem=oem,
                    brand=item_dict.get("brand") or "GENERAL",
                    stock=quantity,
                    price=0.0,
                    cost_price=unit_price,
                    category="未分类（待定价）",
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

        total_order_amount = Decimal(total_order_amount_cents) / Decimal("100")
        if supplier:
            session.exec(
                update(Supplier)
                .where(Supplier.id == supplier.id)
                .values(debt_usd=func.round(
                    func.coalesce(Supplier.debt_usd, 0.0) + float(total_order_amount), 2
                ))
            )

        po.status = "received"
        session.add(po)
        session.commit()

        log_action(
            session=session,
            username=actor.username,
            role=actor.role,
            action="RECEIVE_PURCHASE_ORDER",
            details=f"采购收货完成: {po.po_no}, 供应商: {supplier.name if supplier else '未知'}, 总金额: ${total_order_amount:.2f}",
        )

        return {
            "status": "success",
            "po_id": po_id,
            "message": "收货成功：库存已增加、流水已记录、供应商应付账款已累加！",
        }

    except HTTPException:
        session.rollback()
        raise
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail="商品档案冲突（OEM + 品牌已存在），请刷新后重试")
    except Exception as e:
        session.rollback()
        print(f"❌ 采购收货发生严重异常，已执行事务回滚。错误详情: {e}")
        raise HTTPException(status_code=500, detail=f"收货处理失败，已安全回滚: {str(e)}")


@router.get("/api/purchase-orders")
def get_purchase_orders(
    session: Session = Depends(get_session),
    actor: Actor = Depends(RequirePermission("procurement:view"))
):
    return session.exec(select(PurchaseOrder).order_by(PurchaseOrder.id.desc())).all()