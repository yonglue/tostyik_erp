"""客户档案：列表 / 新增 / 还款 / 未结清订单查询。"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlmodel import Session, select, update

from app.database import get_session
from app.deps import Actor, get_current_actor
from app.models import Client, ClientPaymentRecord, InventoryTransaction
from app.schemas import ClientPaymentPayload
from app.services.audit import log_action
from app.services.bcv import get_official_rate

router = APIRouter(tags=["客户"])


@router.get("/api/clients", response_model=list[Client])
def get_clients(session: Session = Depends(get_session)):
    return session.exec(select(Client).order_by(Client.id.desc())).all()


@router.post("/api/clients", response_model=Client)
def create_client(
    client: Client,
    actor: Actor = Depends(get_current_actor),
    session: Session = Depends(get_session),
):
    session.add(client)
    session.commit()
    session.refresh(client)

    log_action(
        session=session,
        username=actor.username,
        role=actor.role,
        action="CREATE_CLIENT",
        details=f"新增了客户档案: {client.name} (电话: {client.phone or '无'}, 信用额度: ${client.credit_limit})",
    )

    return {
        "id": client.id,
        "name": client.name,
        "phone": client.phone,
        "address": client.address,
        "rif_or_cedula": client.rif_or_cedula,
        "client_type": client.client_type,
        "debt": client.debt,
        "credit_limit": client.credit_limit,
        "notes": client.notes,
        "timestamp": client.timestamp,
    }


@router.post("/api/clients/repay")
def client_repayment(
    payload: ClientPaymentPayload,
    actor: Actor = Depends(get_current_actor),
    session: Session = Depends(get_session),
):
    client = session.exec(select(Client).where(Client.name == payload.client_name)).first()
    if not client:
        raise HTTPException(status_code=404, detail="客户档案不存在")

    bcv_rate = get_official_rate()

    curr = payload.currency.upper()
    if curr in ["BS", "VES", "PAGO_MOVIL", "TRANSFER_BS"]:
        amount_usd_eq = payload.amount_paid / bcv_rate
    else:
        amount_usd_eq = payload.amount_paid

    # 在 SQL 里做 max(0, debt - amount)，避免并发还款时丢失更新。
    # 注意不要在这里单独 commit：欠款扣减、还款流水、审计日志必须在同一事务内。
    session.exec(
        update(Client)
        .where(Client.id == client.id)
        .values(debt=func.max(0.0, Client.debt - amount_usd_eq))
    )

    payment_record = ClientPaymentRecord(
        client_name=client.name,
        amount_usd=amount_usd_eq,
        payment_method=payload.payment_method,
        reference_no=payload.reference_no,
        notes=f"[{curr} 原币: {payload.amount_paid} | 汇率: {bcv_rate}] {payload.notes or ''}",
    )
    session.add(payment_record)

    log_action(
        session=session, username=actor.username, role=actor.role,
        action="CLIENT_REPAYMENT",
        details=(
            f"客户 {client.name} 还款: {payload.amount_paid} {curr} "
            f"(折合 ${amount_usd_eq:.2f} USD)"
        ),
    )

    session.commit()
    # 提交后再读回最新欠款（前面用的是 SQL 级更新，ORM 里的值已过期）
    session.refresh(client)
    return {
        "status": "success",
        "amount_usd_equivalent": amount_usd_eq,
        "remaining_debt": client.debt,
        "bcv_rate": bcv_rate,
    }


@router.get("/api/clients/{client_name}/unpaid-orders")
def get_client_unpaid_orders(client_name: str, session: Session = Depends(get_session)):
    transactions = session.exec(
        select(InventoryTransaction)
        .where(InventoryTransaction.customer_or_supplier == client_name)
        .where(InventoryTransaction.type == "OUT")
        .order_by(InventoryTransaction.id.desc())
    ).all()

    payments = session.exec(
        select(ClientPaymentRecord)
        .where(ClientPaymentRecord.client_name == client_name)
        .order_by(ClientPaymentRecord.id.desc())
    ).all()

    return {"transactions": transactions, "payments": payments}
