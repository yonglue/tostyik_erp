"""POS 收银：下单（扣库存 + 落订单）/ 历史订单 / 退货回滚 / 云端挂单。"""

from datetime import datetime, timedelta
from typing import Optional
from decimal import Decimal, ROUND_HALF_UP

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select, update

from app.database import get_session
from app.deps import Actor, RequirePermission
from app.models import (
    AutoPart,
    CashRegisterSession,
    Client,
    HeldOrder,
    InventoryTransaction,
    Order,
    OrderItem,
    _VENEZUELA_TZ,
)
from app.schemas import HeldOrderCreatePayload, POSOrderCreatePayload, ShiftHandoverPayload
from app.services.numbering import make_order_no
from app.services.audit import log_action
import json

router = APIRouter(tags=["POS 收银"])

_DEBT_KEYWORDS = ("Fiado", "Debt", "挂账")


def _is_debt_payment(payment_method: str) -> bool:
    return any(k in payment_method for k in _DEBT_KEYWORDS)

def _money(value) -> Decimal:
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _resolve_part(session: Session, oem: str, brand: Optional[str]) -> AutoPart:
    matches = session.exec(select(AutoPart).where(AutoPart.oem == oem)).all()
    if not matches:
        raise HTTPException(status_code=404, detail=f"商品 {oem} 不存在")
    if len(matches) > 1:
        wanted = (brand or "").strip()
        matches = [p for p in matches if p.brand == wanted]
        if len(matches) != 1:
            raise HTTPException(
                status_code=400,
                detail=f"OEM {oem} 存在多个品牌，请在明细中指定正确的 brand",
            )
    return matches[0]


def _idempotent_response(session: Session, request_id: Optional[str]):
    if not request_id:
        return None
    existing = session.exec(
        select(Order).where(Order.request_id == request_id)
    ).first()
    if not existing:
        return None
    return {
        "status": "success",
        "order_no": existing.order_no,
        "order_id": existing.id,
        "idempotent": True,
    }


@router.post("/api/pos/orders")
def create_pos_order(
    payload: POSOrderCreatePayload,
    actor: Actor = Depends(RequirePermission("pos:checkout")),
    session: Session = Depends(get_session),
):
    request_id = (payload.request_id or "").strip() or None
    cached = _idempotent_response(session, request_id)
    if cached is not None:
        return cached

    client_name = payload.client_name.strip() if payload.client_name else "Cliente General"

    client = None
    if payload.client_id is not None:
        client = session.get(Client, payload.client_id)
        if not client:
            raise HTTPException(status_code=404, detail="客户档案不存在")
        client_name = client.name
    else:
        matches = session.exec(select(Client).where(Client.name == client_name)).all()
        if len(matches) == 1:
            client = matches[0]
        elif len(matches) > 1 and _is_debt_payment(payload.payment_method):
            raise HTTPException(
                status_code=400,
                detail=f"存在多个同名客户 {client_name}，挂账请改用 client_id 指定",
            )

    merged_items_map = {}
    for item in payload.items:
        merge_key = (
            item.oem,
            (item.brand or "GENERAL").strip(),
            str(_money(item.price)),
        )
        if merge_key in merged_items_map:
            merged_items_map[merge_key].quantity += item.quantity
        else:
            merged_items_map[merge_key] = type(item)(
                oem=item.oem,
                name=item.name,
                brand=merge_key[1],
                price=item.price,
                quantity=item.quantity
            )
    deduped_items = list(merged_items_map.values())

    if not deduped_items:
        raise HTTPException(status_code=400, detail="订单不能为空")

    total_base_amount = Decimal("0.00")
    total_tax_amount = Decimal("0.00")
    order_items_to_create = []

    for item in deduped_items:
        if item.quantity <= 0:
            raise HTTPException(status_code=400, detail=f"商品 {item.oem} 数量必须大于 0")

        part = _resolve_part(session, item.oem, item.brand)
        part_id = part.id
        part_name = part.name
        

        # 🌟 新增：从数据库获取真实进价
        part_cost_price = Decimal(str(getattr(part, "cost_price", 0.0)))

        result = session.exec(
            update(AutoPart)
            .where(AutoPart.id == part_id, AutoPart.stock >= item.quantity)
            .values(stock=AutoPart.stock - item.quantity)
        )
        if result.rowcount != 1:
            session.rollback()
            current = session.get(AutoPart, part_id)
            available = current.stock if current else 0
            raise HTTPException(status_code=400, detail=f"商品 {part_name} 库存不足（当前库存: {available}）")

        d_price = Decimal(str(item.price))
        if d_price <= 0:
            session.rollback()
            raise HTTPException(status_code=400, detail=f"商品 {item.oem} 单价必须大于 0")
        d_quantity = Decimal(str(item.quantity))
        line_total = _money(d_price * d_quantity)

        session.add(InventoryTransaction(
            part_oem=item.oem,
            part_name=item.name,
            type="OUT",
            quantity=item.quantity,
            unit_price=float(d_price),
            total_amount=float(line_total),
            customer_or_supplier=client_name,
        ))

        item_tax_rate = Decimal(str(getattr(part, "tax_rate", 0.16)))
        
        if item_tax_rate > 0:
            base_sub = _money(line_total / (Decimal("1.0") + item_tax_rate))
            tax_sub = _money(line_total - base_sub)
        else:
            base_sub = line_total
            tax_sub = Decimal("0.00")

        total_base_amount += base_sub
        total_tax_amount += tax_sub

        order_items_to_create.append({
            "part_id": part_id,
            "oem": item.oem,
            "name": item.name,
            "quantity": item.quantity,
            "price_usd": float(d_price),
            "subtotal_usd": float(line_total),
            "cost_price_usd": float(part_cost_price), # 🌟 新增：把进价带上
            "tax_rate": float(item_tax_rate),
            "base_subtotal_usd": float(base_sub),
            "tax_subtotal_usd": float(tax_sub),
        })

    goods_total_usd = _money(total_base_amount + total_tax_amount)

    igtf_amount = _money(payload.igtf_amount)
    if igtf_amount < 0:
        session.rollback()
        raise HTTPException(status_code=400, detail="IGTF 金额不能为负数")
    max_igtf = _money(goods_total_usd * Decimal("0.03")) + Decimal("0.01")
    if igtf_amount > max_igtf:
        session.rollback()
        raise HTTPException(status_code=400, detail=f"IGTF 金额超出上限（最多 ${max_igtf:.2f}）")

    total_usd = _money(goods_total_usd + igtf_amount)

    if _is_debt_payment(payload.payment_method):
        if client is None:
            session.rollback()
            raise HTTPException(
                status_code=400,
                detail=f"挂账客户不存在: {client_name}，请先在客户档案中建档",
            )
        projected_debt = _money(Decimal(str(client.debt)) + total_usd)
        credit_limit = _money(client.credit_limit)
        if projected_debt > credit_limit:
            session.rollback()
            raise HTTPException(
                status_code=400,
                detail=(
                    f"超出客户信用额度：当前欠款 ${_money(client.debt):.2f}，"
                    f"本次 ${total_usd:.2f}，上限 ${credit_limit:.2f}"
                ),
            )
    
    d_bcv_rate = Decimal(str(payload.bcv_rate))
    if d_bcv_rate <= 0:
        session.rollback()
        raise HTTPException(status_code=400, detail="汇率必须大于 0")
    total_bs = _money(total_usd * d_bcv_rate)
    
    order_no = make_order_no()

    new_order = Order(
        order_no=order_no,
        client_name=client_name,
        client_id=client.id if client else None,
        request_id=request_id,
        operator=actor.username,
        base_amount_usd=float(total_base_amount),
        tax_amount_usd=float(total_tax_amount),
        igtf_amount_usd=float(igtf_amount),
        total_usd=float(total_usd),
        total_bs=float(total_bs),
        bcv_rate=float(d_bcv_rate),
        payment_method=payload.payment_method,
        payment_reference=payload.payment_reference,
        status="COMPLETED",
    )
    session.add(new_order)
    try:
        session.flush()
    except IntegrityError:
        session.rollback()
        cached = _idempotent_response(session, request_id)
        if cached is not None:
            return cached
        raise HTTPException(status_code=409, detail="订单创建冲突，请重试")

    for oi in order_items_to_create:
        session.add(OrderItem(
            order_id=new_order.id,
            part_id=oi["part_id"],
            oem=oi["oem"],
            name=oi["name"],
            quantity=oi["quantity"],
            price_usd=oi["price_usd"],
            subtotal_usd=oi["subtotal_usd"],
            cost_price_usd=oi["cost_price_usd"], # 🌟 新增：把进价写入数据库
            tax_rate=oi["tax_rate"],
            base_subtotal_usd=oi["base_subtotal_usd"],
            tax_subtotal_usd=oi["tax_subtotal_usd"],
        ))

    if _is_debt_payment(payload.payment_method):
        debt_updated = session.exec(
            update(Client)
            .where(
                Client.id == client.id,
                Client.debt + float(total_usd) <= Client.credit_limit,
            )
            .values(debt=Client.debt + float(total_usd))
        )
        if debt_updated.rowcount != 1:
            session.rollback()
            raise HTTPException(
                status_code=400,
                detail="超出客户信用额度或客户档案已变更，请刷新后重试",
            )

    order_id = new_order.id
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        cached = _idempotent_response(session, request_id)
        if cached is not None:
            return cached
        raise HTTPException(status_code=409, detail="订单保存冲突，请重试")

    log_action(session, actor.username, actor.role, "POS_ORDER", f"POS开单完成, 单号: {order_no}, Base: ${total_base_amount:.2f}, IVA: ${total_tax_amount:.2f}, IGTF: ${igtf_amount:.2f}, 总计: ${total_usd:.2f}")

    return {"status": "success", "order_no": order_no, "order_id": order_id}


@router.get("/api/pos/orders")
def get_pos_orders(
    date: Optional[str] = Query(None, description="可选筛选日期，格式 YYYY-MM-DD"),
    session: Session = Depends(get_session),
    actor: Actor = Depends(RequirePermission("pos:access"))
):
    stmt = (
        select(Order)
        .options(selectinload(Order.items))
        .order_by(Order.id.desc())
        .limit(200)
    )
    if date:
        try:
            start = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="日期格式必须为 YYYY-MM-DD")
        stmt = stmt.where(
            Order.created_at >= start,
            Order.created_at < start + timedelta(days=1),
        )

    orders = session.exec(stmt).all()

    result = []
    for o in orders:
        items_list = [{
            "oem": i.oem,
            "name": i.name,
            "quantity": i.quantity,
            "price": i.price_usd,
            "cost_price": i.cost_price_usd, # 🌟 新增：把进价返回给前端
        } for i in o.items]

        time_str = o.created_at.strftime("%Y-%m-%d %H:%M:%S") if o.created_at else ""

        result.append({
            "orderId": o.order_no,
            "dbId": o.id,
            "clientId": o.client_id,
            "clientName": o.client_name,
            "baseAmountUsd": o.base_amount_usd,
            "taxAmountUsd": o.tax_amount_usd,
            "igtfAmountUsd": o.igtf_amount_usd,
            "totalUsd": o.total_usd,
            "paymentMethod": o.payment_method,
            "paymentReference": o.payment_reference,
            "bcvRate": o.bcv_rate,
            "status": o.status,
            "time": time_str,
            "created_at": time_str,
            "items": items_list,
        })
    return result


@router.post("/api/pos/orders/{order_id}/refund")
def refund_pos_order(
    order_id: int,
    actor: Actor = Depends(RequirePermission("pos:refund")),
    session: Session = Depends(get_session),
):
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    order_no = order.order_no

    claimed = session.exec(
        update(Order)
        .where(Order.id == order_id, Order.status != "REFUNDED")
        .values(status="REFUNDED")
    )
    if claimed.rowcount == 0:
        session.rollback()
        raise HTTPException(status_code=400, detail="该订单已经退货，请勿重复操作")

    for item in order.items:
        part = session.get(AutoPart, item.part_id) if item.part_id else None
        if part is not None and part.oem != item.oem:
            part = None
        if part is None:
            candidates = session.exec(select(AutoPart).where(AutoPart.oem == item.oem)).all()
            if len(candidates) != 1:
                session.rollback()
                raise HTTPException(
                    status_code=409,
                    detail=f"订单明细 {item.oem} 无法唯一定位商品，退货中止",
                )
            part = candidates[0]

        restored = session.exec(
            update(AutoPart)
            .where(AutoPart.id == part.id)
            .values(stock=AutoPart.stock + item.quantity)
        )
        if restored.rowcount != 1:
            session.rollback()
            raise HTTPException(status_code=409, detail=f"商品 {item.oem} 已不存在，退货中止")

        session.add(InventoryTransaction(
            part_oem=part.oem,
            part_name=item.name,
            type="REFUND",
            quantity=item.quantity,
            unit_price=item.price_usd,
            total_amount=item.subtotal_usd,
            customer_or_supplier=f"退货回滚-{order.client_name}",
        ))

    if _is_debt_payment(order.payment_method):
        if order.client_id is not None:
            client = session.get(Client, order.client_id)
            if client is None:
                session.rollback()
                raise HTTPException(
                    status_code=409,
                    detail="原挂账客户档案已删除，无法精确反减欠款，退货中止",
                )
        else:
            candidates = session.exec(
                select(Client).where(Client.name == order.client_name)
            ).all()
            if len(candidates) != 1:
                session.rollback()
                raise HTTPException(
                    status_code=409,
                    detail=f"无法唯一定位挂账客户 {order.client_name}，退货中止",
                )
            client = candidates[0]

        reversed_debt = session.exec(
            update(Client)
            .where(Client.id == client.id)
            .values(debt=Client.debt - order.total_usd)
        )
        if reversed_debt.rowcount != 1:
            session.rollback()
            raise HTTPException(status_code=409, detail="客户档案已不存在，退货中止")

    session.commit()

    log_action(session, actor.username, actor.role, "POS_REFUND", f"执行POS退货, 单号: {order_no}")
    return {"status": "success", "message": f"订单 {order_no} 已成功退货并回滚库存！"}


@router.get("/api/held-orders")
def get_held_orders(
    session: Session = Depends(get_session),
    actor: Actor = Depends(RequirePermission("pos:hold"))
):
    return session.exec(select(HeldOrder).order_by(HeldOrder.id.desc())).all()


@router.post("/api/held-orders")
def create_held_order(
    payload: HeldOrderCreatePayload,
    session: Session = Depends(get_session),
    actor: Actor = Depends(RequirePermission("pos:hold"))
):
    if not payload.items:
        raise HTTPException(status_code=400, detail="挂单不能为空")

    now = datetime.now(_VENEZUELA_TZ)
    items_payload = [
        {
            "oem": item.oem,
            "name": item.name,
            "brand": item.brand,
            "quantity": item.quantity,
            "price": float(item.price),
        }
        for item in payload.items
    ]
    total_amount = _money(
        sum(Decimal(str(item.price)) * item.quantity for item in payload.items)
    )

    held = HeldOrder(
        hold_no=f"HOLD-{now.strftime('%Y%m%d-%H%M%S%f')}",
        client_name=payload.client_name.strip() or "Cliente General",
        payment_method=payload.payment_method,
        items_json=json.dumps(items_payload, ensure_ascii=False),
        total_amount=float(total_amount),
        timestamp=now.strftime("%Y-%m-%d %H:%M:%S"),
    )
    session.add(held)
    session.commit()
    session.refresh(held)
    return {"status": "success", "held_order": held}


@router.delete("/api/held-orders/{order_id}")
def delete_held_order(
    order_id: int,
    session: Session = Depends(get_session),
    actor: Actor = Depends(RequirePermission("pos:hold"))
):
    held = session.get(HeldOrder, order_id)
    if not held:
        raise HTTPException(status_code=404, detail="挂单记录不存在")
    session.delete(held)
    session.commit()
    return {"status": "success", "message": "挂单已成功清除"}


@router.post("/api/pos/shift-handover")
def create_shift_handover(
    payload: ShiftHandoverPayload,
    session: Session = Depends(get_session),
    actor: Actor = Depends(RequirePermission("shift:report"))
):
    session_record = CashRegisterSession(
        closed_at=datetime.now(_VENEZUELA_TZ).strftime("%Y-%m-%d %H:%M:%S"),
        operator=actor.username,
        bcv_rate_snapshot=float(payload.bcv_rate),
        total_base_amount_usd=float(payload.system_base_amount_usd),
        total_iva_amount_usd=float(payload.system_tax_amount_usd),
        total_igtf_amount_usd=float(payload.system_igtf_amount_usd),
        system_card_pos=float(payload.system_card_pos_bs),
        system_pago_movil=float(payload.system_pago_movil_bs),
        system_cash_bs=float(payload.system_cash_bs),
        system_cash_usd=float(payload.system_cash_usd),
        system_zelle=float(payload.system_zelle_usd),
        system_transfer_bs=float(payload.system_transfer_bs),
        system_usdt=float(payload.system_usdt_usd),
        actual_card_pos=float(payload.actual_card_pos_bs),
        actual_pago_movil=float(payload.actual_pago_movil_bs),
        actual_cash_bs=float(payload.actual_cash_bs),
        actual_cash_usd=float(payload.actual_cash_usd),
        actual_zelle=float(payload.actual_zelle_usd),
        actual_transfer_bs=float(payload.actual_transfer_bs),
        actual_usdt=float(payload.actual_usdt_usd),
        total_revenue_usd=float(payload.system_total_usd),
        notes=payload.notes,
    )
    session.add(session_record)
    session.commit()
    session.refresh(session_record)

    log_action(
        session,
        actor.username,
        actor.role,
        "SHIFT_HANDOVER",
        f"完成收银交接班归档, 实盘现金: ${float(payload.actual_cash_usd):.2f}, "
        f"总计营业额: ${float(payload.system_total_usd):.2f}",
    )

    return {"status": "success", "message": "交接班归档成功"}


@router.get("/api/pos/shift-records")
def get_shift_records(
    session: Session = Depends(get_session),
    actor: Actor = Depends(RequirePermission("shift:report"))
):
    records = session.exec(select(CashRegisterSession).order_by(CashRegisterSession.id.desc())).all()
    return records