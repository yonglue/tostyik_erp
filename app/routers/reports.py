"""经营看板与财务：全部口径统一从 orders / order_items 聚合。

财务契约（务必遵守）：
  * 净营收 = Σ Order.base_amount_usd        （不含任何税）
  * 销项税 = Σ Order.tax_amount_usd
  * IGTF    = Σ Order.igtf_amount_usd         （代收代缴，不是收入）
  * 实收    = Σ Order.total_usd
  * 销货成本 = Σ OrderItem.cost_price_usd × quantity（POS 卖出时的快照）
  * 退货：整单置为 REFUNDED，因此聚合只取 status = COMPLETED，天然净额
"""

from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from sqlalchemy import func

from app.database import get_session
from app.models import AutoPart, Client, Expense, Order, OrderItem
from app.services.fx import get_effective_rate

router = APIRouter(tags=["看板与财务"])

_COMPLETED = "COMPLETED"
LOW_STOCK_THRESHOLD = 5


def _range_for_date(target_date: str) -> tuple[datetime, datetime]:
    try:
        start = datetime.strptime(target_date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="日期格式必须为 YYYY-MM-DD")
    return start, start + timedelta(days=1)


def _order_totals(
    session: Session,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
) -> tuple[float, float, float, float, int]:
    """返回 (净营收, 销项税, IGTF, 实收, 订单数)。只统计 COMPLETED。"""
    stmt = select(
        func.coalesce(func.sum(Order.base_amount_usd), 0.0),
        func.coalesce(func.sum(Order.tax_amount_usd), 0.0),
        func.coalesce(func.sum(Order.igtf_amount_usd), 0.0),
        func.coalesce(func.sum(Order.total_usd), 0.0),
        func.count(Order.id),
    ).where(Order.status == _COMPLETED)
    if start is not None:
        stmt = stmt.where(Order.created_at >= start)
    if end is not None:
        stmt = stmt.where(Order.created_at < end)

    base, tax, igtf, total, count = session.execute(stmt).one()
    return float(base), float(tax), float(igtf), float(total), int(count)


def _sales_cost(
    session: Session,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
) -> float:
    """销货成本：直接读 POS 卖出时写入的成本快照，不再用 70% 估算。"""
    stmt = (
        select(func.coalesce(func.sum(OrderItem.cost_price_usd * OrderItem.quantity), 0.0))
        .join(Order, Order.id == OrderItem.order_id)
        .where(Order.status == _COMPLETED)
    )
    if start is not None:
        stmt = stmt.where(Order.created_at >= start)
    if end is not None:
        stmt = stmt.where(Order.created_at < end)
    return float(session.execute(stmt).scalar_one() or 0.0)


@router.get("/api/dashboard/stats")
def get_dashboard_stats(session: Session = Depends(get_session)):
    bcv = float(get_effective_rate().rate)

    inventory_cost, inventory_retail = session.execute(
        select(
            func.coalesce(func.sum(AutoPart.stock * AutoPart.cost_price), 0.0),
            func.coalesce(func.sum(AutoPart.stock * AutoPart.price), 0.0),
        )
    ).one()

    sku_count = session.execute(select(func.count(AutoPart.id))).scalar_one()
    low_stock_count = session.execute(
        select(func.count(AutoPart.id)).where(AutoPart.stock <= LOW_STOCK_THRESHOLD)
    ).scalar_one()

    base, tax, igtf, total, order_count = _order_totals(session)

    return {
        "totalAssetUSD": round(float(inventory_cost), 2),
        "totalAssetBs": round(float(inventory_cost) * bcv, 2),
        "totalRetailUSD": round(float(inventory_retail), 2),
        "totalSalesUSD": round(base + tax, 2),
        "totalSalesBs": round((base + tax) * bcv, 2),
        "totalNetSalesUSD": round(base, 2),
        "totalTaxUSD": round(tax, 2),
        "totalIgtfUSD": round(igtf, 2),
        "totalCollectedUSD": round(total, 2),
        "totalSKUs": int(sku_count),
        "lowStockCount": int(low_stock_count),
        "orderCount": int(order_count),
        "bcv_rate": bcv,
    }


@router.get("/api/financial/analytics")
def get_financial_analytics(session: Session = Depends(get_session)):
    bcv = float(get_effective_rate().rate)

    base, tax, igtf, total, order_count = _order_totals(session)
    cost = _sales_cost(session)

    inventory_cost = float(session.execute(
        select(func.coalesce(func.sum(AutoPart.stock * AutoPart.cost_price), 0.0))
    ).scalar_one())
    debt = float(session.execute(
        select(func.coalesce(func.sum(Client.debt), 0.0))
    ).scalar_one())

    expenses_usd = float(session.execute(
        select(func.coalesce(func.sum(Expense.amount), 0.0))
        .where(Expense.currency == "USD")
    ).scalar_one())
    expenses_bs = float(session.execute(
        select(func.coalesce(
            func.sum(Expense.amount / func.nullif(Expense.exchange_rate, 0)), 0.0
        )).where(Expense.currency != "USD")
    ).scalar_one())
    expenses = expenses_usd + expenses_bs

    gross = base - cost
    net = gross - expenses
    margin = (gross / base * 100.0) if base > 0 else 0.0

    return {
        "total_revenue_usd": round(base, 2),
        "total_sales_usd": round(base + tax, 2),
        "total_sales_bs": round((base + tax) * bcv, 2),
        "total_tax_usd": round(tax, 2),
        "total_igtf_usd": round(igtf, 2),
        "total_collected_usd": round(total, 2),
        "total_cost_usd": round(cost, 2),
        "gross_profit_usd": round(gross, 2),
        "profit_margin": round(margin, 2),
        "total_inventory_usd": round(inventory_cost, 2),
        "total_inventory_bs": round(inventory_cost * bcv, 2),
        "total_debt_usd": round(debt, 2),
        "total_debt_bs": round(debt * bcv, 2),
        "total_expenses_usd": round(expenses, 2),
        "net_profit_usd": round(net, 2),
        "order_count": int(order_count),
        "bcv_rate": bcv,
    }


@router.get("/api/sales/overview")
def get_sales_overview(
    target_date: Optional[str] = None,
    session: Session = Depends(get_session),
):
    bcv = float(get_effective_rate().rate)

    start = end = None
    if target_date:
        start, end = _range_for_date(target_date)

    base, tax, igtf, total, count = _order_totals(session, start, end)
    hist_base, hist_tax, _, hist_total, hist_count = _order_totals(session)
    day_cost = _sales_cost(session, start, end)

    pay_stmt = (
        select(Order.payment_method, func.coalesce(func.sum(Order.total_usd), 0.0))
        .where(Order.status == _COMPLETED)
        .group_by(Order.payment_method)
    )
    if start is not None:
        pay_stmt = pay_stmt.where(Order.created_at >= start, Order.created_at < end)

    payment_breakdown = {
        key: 0.0 for key in ("Cash_USD", "Zelle", "Pago_Movil", "Transfer_Bs", "USDT")
    }
    for method, amount in session.execute(pay_stmt).all():
        key = method or "Unknown"
        payment_breakdown[key] = round(payment_breakdown.get(key, 0.0) + float(amount), 2)

    item_stmt = (
        select(
            OrderItem.oem,
            func.min(OrderItem.name),
            func.coalesce(func.sum(OrderItem.quantity), 0),
            func.coalesce(func.sum(OrderItem.subtotal_usd), 0.0),
        )
        .join(Order, Order.id == OrderItem.order_id)
        .where(Order.status == _COMPLETED)
        .group_by(OrderItem.oem)
    )
    if start is not None:
        item_stmt = item_stmt.where(Order.created_at >= start, Order.created_at < end)

    product_sales_items = [
        {
            "oem": oem,
            "name": name,
            "total_qty": int(qty),
            "total_amount": round(float(amount), 2),
        }
        for oem, name, qty, amount in session.execute(item_stmt).all()
    ]
    product_sales_items.sort(key=lambda item: item["total_amount"], reverse=True)

    skus_sold = session.execute(
        select(func.coalesce(func.sum(OrderItem.quantity), 0))
        .join(Order, Order.id == OrderItem.order_id)
        .where(Order.status == _COMPLETED)
    ).scalar_one()

    raw_stmt = (
        select(OrderItem, Order)
        .join(Order, Order.id == OrderItem.order_id)
        .where(Order.status == _COMPLETED)
        .order_by(Order.id.desc(), OrderItem.id.asc())
        .limit(500)
    )
    raw_transactions = [
        {
            "id": order_item.id,
            "oem": order_item.oem,
            "name": order_item.name,
            "quantity": order_item.quantity,
            "unit_price": order_item.price_usd,
            "total_amount": order_item.subtotal_usd,
            "type": "OUT",
            "customer": order.client_name,
            "timestamp": (
                order.created_at.strftime("%Y-%m-%d %H:%M:%S")
                if order.created_at else ""
            ),
        }
        for order_item, order in session.execute(raw_stmt).all()
    ]

    return {
        "daily_total_usd": round(base + tax, 2),
        "daily_net_usd": round(base, 2),
        "daily_tax_usd": round(tax, 2),
        "daily_cost_usd": round(day_cost, 2),
        "daily_gross_profit_usd": round(base - day_cost, 2),
        "daily_total_bs": round((base + tax) * bcv, 2),
        "history_total_usd": round(hist_base + hist_tax, 2),
        "history_net_usd": round(hist_base, 2),
        "history_total_transactions": int(hist_count),
        "history_total_skus_sold": int(skus_sold),
        "payment_breakdown": payment_breakdown,
        "product_sales_items": product_sales_items,
        "raw_transactions": raw_transactions,
        "bcv_rate": bcv,
    }