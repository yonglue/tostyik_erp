"""客户档案：列表 / 新增 / 还款 / 未结清订单查询。"""

from decimal import Decimal, ROUND_HALF_UP
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlmodel import Session, select, update
import re

from app.database import get_session
from app.deps import Actor, get_current_actor, RequirePermission 
from app.models import Client, ClientPaymentRecord, InventoryTransaction
from app.schemas import ClientPaymentPayload
from app.services.audit import log_action

router = APIRouter(tags=["客户"])

# 🌟 辅助函数：从本地配置读取当前手动汇率
import os
import json
from app.config import DB_PATH
SETTINGS_FILE = os.path.join(os.path.dirname(DB_PATH), "system_settings.json")

def get_local_rate() -> float:
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                return float(json.load(f).get("bcv_rate", 36.50))
    except Exception:
        pass
    return 36.50

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
    # 1. 放宽电话号码校验：允许 + 号、数字、横杠、空格，长度 8-15 位 (兼容本地号码 04xx 和 +58)
    if client.phone and client.phone != "":
        if not re.match(r"^[\d\+\-\s]{8,15}$", client.phone):
            raise HTTPException(status_code=400, detail="电话号码格式错误：只能包含数字、+号、横杠，长度 8-15 位")
    
    # 2. 放宽 RIF 校验：横杠 '-' 变为可选，且自动忽略大小写
    if client.rif_or_cedula and client.rif_or_cedula != "":
        # 将输入转成大写，去除前后空格
        rif_clean = client.rif_or_cedula.strip().upper()
        if not re.match(r"^[VEJG]-?\d{8,9}$", rif_clean):
            raise HTTPException(status_code=400, detail="RIF 格式错误：需以 V/E/J/G 开头，后跟 8-9 位数字，横杠可有可无")
        
        # 把整理好的干净 RIF 重新赋值给要存库的数据
        client.rif_or_cedula = rif_clean

    session.add(client)
    session.commit()
    session.refresh(client)
    log_action(session=session, username=actor.username, role=actor.role, action="CREATE_CLIENT",
               details=f"新增客户: {client.name} (RIF: {client.rif_or_cedula})")
    return client

@router.put("/api/clients/{client_id}", response_model=Client)
def update_client(
    client_id: int,
    client_data: Client, # 直接使用 Client 模型接收前端传来的数据
    actor: Actor = Depends(RequirePermission("clients:manage")),
    session: Session = Depends(get_session),
):
    # 1. 去数据库里找这个客户
    db_client = session.get(Client, client_id)
    if not db_client:
        raise HTTPException(status_code=404, detail="客户不存在")

    # 2. 校验电话格式（和新建保持一样的宽松规则）
    if client_data.phone and client_data.phone != "":
        if not re.match(r"^[\d\+\-\s]{8,15}$", client_data.phone):
            raise HTTPException(status_code=400, detail="电话号码格式错误：只能包含数字、+号、横杠，长度 8-15 位")
    
    # 3. 校验 RIF 格式
    if client_data.rif_or_cedula and client_data.rif_or_cedula != "":
        rif_clean = client_data.rif_or_cedula.strip().upper()
        if not re.match(r"^[VEJG]-?\d{8,9}$", rif_clean):
            raise HTTPException(status_code=400, detail="RIF 格式错误：需以 V/E/J/G 开头，后跟 8-9 位数字，横杠可有可无")
        client_data.rif_or_cedula = rif_clean

    # 4. 更新数据
    db_client.name = client_data.name
    # 注意：确保你的 models.py 的 Client 里加了 store_name 字段
    db_client.store_name = client_data.store_name 
    db_client.client_type = client_data.client_type
    db_client.phone = client_data.phone
    db_client.address = client_data.address
    db_client.rif_or_cedula = client_data.rif_or_cedula
    db_client.notes = client_data.notes
    
    # 注意：debt（欠款）不能直接让前端随意修改，所以这里不要更新 debt 字段

    # 5. 保存并记录日志
    session.add(db_client)
    session.commit()
    session.refresh(db_client)
    
    log_action(
        session=session, 
        username=actor.username, 
        role=actor.role, 
        action="UPDATE_CLIENT",
        details=f"修改客户: {db_client.name} (ID: {db_client.id})"
    )
    
    return db_client


@router.post("/api/clients/repay")
def client_repayment(
    payload: ClientPaymentPayload,
    actor: Actor = Depends(RequirePermission("fiado:pay")),
    session: Session = Depends(get_session),
):
    client = session.exec(select(Client).where(Client.name == payload.client_name)).first()
    if not client:
        raise HTTPException(status_code=404, detail="客户档案不存在")

    # 🌟 核心修复：使用本地手动配置的汇率，而不是联网抓取
    bcv_rate = get_local_rate()
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
    session.commit()
    session.refresh(client)

    log_action(
        session=session, username=actor.username, role=actor.role,
        action="CLIENT_REPAYMENT",
        details=(f"客户 {client.name} 还款: {payload.amount_paid} {curr} (折合 ${amount_usd_eq:.2f} USD)"),
    )
    
    return {
        "status": "success",
        "amount_usd_equivalent": float(amount_usd_eq),
        "remaining_debt": client.debt,
        "bcv_rate": float(bcv_rate),
    }

# 🌟 新增：获取总应收欠款统计（给财务看板用）
@router.get("/api/clients/analytics/debt-summary")
def get_debt_summary(
    session: Session = Depends(get_session),
    actor: Actor = Depends(RequirePermission("clients:view"))
):
    total_debt = session.exec(select(func.sum(Client.debt)).where(Client.debt > 0)).one() or 0.0
    
    # 获取最近还款记录流水
    recent_payments = session.exec(
        select(ClientPaymentRecord).order_by(ClientPaymentRecord.id.desc()).limit(50)
    ).all()
    
    total_repaid_usd = sum(p.amount_usd for p in recent_payments)

    return {
        "total_debt_usd": float(total_debt),
        "recent_repaid_usd": float(total_repaid_usd)
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
    log_action(session=session, username=actor.username, role=actor.role, action="DELETE_CLIENT",
               details=f"删除了客户档案: {client_name} (ID: {client_id})")
    return {"status": "success", "message": f"客户 {client_name} 已成功删除"}