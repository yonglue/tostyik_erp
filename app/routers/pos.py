"""POS 收银：下单（扣库存 + 落订单）/ 历史订单 / 退货回滚 / 云端挂单。"""

from datetime import datetime, time
from typing import Optional
from decimal import Decimal, ROUND_HALF_UP # 🌟 引入 Decimal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlmodel import Session, select, update

from app.database import get_session
from app.deps import Actor, RequirePermission
from app.models import AutoPart, Client, InventoryTransaction, Order, OrderItem, HeldOrder, CashRegisterSession
from app.schemas import POSOrderCreatePayload
from app.services.numbering import make_order_no
from app.services.audit import log_action
import json

router = APIRouter(tags=["POS 收银"])

_DEBT_KEYWORDS = ("Fiado", "Debt", "挂账")


def _is_debt_payment(payment_method: str) -> bool:
    return any(k in payment_method for k in _DEBT_KEYWORDS)

# 🌟 辅助函数：将 Decimal 四舍五入保留 2 位小数
def _money(value) -> Decimal:
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


@router.post("/api/pos/orders")
def create_pos_order(
    payload: POSOrderCreatePayload,
    actor: Actor = Depends(RequirePermission("pos:access")),
    session: Session = Depends(get_session),
):
    client_name = payload.client_name.strip() if payload.client_name else "Cliente General"

    merged_items_map = {}
    for item in payload.items:
        if item.oem in merged_items_map:
            merged_items_map[item.oem].quantity += item.quantity
        else:
            merged_items_map[item.oem] = type(item)(
                oem=item.oem,
                name=item.name,
                price=item.price,
                quantity=item.quantity
            )
    deduped_items = list(merged_items_map.values())

    # 🌟 使用 Decimal 初始化累加器
    total_base_amount = Decimal("0.00")
    total_tax_amount = Decimal("0.00")
    order_items_to_create = []

    for item in deduped_items:
        if item.quantity <= 0:
            raise HTTPException(status_code=400, detail=f"商品 {item.oem} 数量必须大于 0")

        part = session.exec(select(AutoPart).where(AutoPart.oem == item.oem)).first()
        if not part:
            raise HTTPException(status_code=404, detail=f"商品 {item.oem} 不存在")

        result = session.exec(
            update(AutoPart)
            .where(AutoPart.oem == item.oem, AutoPart.stock >= item.quantity)
            .values(stock=AutoPart.stock - item.quantity)
        )
        if result.rowcount == 0:
            session.rollback()
            raise HTTPException(status_code=400, detail=f"商品 {part.name} 库存不足（当前库存: {part.stock}）")

        # 🌟 使用 Decimal 计算
        d_price = Decimal(str(item.price))
        d_quantity = Decimal(str(item.quantity))
        line_total = _money(d_price * d_quantity)

        session.add(InventoryTransaction(
            part_oem=item.oem,
            part_name=item.name,
            type="OUT",
            quantity=item.quantity,
            unit_price=float(d_price), # 🌟 数据库模型还是 float，入库前转回 float 防止报错
            total_amount=float(line_total),
            customer_or_supplier=client_name,
        ))

        item_tax_rate = Decimal(str(getattr(part, "tax_rate", 0.16)))
        
        # 🌟 严格按照 SENIAT 法规分离 Base Imponible 与 IVA (Decimal 版)
        if item_tax_rate > 0:
            base_sub = _money(line_total / (Decimal("1.0") + item_tax_rate))
            tax_sub = _money(line_total - base_sub)
        else:
            base_sub = line_total
            tax_sub = Decimal("0.00")

        total_base_amount += base_sub
        total_tax_amount += tax_sub

        order_items_to_create.append({
            "oem": item.oem,
            "name": item.name,
            "quantity": item.quantity,
            "price_usd": float(d_price),
            "subtotal_usd": float(line_total),
            "tax_rate": float(item_tax_rate),
            "base_subtotal_usd": float(base_sub),
            "tax_subtotal_usd": float(tax_sub),
        })

    goods_total_usd = _money(total_base_amount + total_tax_amount)

    # 🌟 核心修复：不再硬编码 3%，直接使用前端传来的 IGTF 金额
    igtf_amount = _money(payload.igtf_amount)
    total_usd = _money(goods_total_usd + igtf_amount)
    
    # 🌟 Decimal 计算汇率转换
    d_bcv_rate = Decimal(str(payload.bcv_rate))
    total_bs = _money(total_usd * d_bcv_rate)
    
    order_no = make_order_no()

    new_order = Order(
        order_no=order_no,
        client_name=client_name,
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
    session.flush()

    for oi in order_items_to_create:
        session.add(OrderItem(
            order_id=new_order.id,
            oem=oi["oem"],
            name=oi["name"],
            quantity=oi["quantity"],
            price_usd=oi["price_usd"],
            subtotal_usd=oi["subtotal_usd"],
            tax_rate=oi["tax_rate"],
            base_subtotal_usd=oi["base_subtotal_usd"],
            tax_subtotal_usd=oi["tax_subtotal_usd"],
        ))

    if _is_debt_payment(payload.payment_method):
        # 🌟 债务更新也使用 Decimal
        session.exec(
            update(Client)
            .where(Client.name == client_name)
            .values(debt=Client.debt + float(total_usd))
        )

    session.commit()
    log_action(session, actor.username, actor.role, "POS_ORDER", f"POS开单完成, 单号: {order_no}, Base: ${total_base_amount:.2f}, IVA: ${total_tax_amount:.2f}, IGTF: ${igtf_amount:.2f}, 总计: ${total_usd:.2f}")

    return {"status": "success", "order_no": order_no, "order_id": new_order.id}


# 🌟 下面的函数（get_pos_orders, refund_pos_order 等）逻辑不用大变，保持原样即可。
# 为了方便你复制，我已经把后面的代码完整贴出来了（仅做了轻微格式调整）。

@router.get("/api/pos/orders")
def get_pos_orders(
    date: Optional[str] = Query(None, description="可选筛选日期，格式 YYYY-MM-DD"),
    session: Session = Depends(get_session),
    actor: Actor = Depends(RequirePermission("pos:access"))
):
    orders = session.exec(select(Order).order_by(Order.id.desc())).all()

    result = []
    for o in orders:
        items_list = [{
            "oem": i.oem,
            "name": i.name,
            "quantity": i.quantity,
            "price": i.price_usd,
        } for i in o.items]

        time_str = o.created_at.strftime("%Y-%m-%d %H:%M:%S") if o.created_at else ""

        result.append({
            "orderId": o.order_no,
            "dbId": o.id,
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
    actor: Actor = Depends(RequirePermission("transactions:history")),
    session: Session = Depends(get_session),
):
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")

    claimed = session.exec(
        update(Order)
        .where(Order.id == order_id, Order.status != "REFUNDED")
        .values(status="REFUNDED")
    )
    if claimed.rowcount == 0:
        session.rollback()
        raise HTTPException(status_code=400, detail="该订单已经退货，请勿重复操作")

    for item in order.items:
        session.exec(
            update(AutoPart)
            .where(AutoPart.oem == item.oem)
            .values(stock=AutoPart.stock + item.quantity)
        )

        session.add(InventoryTransaction(
            part_oem=item.oem,
            part_name=item.name,
            type="IN",
            quantity=item.quantity,
            unit_price=item.price_usd,
            total_amount=item.subtotal_usd,
            customer_or_supplier=f"退货回滚-{order.client_name}",
        ))

    if _is_debt_payment(order.payment_method):
        session.exec(
            update(Client)
            .where(Client.name == order.client_name)
            # 🌟 修复：去掉 func.max，允许产生负数（余额），财务上这叫做“客户预存款”或“应收负数”
            .values(debt=Client.debt - order.total_usd) 
        )

    session.commit()

    log_action(session, actor.username, actor.role, "POS_REFUND", f"执行POS退货, 单号: {order.order_no}")
    return {"status": "success", "message": f"订单 {order.order_no} 已成功退货并回滚库存！"}


@router.get("/api/held-orders")
def get_held_orders(
    session: Session = Depends(get_session),
    actor: Actor = Depends(RequirePermission("pos:access"))
):
    return session.exec(select(HeldOrder).order_by(HeldOrder.id.desc())).all()


@router.post("/api/held-orders")
def create_held_order(
    payload: dict,
    session: Session = Depends(get_session),
    actor: Actor = Depends(RequirePermission("pos:access"))
):
    hold_no = f"HOLD-{int(datetime.now().timestamp())}"
    held = HeldOrder(
        hold_no=hold_no,
        client_name=payload.get("client_name", "Cliente General"),
        payment_method=payload.get("payment_method", "Cash_USD"),
        items_json=json.dumps(payload.get("items", [])),
        total_amount=float(payload.get("total_amount", 0.0)),
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    session.add(held)
    session.commit()
    session.refresh(held)
    return {"status": "success", "held_order": held}


@router.delete("/api/held-orders/{order_id}")
def delete_held_order(
    order_id: int,
    session: Session = Depends(get_session),
    actor: Actor = Depends(RequirePermission("pos:access"))
):
    held = session.get(HeldOrder, order_id)
    if not held:
        raise HTTPException(status_code=404, detail="挂单记录不存在")
    session.delete(held)
    session.commit()
    return {"status": "success", "message": "挂单已成功清除"}


@router.post("/api/pos/shift-handover")
def create_shift_handover(
    payload: dict,
    session: Session = Depends(get_session),
    actor: Actor = Depends(RequirePermission("pos:access"))
):
    try:
        actual_cash = float(payload.get("actual_cash_usd", 0.0))
        system_cash = float(payload.get("system_cash_usd", 0.0))

        session_record = CashRegisterSession(
            closed_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            operator=actor.username if actor and hasattr(actor, "username") else "admin",
            bcv_rate_snapshot=float(payload.get("bcv_rate", 0.0)),
            total_base_amount_usd=float(payload.get("system_base_amount_usd", 0.0)),
            total_iva_amount_usd=float(payload.get("system_tax_amount_usd", 0.0)),
            total_igtf_amount_usd=float(payload.get("system_igtf_amount_usd", 0.0)),
            system_cash_usd=system_cash,
            system_zelle=float(payload.get("system_zelle_usd", 0.0)),
            system_pago_movil=float(payload.get("system_pagomovil_usd", 0.0)),
            system_transfer_bs=float(payload.get("system_transfer_bs", 0.0)),
            system_usdt=float(payload.get("system_usdt_usd", 0.0)),
            actual_cash_usd=actual_cash,
            actual_zelle=float(payload.get("system_zelle_usd", 0.0)),
            actual_pago_movil=float(payload.get("system_pagomovil_usd", 0.0)),
            actual_transfer_bs=float(payload.get("system_transfer_bs", 0.0)),
            actual_usdt=float(payload.get("system_usdt_usd", 0.0)),
            total_revenue_usd=float(payload.get("system_total_usd", 0.0)),
            notes=str(payload.get("notes", ""))
        )
        session.add(session_record)
        session.commit()
        session.refresh(session_record)

        try:
            log_action(
                session,
                actor.username if actor and hasattr(actor, "username") else "admin",
                actor.role if actor and hasattr(actor, "role") else "staff",
                "SHIFT_HANDOVER",
                f"完成收银交接班归档, 实盘现金: ${actual_cash:.2f}, 总计营业额: ${float(payload.get('system_total_usd', 0.0)):.2f}"
            )
        except Exception as log_err:
            print(f"⚠️ 审计日志写入跳过: {log_err}")

        return {"status": "success", "message": "交接班归档成功"}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")


@router.get("/api/pos/shift-records")
def get_shift_records(
    session: Session = Depends(get_session),
    actor: Actor = Depends(RequirePermission("pos:access"))
):
    records = session.exec(select(CashRegisterSession).order_by(CashRegisterSession.id.desc())).all()
    return records