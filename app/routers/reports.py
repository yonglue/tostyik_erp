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

_REFUND_TYPE = "REFUND"
_LEGACY_REFUND_PREFIX = "退货回滚-"


def _is_refund(tx: InventoryTransaction) -> bool:
    """退款流水：新数据用 type=REFUND，旧数据用 IN + 固定前缀。"""
    return tx.type == _REFUND_TYPE or (
        tx.type == "IN"
        and (tx.customer_or_supplier or "").startswith(_LEGACY_REFUND_PREFIX)
    )


def _sales_delta(tx: InventoryTransaction) -> float:
    """出库记正营业额，退款记负营业额，进货入库不计。"""
    if tx.type == "OUT":
        return tx.total_amount
    if _is_refund(tx):
        return -tx.total_amount
    return 0.0


def _cost_delta(tx: InventoryTransaction) -> float:
    """沿用 70% 售价估算成本，退款时反向冲减成本。"""
    if tx.type == "OUT":
        return tx.quantity * tx.unit_price * 0.7
    if _is_refund(tx):
        return -tx.quantity * tx.unit_price * 0.7
    return 0.0


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
    total_sales_usd = sum(_sales_delta(tx) for tx in transactions)
    total_sales_bs = total_sales_usd * bcv_rate
    low_stock_count = len([p for p in parts if p.stock <= 5])

    return {
        "totalAssetUSD": total_inventory_usd,    # 🌟 完美匹配前端字段
        "totalAssetBs": total_inventory_bs,      # 🌟 完美匹配前端字段
        "totalSalesUSD": total_sales_usd,        # 🌟 完美匹配前端字段
        "totalSalesBs": total_sales_bs,          # 🌟 完美匹配前端字段
        "totalSKUs": len(parts),                 # 🌟 完美匹配前端字段
        "lowStockCount": low_stock_count,        # 🌟 完美匹配前端字段
        "bcv_rate": bcv_rate,
    }


@router.get("/api/financial/analytics")
def get_financial_analytics(session: Session = Depends(get_session)):
    parts = session.exec(select(AutoPart)).all()
    transactions = session.exec(select(InventoryTransaction)).all()
    clients = session.exec(select(Client)).all()

    bcv_rate = get_official_rate()

    total_inventory_usd = sum(p.stock * p.price for p in parts)
    
    # 1. 总营业收入 = 出库 - 退款
    total_sales_usd = sum(_sales_delta(tx) for tx in transactions)
    
    # 2. 估算成本，退款时按同样的 70% 口径反向冲减
    total_cost_usd = sum(_cost_delta(tx) for tx in transactions)
    
    # 3. 计算毛利与毛利率
    gross_profit_usd = total_sales_usd - total_cost_usd
    profit_margin = (gross_profit_usd / total_sales_usd * 100.0) if total_sales_usd > 0 else 0.0

    total_debt_usd = sum(c.debt for c in clients)

    return {
        "total_revenue_usd": total_sales_usd,       # 🌟 完美适配前端字段
        "total_cost_usd": total_cost_usd,           # 🌟 总进货成本
        "gross_profit_usd": gross_profit_usd,       # 🌟 毛利润
        "profit_margin": profit_margin,             # 🌟 毛利率
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

    daily_total_usd = sum(_sales_delta(t) for t in filtered_txs)
    daily_total_bs = daily_total_usd * bcv_rate
    history_total_usd = sum(_sales_delta(t) for t in transactions)

    payment_breakdown = {
        # 这里原本就是按单一渠道占位的近似值，至少保持与净营业额一致
        "Cash_USD": daily_total_usd,
        "Zelle": 0.0,
        "Pago_Movil": 0.0,
        "Transfer_Bs": 0.0,
        "USDT": 0.0,
    }

    product_sales_map = {}
    for t in filtered_txs:
        delta = _sales_delta(t)
        if delta == 0:
            continue
        if t.part_oem not in product_sales_map:
            product_sales_map[t.part_oem] = {
                "oem": t.part_oem,
                "name": t.part_name,
                "total_qty": 0,
                "total_amount": 0.0,
            }
        qty_delta = t.quantity if t.type == "OUT" else -t.quantity
        product_sales_map[t.part_oem]["total_qty"] += qty_delta
        product_sales_map[t.part_oem]["total_amount"] += delta

    product_sales_items = [
        item for item in product_sales_map.values() if item["total_qty"] > 0
    ]

    history_total_skus_sold = sum(
        t.quantity if t.type == "OUT" else -t.quantity if _is_refund(t) else 0
        for t in transactions
    )

    return {
        "daily_total_usd": float(daily_total_usd),
        "daily_total_bs": float(daily_total_bs),
        "history_total_usd": float(history_total_usd),
        "history_total_transactions": len(quotations),
        "history_total_skus_sold": int(history_total_skus_sold),
        "payment_breakdown": payment_breakdown,
        "product_sales_items": product_sales_items,
        "raw_transactions": [
            {
                "id": t.id,
                "oem": t.part_oem,
                "name": t.part_name,
                "quantity": t.quantity,
                "unit_price": t.unit_price,
                "total_amount": t.total_amount,
                "type": t.type,
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
