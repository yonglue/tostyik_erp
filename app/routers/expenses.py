"""日常开支管理 (Gastos)"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlmodel import Session, select, desc

from app.database import get_session
from app.deps import Actor, RequirePermission
from app.models import Expense
from app.services.audit import log_action

router = APIRouter(tags=["日常开支"])

# ──────────────────────────── 入参模型 ────────────────────────────
class ExpenseCreatePayload(BaseModel):
    category: str = Field(..., max_length=50)
    description: str = Field(default="", max_length=255)
    amount: float = Field(..., gt=0) # 金额必须大于 0
    currency: str = Field(default="USD", max_length=10)
    exchange_rate: float = Field(default=1.0)
    payment_method: str = Field(default="Cash_USD", max_length=50)
    receipt_url: str = Field(default="")
    created_by: str = Field(default="Admin", max_length=50)
    expense_date: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))

class ExpenseUpdatePayload(ExpenseCreatePayload):
    pass


# ──────────────────────────── 接口列表 ────────────────────────────

@router.get("/api/expenses")
def get_expenses(
    month: Optional[str] = Query(None, description="按月份过滤，格式 YYYY-MM"),
    session: Session = Depends(get_session),
    actor: Actor = Depends(RequirePermission("financial:view"))
):
    """获取开支列表，可按月份筛选"""
    query = select(Expense).order_by(desc(Expense.expense_date), desc(Expense.id))
    
    if month:
        # 简单的字符串匹配，假设 expense_date 格式为 YYYY-MM-DD
        query = query.where(Expense.expense_date.like(f"{month}%"))
        
    return session.exec(query).all()


@router.post("/api/expenses")
def create_expense(
    payload: ExpenseCreatePayload,
    session: Session = Depends(get_session),
    actor: Actor = Depends(RequirePermission("financial:view")) # 后续如果你有 financial:manage 可以换成它
):
    """新增一条日常开支"""
    new_expense = Expense(**payload.model_dump())
    session.add(new_expense)
    session.commit()
    session.refresh(new_expense)

    log_action(
        session=session,
        username=actor.username,
        role=actor.role,
        action="CREATE_EXPENSE",
        details=f"新增开支: {payload.category} - {payload.amount} {payload.currency} ({payload.description})"
    )

    return {"status": "success", "data": new_expense}


@router.put("/api/expenses/{expense_id}")
def update_expense(
    expense_id: int,
    payload: ExpenseUpdatePayload,
    session: Session = Depends(get_session),
    actor: Actor = Depends(RequirePermission("financial:view"))
):
    """修改日常开支"""
    expense = session.get(Expense, expense_id)
    if not expense:
        raise HTTPException(status_code=404, detail="未找到该开支记录")

    for key, value in payload.model_dump().items():
        setattr(expense, key, value)
    
    session.add(expense)
    session.commit()

    log_action(
        session=session,
        username=actor.username,
        role=actor.role,
        action="UPDATE_EXPENSE",
        details=f"修改开支 (ID:{expense_id}): {payload.category} - {payload.amount}"
    )

    return {"status": "success", "data": expense}


@router.delete("/api/expenses/{expense_id}")
def delete_expense(
    expense_id: int,
    session: Session = Depends(get_session),
    actor: Actor = Depends(RequirePermission("financial:view"))
):
    """删除日常开支"""
    expense = session.get(Expense, expense_id)
    if not expense:
        raise HTTPException(status_code=404, detail="未找到该开支记录")

    session.delete(expense)
    session.commit()

    log_action(
        session=session,
        username=actor.username,
        role=actor.role,
        action="DELETE_EXPENSE",
        details=f"删除开支 (ID:{expense_id}): {expense.category} - {expense.amount}"
    )

    return {"status": "success"}