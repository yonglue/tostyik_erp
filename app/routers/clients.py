"""客户档案：列表 / 新增 / 还款 / 未结清订单查询。"""

from decimal import Decimal, ROUND_HALF_UP
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlmodel import Session, select, update

from app.database import get_session
from app.deps import Actor, get_current_actor, RequirePermission # 🌟 引入权限
from app.models import Client, ClientPaymentRecord, InventoryTransaction
from app.schemas import ClientPaymentPayload
from app.services.audit import log_action
from app.services.bcv import get_official_rate

router = APIRouter(tags=["客户"])


# 🌟 加锁：必须拥有查看客户权限
@router.get("/api/clients", response_model=list[Client])
def get_clients(
    session: Session = Depends(get_session),
    actor: Actor = Depends(RequirePermission("clients:view"))
):
    return session.exec(select(Client).order_by(Client.id.desc())).all()


# 🌟 加锁：必须拥有管理客户权限
@router.post("/api/clients", response_model=Client)
def create_client(
    client: Client,
    actor: Actor = Depends(RequirePermission("clients:manage")),
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


# 🌟 加锁：必须拥有还款/核销权限
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
    
    # 🌟 核心修复 1：强制使用 Decimal 进行汇率换算
    d_amount_paid = Decimal(str(payload.amount_paid))
    d_bcv_rate = Decimal(str(bcv_rate))
    
    if curr in ["BS", "VES", "PAGO_MOVIL", "TRANSFER_BS"]:
        amount_usd_eq = (d_amount_paid / d_bcv_rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    else:
        amount_usd_eq = d_amount_paid.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    # 🌟 核心修复 2：去掉 func.max，允许债务变成负数（表示客户预存）
    session.exec(
        update(Client)
        .where(Client.id == client.id)
        .values(debt=Client.debt - float(amount_usd_eq))
    )

    payment_record = ClientPaymentRecord(
        client_name=client.name,
        amount_usd=float(amount_usd_eq),
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
    session.refresh(client)
    
    return {
        "status": "success",
        "amount_usd_equivalent": float(amount_usd_eq),
        "remaining_debt": client.debt,
        "bcv_rate": float(bcv_rate),
    }


# 🌟 加锁：必须拥有查看客户权限
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


# 🌟 加锁：必须拥有管理客户权限
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