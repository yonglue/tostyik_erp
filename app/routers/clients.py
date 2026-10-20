"""客户档案：列表 / 新增 / 还款 / 未结清订单查询。"""

from decimal import Decimal, ROUND_HALF_UP
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlmodel import Session, select, update
import re # 🌟 引入正则用于校验电话

from app.database import get_session
from app.deps import Actor, get_current_actor, RequirePermission 
from app.models import Client, ClientPaymentRecord, InventoryTransaction
from app.schemas import ClientPaymentPayload
from app.services.audit import log_action
from app.services.bcv import get_official_rate

router = APIRouter(tags=["客户"])


@router.get("/api/clients", response_model=list[Client])
def get_clients(
    session: Session = Depends(get_session),
    actor: Actor = Depends(RequirePermission("clients:view"))
):
    return session.exec(select(Client).order_by(Client.id.desc())).all()


@router.post("/api/clients", response_model=Client)
def create_client(
    client: Client,
    actor: Actor = Depends(RequirePermission("clients:manage")),
    session: Session = Depends(get_session),
):
    # 🌟 后端兜底校验：手机号如果存在，必须符合委内瑞拉格式 (+58 + 10位数字)
    if client.phone and client.phone != "":
        if not re.match(r"^\+58\d{10}$", client.phone):
            raise HTTPException(status_code=400, detail="电话号码格式错误，需为 +58 加 10 位数字")
    
    # 🌟 后端兜底校验：RIF/身份证格式 (字母 + 8~9 位数字)
    if client.rif_or_cedula and client.rif_or_cedula != "":
        if not re.match(r"^[VEJG]-\d{8,9}$", client.rif_or_cedula):
            raise HTTPException(status_code=400, detail="RIF/身份证格式错误，需形如 J-12345678")

    session.add(client)
    session.commit()
    session.refresh(client)

    log_action(
        session=session,
        username=actor.username,
        role=actor.role,
        action="CREATE_CLIENT",
        details=f"新增客户: {client.name} (RIF: {client.rif_or_cedula}, 特殊纳税人: {client.is_special_taxpayer})",
    )

    return client


@router.post("/api/clients/repay")
def client_repayment(
    payload: ClientPaymentPayload,
    actor: Actor = Depends(RequirePermission("fiado:pay")),
    session: Session = Depends(get_session),
):
    client = session.exec(select(Client).where(Client.name == payload.client_name)).first()
    if not client:
        raise HTTPException(status_code=404, detail="客户档案不存在")

    bcv_rate = get_official_rate()
    if not bcv_rate:
        bcv_rate = Decimal("1.0")

    curr = payload.currency.upper()
    
    d_amount_paid = Decimal(str(payload.amount_paid))
    d_bcv_rate = Decimal(str(bcv_rate))
    
    if curr in ["BS", "VES", "PAGO_MOVIL", "TRANSFER_BS"]:
        amount_usd_eq = (d_amount_paid / d_bcv_rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    else:
        amount_usd_eq = d_amount_paid.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    updated = session.exec(
        update(Client)
        .where(Client.id == client.id)
        .values(debt=Client.debt - float(amount_usd_eq))
    )
    if updated.rowcount != 1:
        session.rollback()
        raise HTTPException(status_code=404, detail="客户档案不存在")

    payment_record = ClientPaymentRecord(
        client_name=client.name,
        amount_usd=float(amount_usd_eq),
        payment_method=payload.payment_method,
        reference_no=payload.reference_no,
        notes=f"[{curr} 原币: {payload.amount_paid} | 汇率: {bcv_rate}] {payload.notes or ''}",
    )
    session.add(payment_record)

    # 先提交业务，再写审计；审计失败时 log_action 会 rollback，
    # 不能让它把尚未提交的还款一起回滚。
    session.commit()
    session.refresh(client)
    remaining_debt = client.debt

    log_action(
        session=session, username=actor.username, role=actor.role,
        action="CLIENT_REPAYMENT",
        details=(f"客户 {client.name} 还款: {payload.amount_paid} {curr} (折合 ${amount_usd_eq:.2f} USD)"),
    )
    
    return {
        "status": "success",
        "amount_usd_equivalent": float(amount_usd_eq),
        "remaining_debt": remaining_debt,
        "bcv_rate": float(bcv_rate),
    }


@router.get("/api/clients/{client_name}/unpaid-orders")
def get_client_unpaid_orders(
    client_name: str, 
    session: Session = Depends(get_session),
    actor: Actor = Depends(RequirePermission("clients:view"))
):
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


@router.delete("/api/clients/{client_id}")
def delete_client(
    client_id: int,
    actor: Actor = Depends(RequirePermission("clients:manage")),
    session: Session = Depends(get_session),
):
    client = session.get(Client, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="客户档案不存在")
    
    client_name = client.name
    session.delete(client)
    session.commit()

    log_action(
        session=session,
        username=actor.username,
        role=actor.role,
        action="DELETE_CLIENT",
        details=f"删除了客户档案: {client_name} (ID: {client_id})",
    )

    return {"status": "success", "message": f"客户 {client_name} 已成功删除"}