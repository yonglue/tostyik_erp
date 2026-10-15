"""库存出入库流水：列表 / 新增（联动库存）/ 删除（回滚库存）。"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlmodel import Session, select, update

from app.database import get_session
from app.deps import Actor, get_current_actor
from app.models import AutoPart, InventoryTransaction
from app.services.audit import log_action

router = APIRouter(tags=["进销存"])


@router.get("/api/transactions", response_model=List[InventoryTransaction])
def get_transactions(session: Session = Depends(get_session)):
    return session.exec(select(InventoryTransaction).order_by(InventoryTransaction.id.desc())).all()


@router.post("/api/transactions", response_model=InventoryTransaction)
def create_transaction(
    tx: InventoryTransaction,
    actor: Actor = Depends(get_current_actor),
    session: Session = Depends(get_session),
):
    part = session.exec(select(AutoPart).where(AutoPart.oem == tx.part_oem)).first()
    old_stock = new_stock = None

    if part:
        old_stock = part.stock
        if tx.type == "IN":
            # 原子自增：避免并发时丢失更新
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

    tx.total_amount = tx.quantity * tx.unit_price
    session.add(tx)
    # 库存变动与流水记录必须在同一次提交里落库。
    # （历史实现在此之前调用 log_action，而它内部会 commit，
    #   导致流水插入失败时库存已经被改掉。）
    session.commit()
    session.refresh(tx)

    if part:
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


@router.delete("/api/transactions/{tx_id}")
def delete_transaction(
    tx_id: int,
    actor: Actor = Depends(get_current_actor),
    session: Session = Depends(get_session),
):
    tx = session.get(InventoryTransaction, tx_id)
    if not tx:
        raise HTTPException(status_code=404, detail="Movimiento no encontrado")

    part = session.exec(select(AutoPart).where(AutoPart.oem == tx.part_oem)).first()
    old_stock = new_stock = None

    if part:
        old_stock = part.stock
        if tx.type == "OUT":
            session.exec(
                update(AutoPart)
                .where(AutoPart.oem == tx.part_oem)
                .values(stock=AutoPart.stock + tx.quantity)
            )
            new_stock = old_stock + tx.quantity
        elif tx.type == "IN":
            # max(0, stock - qty) 在 SQL 里算，保证并发下也不会被扣成负数
            session.exec(
                update(AutoPart)
                .where(AutoPart.oem == tx.part_oem)
                .values(stock=func.max(0, AutoPart.stock - tx.quantity))
            )
            new_stock = max(0, old_stock - tx.quantity)

    session.delete(tx)
    # 同样是"库存回滚 + 删除流水"一次性提交
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
