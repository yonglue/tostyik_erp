"""全部数据表定义（统一 SQLModel）。"""

from datetime import datetime, timezone, timedelta
from typing import List, Optional
import json

from pydantic import NaiveDatetime
from sqlmodel import Field, Relationship, SQLModel, Column, Text

# 细粒度权限定义
ALL_PERMISSIONS = [
    "pos:access", "pos:checkout", "pos:hold", "pos:discount",
    "parts:view", "parts:manage", "parts:import",
    "clients:view", "clients:manage", "fiado:pay",
    "quotations:export", "procurement:view",
    "financial:view", "shift:report", "transactions:history",
    "settings:manage", "db:maintenance", "users:manage"
]


# ══════════════════════════ 库存与商品 ══════════════════════════
class AutoPart(SQLModel, table=True):
    __tablename__ = "autopart"

    id: Optional[int] = Field(default=None, primary_key=True)
    oem: str = Field(index=True)
    name: str
    brand: str = Field(default="GENERAL")
    category: str = Field(default="未分类")
    stock: int = Field(default=0)
    price: float = Field(default=0.0)
    bin_location: Optional[str] = Field(default="Estante A-1")
    image_url: Optional[str] = Field(default="")
    cross_references: Optional[str] = Field(default="")
    compatible_models: Optional[str] = Field(default="")
    # 【新增】商品级税率配置：0.16 表示 16% 标准 IVA，0.0 表示免税 (Exento)
    tax_rate: float = Field(default=0.16)


class InventoryTransaction(SQLModel, table=True):
    __tablename__ = "inventorytransaction"

    id: Optional[int] = Field(default=None, primary_key=True)
    part_oem: str = Field(index=True)
    part_name: str
    type: str
    quantity: int
    unit_price: float
    total_amount: float
    customer_or_supplier: str
    timestamp: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M"))


# ══════════════════════════ 客户与挂账 ══════════════════════════
class Client(SQLModel, table=True):
    __tablename__ = "client"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    phone: Optional[str] = Field(default="")
    address: Optional[str] = Field(default="")
    rif_or_cedula: Optional[str] = Field(default="")
    client_type: Optional[str] = Field(default="Regular")
    debt: float = Field(default=0.0)
    credit_limit: float = Field(default=500.0)
    notes: Optional[str] = Field(default="")
    timestamp: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M"))


class ClientPaymentRecord(SQLModel, table=True):
    __tablename__ = "clientpaymentrecord"

    id: Optional[int] = Field(default=None, primary_key=True)
    client_name: str = Field(index=True)
    amount_usd: float
    payment_method: str
    reference_no: Optional[str] = Field(default="")
    notes: Optional[str] = Field(default="")
    timestamp: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M"))


# ══════════════════════════ 采购与供应商 ══════════════════════════
class Supplier(SQLModel, table=True):
    __tablename__ = "suppliers"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True, max_length=150)
    contact_person: Optional[str] = Field(default=None, max_length=100)
    phone: Optional[str] = Field(default=None, max_length=50)
    address: Optional[str] = Field(default=None)
    debt_usd: float = Field(default=0.0)
    updated_at: Optional[NaiveDatetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )

    purchase_orders: List["PurchaseOrder"] = Relationship(back_populates="supplier")


class PurchaseOrder(SQLModel, table=True):
    __tablename__ = "purchase_orders"

    id: Optional[int] = Field(default=None, primary_key=True)
    po_no: str = Field(index=True, unique=True, max_length=50)
    supplier_id: int = Field(foreign_key="suppliers.id")
    status: str = Field(default="PENDING", max_length=30)
    total_amount_usd: float = Field(default=0.0)
    items_json: str
    created_at: NaiveDatetime = Field(
        default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )
    received_at: Optional[NaiveDatetime] = Field(default=None)

    supplier: Optional[Supplier] = Relationship(back_populates="purchase_orders")


# ══════════════════════════ POS 销售订单 ══════════════════════════
# 委内瑞拉标准时区：UTC-4，确保开单时间精准对齐委内瑞拉当地自然天
_VENEZUELA_TZ = timezone(timedelta(hours=-4))


class Order(SQLModel, table=True):
    __tablename__ = "orders"
    __table_args__ = {"extend_existing": True}

    id: Optional[int] = Field(default=None, primary_key=True)
    order_no: str = Field(index=True, unique=True, max_length=50)
    client_name: str = Field(max_length=150)
    operator: str = Field(max_length=100)
    
    # 【新增】税务拆分总额字段
    base_amount_usd: float = Field(default=0.0)  # 不含税总额 (Base Imponible)
    tax_amount_usd: float = Field(default=0.0)   # 总 IVA 增值税额 (16% 或混合)
    igtf_amount_usd: float = Field(default=0.0)  # 3% 外汇/大额交易税 (如适用)
    
    total_usd: float  # 含税最终总额 (Base + Tax + IGTF)
    total_bs: float
    bcv_rate: float
    payment_method: str = Field(max_length=50)
    payment_reference: Optional[str] = Field(default=None, max_length=150)
    status: str = Field(default="COMPLETED", max_length=30)
    created_at: NaiveDatetime = Field(
        default_factory=lambda: datetime.now(_VENEZUELA_TZ).replace(tzinfo=None)
    )

    items: List["OrderItem"] = Relationship(
        back_populates="order",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class OrderItem(SQLModel, table=True):
    __tablename__ = "order_items"
    __table_args__ = {"extend_existing": True}

    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="orders.id")
    oem: str = Field(max_length=100)
    name: str = Field(max_length=150)
    quantity: int
    price_usd: float
    subtotal_usd: float  # 行总金额
    
    # 【新增】明细行税务快照（防止日后商品税率修改导致历史账目对不上）
    tax_rate: float = Field(default=0.16)     # 该行应用的税率（例如 0.16 或 0.0）
    base_subtotal_usd: float = Field(default=0.0)  # 该行不含税小计
    tax_subtotal_usd: float = Field(default=0.0)   # 该行税金小计

    order: Optional[Order] = Relationship(back_populates="items")


class OrderItem(SQLModel, table=True):
    __tablename__ = "order_items"
    __table_args__ = {"extend_existing": True}

    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="orders.id")
    oem: str = Field(max_length=100)
    name: str = Field(max_length=150)
    quantity: int
    price_usd: float
    subtotal_usd: float

    order: Optional[Order] = Relationship(back_populates="items")


# ══════════════════════════ 报价单 ══════════════════════════
class QuotationRecord(SQLModel, table=True):
    __tablename__ = "quotationrecord"

    id: Optional[int] = Field(default=None, primary_key=True)
    quotation_no: str = Field(index=True)
    client_name: str
    total_usd: float
    total_bs: float
    bcv_rate: float
    lang: str
    items_json: str
    timestamp: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M"))


# ══════════════════════════ 收银班结 ══════════════════════════
class CashRegisterSession(SQLModel, table=True):
    __tablename__ = "cashregistersession"

    id: Optional[int] = Field(default=None, primary_key=True)
    closed_at: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M"))
    operator: str = Field(default="Elias")
    bcv_rate_snapshot: float = Field(default=0.0)
    
    # 【新增】日结税务总账拆分（老板与财务对账核心）
    total_base_amount_usd: float = Field(default=0.0)  # 当班不含税销售总额 (Base Imponible)
    total_iva_amount_usd: float = Field(default=0.0)   # 当班代收增值税总额 (IVA 16%)
    total_igtf_amount_usd: float = Field(default=0.0)  # 当班代收外汇交易税总额 (IGTF 3%)

    system_cash_usd: float = Field(default=0.0)
    system_zelle: float = Field(default=0.0)
    system_pago_movil: float = Field(default=0.0)
    system_transfer_bs: float = Field(default=0.0)
    system_usdt: float = Field(default=0.0)
    actual_cash_usd: float = Field(default=0.0)
    actual_zelle: float = Field(default=0.0)
    actual_pago_movil: float = Field(default=0.0)
    actual_transfer_bs: float = Field(default=0.0)
    actual_usdt: float = Field(default=0.0)
    total_revenue_usd: float = Field(default=0.0)
    notes: Optional[str] = Field(default="")


# ══════════════════════════ 账号与审计 ══════════════════════════
class AdminUser(SQLModel, table=True):
    __tablename__ = "adminuser"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    password_hash: str
    role: str = Field(default="super_admin")
    timestamp: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M"))


class StaffUser(SQLModel, table=True):
    __tablename__ = "staffuser"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    password_hash: str
    role: str = Field(default="staff")
    permissions_json: str = Field(default="[]", sa_column=Column(Text))
    created_at: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M"))

    @property
    def permissions(self) -> list[str]:
        try:
            return json.loads(self.permissions_json)
        except Exception:
            return []

    @permissions.setter
    def permissions(self, perm_list: list[str]):
        self.permissions_json = json.dumps(perm_list)


class AuditLog(SQLModel, table=True):
    __tablename__ = "auditlog"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True)
    role: str = Field(default="staff")
    action: str
    details: str
    ip_address: Optional[str] = Field(default=None)
    created_at: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


class HeldOrder(SQLModel, table=True):
    __tablename__ = "held_orders"
    __table_args__ = {"extend_existing": True}

    id: Optional[int] = Field(default=None, primary_key=True)
    hold_no: str = Field(index=True)
    client_name: str
    payment_method: str
    items_json: str
    total_amount: float
    timestamp: str


__all__ = [
    "ALL_PERMISSIONS",
    "AutoPart",
    "InventoryTransaction",
    "Client",
    "ClientPaymentRecord",
    "Supplier",
    "PurchaseOrder",
    "Order",
    "OrderItem",
    "QuotationRecord",
    "CashRegisterSession",
    "AdminUser",
    "StaffUser",
    "AuditLog",
    "HeldOrder",
]