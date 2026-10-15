"""POS 收银：下单（扣库存 + 落订单）/ 历史订单 / 退货回滚。"""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlmodel import Session, select, update

from app.database import get_session
from app.deps import Actor, get_current_actor
from app.models import AutoPart, Client, InventoryTransaction, Order, OrderItem
from app.schemas import POSOrderCreatePayload
from app.services.numbering import make_order_no
from app.services.audit import log_action

router = APIRouter(tags=["POS 收银"])

# 判定为挂账（赊销）的支付方式关键字
_DEBT_KEYWORDS = ("Fiado", "Debt", "挂账")


def _is_debt_payment(payment_method: str) -> bool:
    return any(k in payment_method for k in _DEBT_KEYWORDS)


@router.post("/api/pos/orders")
def create_pos_order(
    payload: POSOrderCreatePayload,
    actor: Actor = Depends(get_current_actor),
    session: Session = Depends(get_session),
):
    total_usd = sum(item.price * item.quantity for item in payload.items)
    total_bs = total_usd * payload.bcv_rate
    order_no = make_order_no()

    client_name = payload.client_name.strip() if payload.client_name else "Cliente General"

    # 校验并扣减库存，同时写入进销存流水
    for item in payload.items:
        if item.quantity <= 0:
            raise HTTPException(status_code=400, detail=f"商品 {item.oem} 数量必须大于 0")

        part = session.exec(select(AutoPart).where(AutoPart.oem == item.oem)).first()
        if not part:
            raise HTTPException(status_code=404, detail=f"商品 {item.oem} 不存在")

        # ⚠️ 同 quotations.py：SQLite 会静默忽略 with_for_update()，
        # 必须用原子条件更新来避免并发超卖。
        result = session.exec(
            update(AutoPart)
            .where(AutoPart.oem == item.oem, AutoPart.stock >= item.quantity)
            .values(stock=AutoPart.stock - item.quantity)
        )
        if result.rowcount == 0:
            session.rollback()
            raise HTTPException(status_code=400, detail=f"商品 {part.name} 库存不足（当前库存: {part.stock}）")

        session.add(InventoryTransaction(
            part_oem=item.oem,
            part_name=item.name,
            type="OUT",
            quantity=item.quantity,
            unit_price=item.price,
            total_amount=item.quantity * item.price,
            customer_or_supplier=client_name,
        ))

    # 持久化订单主表
    new_order = Order(
        order_no=order_no,
        client_name=client_name,
        operator=actor.username,
        total_usd=total_usd,
        total_bs=total_bs,
        bcv_rate=payload.bcv_rate,
        payment_method=payload.payment_method,
        payment_reference=payload.payment_reference,
        status="COMPLETED",
    )
    session.add(new_order)
    # 只 flush，不 commit：INSERT 在本事务内执行并回填主键，从而拿到 new_order.id，
    # 但库存扣减 / 流水 / 订单明细 / 客户欠款全部留在同一个事务里，
    # 由下面唯一一次 commit 原子落库。
    # （历史实现此处是 commit，导致第二次提交失败时会留下"有主表、无明细"的脏订单。）
    session.flush()

    # 写入订单明细表
    for item in payload.items:
        session.add(OrderItem(
            order_id=new_order.id,
            oem=item.oem,
            name=item.name,
            quantity=item.quantity,
            price_usd=item.price,
            subtotal_usd=item.price * item.quantity,
        ))

    # 挂账则同步累加客户欠款
    if _is_debt_payment(payload.payment_method):
        # SQL 级自增，避免同一客户并发挂账时丢失更新
        session.exec(
            update(Client)
            .where(Client.name == client_name)
            .values(debt=Client.debt + total_usd)
        )

    session.commit()
    log_action(session, actor.username, actor.role, "POS_ORDER", f"POS完成收银开单, 单号: {order_no}, 总额: ${total_usd:.2f}")

    return {"status": "success", "order_no": order_no, "order_id": new_order.id}


@router.get("/api/pos/orders")
def get_pos_orders(session: Session = Depends(get_session)):
    orders = session.exec(select(Order).order_by(Order.id.desc())).all()
    result = []
    for o in orders:
        items_list = [{
            "oem": i.oem,
            "name": i.name,
            "quantity": i.quantity,
            "price": i.price_usd,
        } for i in o.items]

        result.append({
            "orderId": o.order_no,
            "dbId": o.id,
            "clientName": o.client_name,
            "totalUsd": o.total_usd,
            "paymentMethod": o.payment_method,
            "paymentReference": o.payment_reference,
            "bcvRate": o.bcv_rate,
            "status": o.status,
            "time": o.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "items": items_list,
        })
    return result


@router.post("/api/pos/orders/{order_id}/refund")
def refund_pos_order(
    order_id: int,
    actor: Actor = Depends(get_current_actor),
    session: Session = Depends(get_session),
):
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")

    # 原子地抢占"退货权"：用带条件的 UPDATE 代替"先读 status 再判断"。
    # 并发发起多次退货时，只有第一个事务能把 status 从非 REFUNDED 改成 REFUNDED，
    # 其余的 rowcount 为 0 —— 否则会重复回滚库存（实测库存 7 -> 13）。
    claimed = session.exec(
        update(Order)
        .where(Order.id == order_id, Order.status != "REFUNDED")
        .values(status="REFUNDED")
    )
    if claimed.rowcount == 0:
        session.rollback()
        raise HTTPException(status_code=400, detail="该订单已经退货，请勿重复操作")

    # 回滚库存并写入退货流水
    for item in order.items:
        # 原子自增，避免与其它出入库并发时丢失更新
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

    # 挂账订单需扣减客户欠款
    if _is_debt_payment(order.payment_method):
        # SQL 级 max(0, debt - amount)：同一客户的多张挂账单被并发退货时不会丢失更新
        session.exec(
            update(Client)
            .where(Client.name == order.client_name)
            .values(debt=func.max(0.0, Client.debt - order.total_usd))
        )

    session.commit()

    log_action(session, actor.username, actor.role, "POS_REFUND", f"执行POS退货, 单号: {order.order_no}")
    return {"status": "success", "message": f"订单 {order.order_no} 已成功退货并回滚库存！"}
