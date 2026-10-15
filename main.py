"""兼容入口与启动脚本。

应用装配已迁移到 `app.main`。保留本模块是为了兼容历史引用方式：
测试与脚本中的 ``from main import app, get_session, ...`` 仍然可用。
"""

from app.database import engine, get_session, init_db
from app.main import app
from app.models import (
    AdminUser,
    AuditLog,
    AutoPart,
    CashRegisterSession,
    Client,
    ClientPaymentRecord,
    InventoryTransaction,
    Order,
    OrderItem,
    PurchaseOrder,
    QuotationRecord,
    StaffUser,
    Supplier,
)
from app.security import hash_password, verify_password
from app.services.audit import log_action

__all__ = [
    "app",
    "engine",
    "get_session",
    "init_db",
    "log_action",
    "hash_password",
    "verify_password",
    "AdminUser",
    "AuditLog",
    "AutoPart",
    "CashRegisterSession",
    "Client",
    "ClientPaymentRecord",
    "InventoryTransaction",
    "Order",
    "OrderItem",
    "PurchaseOrder",
    "QuotationRecord",
    "StaffUser",
    "Supplier",
]


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
