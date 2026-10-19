"""库存出入库流水：列表 / 新增（联动库存）/ 删除（回滚库存）。"""

from typing import List
from decimal import Decimal, ROUND_HALF_UP

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlmodel import Session, select, update

from app.database import get_session
from app.deps import Actor, RequirePermission # 🌟 引入细粒度权限
from app.models import AutoPart, InventoryTransaction
from app.services.audit import log_action

router = APIRouter(tags=["进销存"])

# 🌟 加锁：必须拥有查看历史流水的权限
@router.get("/api/transactions", response_model=List[InventoryTransaction])
def get_transactions(
    session: Session = Depends(get_session),
    actor: Actor = Depends(RequirePermission("transactions:history"))
):
    return session.exec(select(InventoryTransaction).order_by(InventoryTransaction.id.desc())).all()


# 🌟 加锁：必须拥有管理库存的权限
@router.post("/api/transactions", response_model=InventoryTransaction)
def create_transaction(
    tx: InventoryTransaction,
    actor: Actor = Depends(RequirePermission("parts:manage")),
    session: Session = Depends(get_session),
):
    # 🌟 校验类型合法性
    if tx.type not in ("IN", "OUT"):
        raise HTTPException(status_code=400, detail="无效的库存变动类型，只能是 'IN' 或 'OUT'")

    part = session.exec(select(AutoPart).where(AutoPart.oem == tx.part_oem)).first()
    
    # 🌟 核心修复：如果商品不存在，绝对不允许产生流水（避免幽灵记录）
    if not part:
        raise HTTPException(status_code=404, detail=f"商品 OEM [{tx.part_oem}] 不存在，无法操作库存")

    old_stock = part.stock
    new_stock = old_stock

    if tx.type == "IN":
        # 原子自增
        session.exec(
            update(AutoPart)
            .where(AutoPart.oem == tx.part_oem)
            .values(stock=AutoPart.stock + tx.quantity)
        )
        new_stock = old_stock + tx.quantity
    elif tx.type == "OUT":
        # 原子条件扣减：并发时只有一个能扣成功，避免超卖
        changed = session.exec(
            update(AutoPart)
            .where(AutoPart.oem == tx.part_oem, AutoPart.stock >= tx.quantity)
            .values(stock=AutoPart.stock - tx.quantity)
        )
        if changed.rowcount == 0:
            session.rollback()
            raise HTTPException(status_code=400, detail="库存不足，无法出库！")
        new_stock = old_stock - tx.quantity

    # 🌟 精度保护：使用 Decimal 计算流水总额
    d_price = Decimal(str(tx.unit_price))
    d_qty = Decimal(str(tx.quantity))
    tx.total_amount = float((d_price * d_qty).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
    
    session.add(tx)
    session.commit()
    session.refresh(tx)

    log_action(
        session=session,
        username=actor.username,
        role=actor.role,
        action="UPDATE_STOCK",
        details=(
            f"进销存单据导致库存变动: {part.name} (OEM: {tx.part_oem}), "
            f"原库存: {old_stock} -> 新库存: {new_stock} (类型: {tx.type}, 数量: {tx.quantity})"
        ),
    )

    return tx


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

    part = session.exec(select(AutoPart).where(AutoPart.oem == tx.part_oem)).first()
    old_stock = new_stock = None

    if part:
        old_stock = part.stock
        if tx.type == "OUT":
            # 删除出库单，意味着把货退回来，库存增加
            session.exec(
                update(AutoPart)
                .where(AutoPart.oem == tx.part_oem)
                .values(stock=AutoPart.stock + tx.quantity)
            )
            new_stock = old_stock + tx.quantity
        elif tx.type == "IN":
            # 删除入库单，意味着把货拿走，库存减少（兜底不能扣成负数）
            session.exec(
                update(AutoPart)
                .where(AutoPart.oem == tx.part_oem)
                .values(stock=func.max(0, AutoPart.stock - tx.quantity))
            )
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