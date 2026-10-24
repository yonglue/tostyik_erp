"""全部数据表定义（统一 SQLModel）。"""

from datetime import datetime, timezone, timedelta
from typing import List, Optional
import json

from pydantic import NaiveDatetime
from sqlalchemy import Index
from sqlmodel import Field, Relationship, SQLModel, Column, Text

# 细粒度权限定义
ALL_PERMISSIONS = [
    "pos:access", "pos:checkout", "pos:refund", "pos:hold", "pos:discount",
    "parts:view", "parts:manage", "parts:import",
    "clients:view", "clients:manage", "fiado:pay",
    "quotations:export", "procurement:view",
    "financial:view", "shift:report", "transactions:history",
    "settings:manage", "db:maintenance", "users:manage"
]


# ══════════════════════════ 库存与商品 ══════════════════════════
class AutoPart(SQLModel, table=True):
    # 同一 OEM 允许存在多个品牌，但 (oem, brand) 必须唯一，
    # 否则按 oem 批量改库存会一次误改所有品牌行。
    __table_args__ = (
        Index("uq_autopart_oem_brand", "oem", "brand", unique=True),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    oem: str = Field(index=True)
    name: str
    brand: str = Field(default="GENERAL")
    category: str = Field(default="未分类")
    stock: int = Field(default=0)
    price: float = Field(default=0.0)
    cost_price: float = Field(default=0.0)
    bin_location: str = Field(default="Estante A-1")
    image_url: str = Field(default="")
    cross_references: str = Field(default="")
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
    store_name: Optional[str] = Field(default=None)
    phone: Optional[str] = Field(default="")
    address: Optional[str] = Field(default="")
    rif_or_cedula: Optional[str] = Field(default="")
    client_type: Optional[str] = Field(default="Regular")
    debt: float = Field(default=0.0)
    credit_limit: float = Field(default=500.0)
    notes: Optional[str] = Field(default="")
    
    # 🌟 新增：是否为 SENIAT 特殊纳税人（需代扣 IVA）
    is_special_taxpayer: bool = Field(default=False)
    
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
    payment_terms: int = Field(default=30)          # 账期天数（0=即付）
    credit_limit: float = Field(default=5000.0)       # 信用额度（0=不限）
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
_VENEZUELA_TZ = timezone(timedelta(hours=-4))


class Order(SQLModel, table=True):
    __tablename__ = "orders"
    __table_args__ = {"extend_existing": True}

    id: Optional[int] = Field(default=None, primary_key=True)
    order_no: str = Field(index=True, unique=True, max_length=50)
    client_name: str = Field(max_length=150)
    # 精确指向挂账客户；老订单可能为空，退款时才回退到按姓名匹配
    client_id: Optional[int] = Field(default=None, index=True)
    # 幂等键：同一 request_id 只会创建一张订单（SQLite 允许多个 NULL）
    request_id: Optional[str] = Field(default=None, unique=True, index=True, max_length=64)
    operator: str = Field(max_length=100)
    
    base_amount_usd: float = Field(default=0.0)
    tax_amount_usd: float = Field(default=0.0)
    igtf_amount_usd: float = Field(default=0.0)
    
    total_usd: float
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
    part_id: Optional[int] = Field(default=None, index=True)
    oem: str = Field(max_length=100)
    name: str = Field(max_length=150)
    quantity: int
    price_usd: float
    subtotal_usd: float
    
    # 🌟 新增：卖出那一刻的商品真实成本快照
    cost_price_usd: float = Field(default=0.0) 

    tax_rate: float = Field(default=0.16)
    base_subtotal_usd: float = Field(default=0.0)
    tax_subtotal_usd: float = Field(default=0.0)

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
    converted_order_id: Optional[int] = Field(default=None)
    converted_at: Optional[NaiveDatetime] = Field(default=None)


# ══════════════════════════ 收银班结 ══════════════════════════
class CashRegisterSession(SQLModel, table=True):
    __tablename__ = "cashregistersession"

    id: Optional[int] = Field(default=None, primary_key=True)
    closed_at: str = Field(default_factory=lambda: datetime.now(_VENEZUELA_TZ).strftime("%Y-%m-%d %H:%M"))
    operator: str = Field(default="Elias")
    bcv_rate_snapshot: float = Field(default=0.0)
    
    total_base_amount_usd: float = Field(default=0.0)
    total_iva_amount_usd: float = Field(default=0.0)
    total_igtf_amount_usd: float = Field(default=0.0)

    system_cash_usd: float = Field(default=0.0)
    system_zelle: float = Field(default=0.0)
    system_pago_movil: float = Field(default=0.0)   # Bs
    system_transfer_bs: float = Field(default=0.0)  # Bs
    system_usdt: float = Field(default=0.0)
    system_card_pos: float = Field(default=0.0)     # Bs
    system_cash_bs: float = Field(default=0.0)      # Bs
    actual_cash_usd: float = Field(default=0.0)
    actual_zelle: float = Field(default=0.0)
    actual_pago_movil: float = Field(default=0.0)   # Bs
    actual_transfer_bs: float = Field(default=0.0)  # Bs
    actual_usdt: float = Field(default=0.0)
    actual_card_pos: float = Field(default=0.0)     # Bs
    actual_cash_bs: float = Field(default=0.0)      # Bs
    total_revenue_usd: float = Field(default=0.0)
    notes: Optional[str] = Field(default="")


# ══════════════════════════ 日常开支 (Gastos) ══════════════════════════
class Expense(SQLModel, table=True):
    __tablename__ = "expenses"

    id: Optional[int] = Field(default=None, primary_key=True)
    category: str = Field(index=True, max_length=50) # 分类：房租、水电、工资、物流等
    description: str = Field(default="", max_length=255) # 详细说明
    amount: float = Field(default=0.0) # 金额
    currency: str = Field(default="USD", max_length=10) # 币种：USD 或 BS
    exchange_rate: float = Field(default=1.0) # 如果是 BS，记录当时的汇率
    payment_method: str = Field(default="Cash_USD", max_length=50) # 现金、转账、刷卡等
    receipt_url: str = Field(default="") # 凭证图片路径 (预留)
    created_by: str = Field(default="Admin", max_length=50) # 经办人
    expense_date: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d")) # 支出日期
    created_at: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))



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

class SupplierPaymentRecord(SQLModel, table=True):
    __tablename__ = "supplierpaymentrecord"

    id: Optional[int] = Field(default=None, primary_key=True)
    supplier_id: int = Field(foreign_key="suppliers.id", index=True)
    supplier_name: str
    amount_usd: float
    currency: str = Field(default="USD")  # 记录原币种
    original_amount: float = Field(default=0.0)  # 原币金额
    exchange_rate: float = Field(default=1.0)  # 当时的汇率
    payment_method: str
    reference_no: Optional[str] = Field(default="")
    notes: Optional[str] = Field(default="")
    created_at: NaiveDatetime = Field(
        default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )

class SystemSettings(SQLModel, table=True):
    __tablename__ = "system_settings"
    
    id: int = Field(default=1, primary_key=True) # 强制单行表
    company_name: str = Field(default="TOSTIYK (TK) - AUTOPARTES VENEZUELA")
    rif: str = Field(default="J-00000000-0")
    address: str = Field(default="Valera, Estado Trujillo, Venezuela")
    phone: str = Field(default="+58 412-0000000")
    email: str = Field(default="tostiyk.ventas@gmail.com")
    bcv_rate: float = Field(default=36.50)


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
    "Expense",
    "SystemSettings",
]



