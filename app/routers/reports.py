"""经营看板与收银班结：汇率 / 仪表盘 / 财务分析 / 销售总览 / 班结记录。"""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.database import get_session
from app.models import (
    AutoPart,
    CashRegisterSession,
    Client,
    InventoryTransaction,
    QuotationRecord,
)
from app.schemas import CashRegisterCreatePayload
from app.services.bcv import get_official_rate, scrape_bcv_rate

router = APIRouter(tags=["看板与财务"])


@router.get("/api/bcv-rate")
def get_bcv_rate():
    return scrape_bcv_rate()


@router.get("/api/dashboard/stats")
def get_dashboard_stats(session: Session = Depends(get_session)):
    parts = session.exec(select(AutoPart)).all()
    transactions = session.exec(select(InventoryTransaction)).all()
    bcv_rate = get_official_rate()

    total_inventory_usd = sum(p.stock * p.price for p in parts)
    total_inventory_bs = total_inventory_usd * bcv_rate
    total_sales_usd = sum(tx.total_amount for tx in transactions if tx.type == "OUT")
    total_sales_bs = total_sales_usd * bcv_rate
    low_stock_count = len([p for p in parts if p.stock <= 5])

    return {
        "total_inventory_usd": total_inventory_usd,
        "total_inventory_bs": total_inventory_bs,
        "total_sales_usd": total_sales_usd,
        "total_sales_bs": total_sales_bs,
        "total_skus": len(parts),
        "low_stock_count": low_stock_count,
        "total_transactions": len(transactions),
        "bcv_rate": bcv_rate,
    }


@router.get("/api/financial/analytics")
def get_financial_analytics(session: Session = Depends(get_session)):
    parts = session.exec(select(AutoPart)).all()
    transactions = session.exec(select(InventoryTransaction)).all()
    clients = session.exec(select(Client)).all()

    bcv_rate = get_official_rate()

    total_inventory_usd = sum(p.stock * p.price for p in parts)
    total_sales_usd = sum(tx.total_amount for tx in transactions if tx.type == "OUT")
    total_debt_usd = sum(c.debt for c in clients)

    return {
        "total_inventory_usd": total_inventory_usd,
        "total_inventory_bs": total_inventory_usd * bcv_rate,
        "total_sales_usd": total_sales_usd,
        "total_sales_bs": total_sales_usd * bcv_rate,
        "total_debt_usd": total_debt_usd,
        "total_debt_bs": total_debt_usd * bcv_rate,
        "bcv_rate": bcv_rate,
    }


@router.get("/api/sales/overview")
def get_sales_overview(target_date: Optional[str] = None, session: Session = Depends(get_session)):
    transactions = session.exec(select(InventoryTransaction)).all()
    quotations = session.exec(select(QuotationRecord)).all()

    bcv_rate = get_official_rate()

    filtered_txs = transactions
    if target_date:
        filtered_txs = [t for t in transactions if t.timestamp.startswith(target_date)]

    daily_total_usd = sum(t.total_amount for t in filtered_txs if t.type == "OUT")
    daily_total_bs = daily_total_usd * bcv_rate
    history_total_usd = sum(t.total_amount for t in transactions if t.type == "OUT")

    payment_breakdown = {
        "Cash_USD": sum(t.total_amount for t in filtered_txs if t.type == "OUT"),
        "Zelle": 0.0,
        "Pago_Movil": 0.0,
        "Transfer_Bs": 0.0,
        "USDT": 0.0,
    }

    product_sales_map = {}
    for t in filtered_txs:
        if t.type == "OUT":
            if t.part_oem not in product_sales_map:
                product_sales_map[t.part_oem] = {
                    "oem": t.part_oem,
                    "name": t.part_name,
                    "total_qty": 0,
                    "total_amount": 0.0,
                }
            product_sales_map[t.part_oem]["total_qty"] += t.quantity
            product_sales_map[t.part_oem]["total_amount"] += t.total_amount

    history_total_skus_sold = sum(t.quantity for t in transactions if t.type == "OUT")

    return {
        "daily_total_usd": float(daily_total_usd),
        "daily_total_bs": float(daily_total_bs),
        "history_total_usd": float(history_total_usd),
        "history_total_transactions": len(quotations),
        "history_total_skus_sold": int(history_total_skus_sold),
        "payment_breakdown": payment_breakdown,
        "product_sales_items": list(product_sales_map.values()),
        "raw_transactions": [
            {
                "id": t.id,
                "oem": t.part_oem,
                "name": t.part_name,
                "quantity": t.quantity,
                "unit_price": t.unit_price,
                "total_amount": t.total_amount,
                "customer": t.customer_or_supplier,
                "timestamp": t.timestamp,
            } for t in filtered_txs[::-1]
        ],
    }


@router.get("/api/cash-register/sessions")
def get_cash_register_sessions(session: Session = Depends(get_session)):
    sessions = session.exec(select(CashRegisterSession).order_by(CashRegisterSession.id.desc())).all()
    safe_sessions = []
    for s in sessions:
        s_dict = s.model_dump()
        for k, v in s_dict.items():
            if isinstance(v, (int, float)) and (v is None):
                s_dict[k] = 0.0
            elif isinstance(v, float) and (str(v) == "nan" or str(v) == "inf"):
                s_dict[k] = 0.0
        safe_sessions.append(s_dict)
    return safe_sessions


@router.post("/api/cash-register/sessions")
def create_cash_register_session(
    payload: CashRegisterCreatePayload,
    session: Session = Depends(get_session),
):
    reg_session = CashRegisterSession(
        operator=payload.operator,
        bcv_rate_snapshot=payload.bcv_rate_snapshot,
        system_cash_usd=payload.system_cash_usd,
        system_zelle=payload.system_zelle,
        system_pago_movil=payload.system_pago_movil,
        system_transfer_bs=payload.system_transfer_bs,
        system_usdt=payload.system_usdt,
        actual_cash_usd=payload.actual_cash_usd,
        actual_zelle=payload.actual_zelle,
        actual_pago_movil=payload.actual_pago_movil,
        actual_transfer_bs=payload.actual_transfer_bs,
        actual_usdt=payload.actual_usdt,
        total_revenue_usd=payload.total_revenue_usd,
        notes=payload.notes,
    )
    session.add(reg_session)
    session.commit()
    session.refresh(reg_session)
    return {"status": "success", "id": reg_session.id}
