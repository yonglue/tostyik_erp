"""库存出入库流水：列表 / 新增（联动库存）/ 删除（回滚库存）。"""

from typing import List, Optional
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func
from sqlmodel import Session, select, update

from app.database import get_session
from app.deps import Actor, RequirePermission # 🌟 引入细粒度权限
from app.models import AutoPart, InventoryTransaction
from app.services.audit import log_action

router = APIRouter(tags=["进销存"])


# 🌟 定义专属的请求载荷（防止因为模型必填字段缺失导致 422 报错）
class ManualTransactionPayload(BaseModel):
    type: str
    part_oem: str
    part_name: str
    quantity: int
    unit_price: float
    customer_or_supplier: Optional[str] = ""


def _resolve_part_by_oem(session: Session, oem: str) -> AutoPart:
    """手工流水没有 brand 字段：同 OEM 多品牌时必须拒绝，不能任选一行改库存。"""
    matches = session.exec(select(AutoPart).where(AutoPart.oem == oem)).all()
    if not matches:
        raise HTTPException(
            status_code=404,
            detail=f"商品 OEM [{oem}] 不存在，无法操作库存",
        )
    if len(matches) > 1:
        raise HTTPException(
            status_code=400,
            detail=(
                f"OEM [{oem}] 存在多个品牌，手工流水无法定位具体商品；"
                "请改用带品牌的 POS / 采购收货流程"
            ),
        )
    return matches[0]


# 🌟 加锁：必须拥有查看历史流水的权限
@router.get("/api/transactions")
def get_transactions(
    page: int = 1,
    page_size: int = 20,
    tx_type: Optional[str] = None,
    session: Session = Depends(get_session),
    actor: Actor = Depends(RequirePermission("transactions:history")),
):
    # 1) 基础过滤（ALL / OUT / IN）
    base = select(InventoryTransaction)
    if tx_type == "OUT":
        base = base.where(InventoryTransaction.type.in_(["OUT", "REFUND"]))
    elif tx_type == "IN":
        base = base.where(InventoryTransaction.type == "IN")

    # 2) 总数（用于分页）
    total = session.exec(
        select(func.count()).select_from(base.subquery())
    ).one()

    # 3) 全量汇总（不受分页/过滤影响，始终返回全部数据的进出总额）
    summary_rows = session.exec(
        select(InventoryTransaction.type, func.sum(InventoryTransaction.total_amount))
        .group_by(InventoryTransaction.type)
    ).all()
    summary = {"in_total": 0.0, "out_total": 0.0}
    for t, s in summary_rows:
        s = float(s or 0)
        if t == "IN":
            summary["in_total"] += s
        else:  # OUT / REFUND 归入出货
            summary["out_total"] += s

    # 4) 当前页
    page = max(1, page)
    page_size = max(1, min(page_size, 100))
    items = session.exec(
        base.order_by(InventoryTransaction.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
    ).all()

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "summary": summary,
    }


# 🌟 加锁：必须拥有管理库存的权限
@router.post("/api/transactions", response_model=InventoryTransaction)
def create_transaction(
    payload: ManualTransactionPayload, # 🌟 改为接收自定义载荷
    actor: Actor = Depends(RequirePermission("parts:manage")),
    session: Session = Depends(get_session),
):
    # 🌟 校验类型合法性
    if payload.type not in ("IN", "OUT"):
        raise HTTPException(status_code=400, detail="无效的库存变动类型，只能是 'IN' 或 'OUT'")
    if payload.quantity <= 0:
        raise HTTPException(status_code=400, detail="库存变动数量必须大于 0")

    part = _resolve_part_by_oem(session, payload.part_oem)

    old_stock = part.stock
    new_stock = old_stock

    if payload.type == "IN":
        # 原子自增，按主键精确命中一行
        changed = session.exec(
            update(AutoPart)
            .where(AutoPart.id == part.id)
            .values(stock=AutoPart.stock + payload.quantity)
        )
        if changed.rowcount != 1:
            session.rollback()
            raise HTTPException(status_code=409, detail="商品已变更，请刷新后重试")
        new_stock = old_stock + payload.quantity
    elif payload.type == "OUT":
        # 原子条件扣减：并发时只有一个能扣成功，避免超卖
        changed = session.exec(
            update(AutoPart)
            .where(AutoPart.id == part.id, AutoPart.stock >= payload.quantity)
            .values(stock=AutoPart.stock - payload.quantity)
        )
        if changed.rowcount != 1:
            session.rollback()
            raise HTTPException(status_code=400, detail="库存不足，无法出库！")
        new_stock = old_stock - payload.quantity

    # 🌟 精度保护：使用 Decimal 计算流水总额，并组装数据库模型
    d_price = Decimal(str(payload.unit_price))
    d_qty = Decimal(str(payload.quantity))
    calculated_total = float((d_price * d_qty).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
    
    new_tx = InventoryTransaction(
        type=payload.type,
        part_oem=payload.part_oem,
        part_name=payload.part_name,
        quantity=payload.quantity,
        unit_price=payload.unit_price,
        total_amount=calculated_total,
        customer_or_supplier=payload.customer_or_supplier,
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S") # 补齐时间戳
    )
    
    session.add(new_tx)
    session.commit()
    session.refresh(new_tx)

    log_action(
        session=session,
        username=actor.username,
        role=actor.role,
        action="UPDATE_STOCK",
        details=(
            f"进销存单据导致库存变动: {part.name} (OEM: {new_tx.part_oem}), "
            f"原库存: {old_stock} -> 新库存: {new_stock} (类型: {new_tx.type}, 数量: {new_tx.quantity})"
        ),
    )

    return new_tx


# 🌟 加锁：必须拥有管理库存的权限（流水删除是非常敏感的操作）
@router.delete("/api/transactions/{tx_id}")
def delete_transaction(
    tx_id: int,
    actor: Actor = Depends(RequirePermission("parts:manage")),
    session: Session = Depends(get_session),
):
    tx = session.get(InventoryTransaction, tx_id)
    if not tx:
        raise HTTPException(status_code=404, detail="流水记录不存在")

    if tx.type not in ("IN", "OUT"):
        raise HTTPException(
            status_code=400,
            detail="只有手工入库/出库流水可以删除；系统生成的退款/采购流水请走对应业务流程",
        )

    matches = session.exec(select(AutoPart).where(AutoPart.oem == tx.part_oem)).all()
    if len(matches) > 1:
        raise HTTPException(
            status_code=400,
            detail=(
                f"OEM [{tx.part_oem}] 存在多个品牌，无法确定要回滚哪一行库存；"
                "请先拆分商品档案"
            ),
        )
    part = matches[0] if matches else None
    old_stock = new_stock = None

    if part:
        old_stock = part.stock
        if tx.type == "OUT":
            # 删除出库单，意味着把货退回来，库存增加
            changed = session.exec(
                update(AutoPart)
                .where(AutoPart.id == part.id)
                .values(stock=AutoPart.stock + tx.quantity)
            )
            if changed.rowcount != 1:
                session.rollback()
                raise HTTPException(status_code=409, detail="商品已变更，请刷新后重试")
            new_stock = old_stock + tx.quantity
        elif tx.type == "IN":
            # 删除入库单，意味着把货拿走，库存减少（兜底不能扣成负数）
            changed = session.exec(
                update(AutoPart)
                .where(AutoPart.id == part.id)
                .values(stock=func.max(0, AutoPart.stock - tx.quantity))
            )
            if changed.rowcount != 1:
                session.rollback()
                raise HTTPException(status_code=409, detail="商品已变更，请刷新后重试")
            new_stock = max(0, old_stock - tx.quantity)

    session.delete(tx)
    session.commit()

    if part:
        log_action(
            session=session,
            username=actor.username,
            role=actor.role,
            action="UPDATE_STOCK",
            details=(
                f"删除单据回滚库存: {part.name} (OEM: {tx.part_oem}), "
                f"原库存: {old_stock} -> 新库存: {new_stock}"
            ),
        )

    return {"status": "success", "message": "Transaction deleted and stock rolled back."}