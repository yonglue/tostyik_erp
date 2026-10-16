"""全部数据表定义（统一 SQLModel）。

迁移说明
--------
历史上本项目存在两套并行的 ORM：

1. 根目录 ``models.py``（SQLAlchemy ``declarative_base``）定义了 ``products`` /
   ``suppliers`` / ``purchase_orders`` / ``inventory_transactions`` / ``orders`` /
   ``order_items`` / ``part_cross_references``；
2. ``main.py`` 内联的 SQLModel 表定义了 ``autopart`` / ``client`` /
   ``inventorytransaction`` 等。

两者指向同一个 SQLite 文件，但表名不同，造成了"三套库存流水表"的混乱。本文件把它们
统一为 SQLModel，并**逐字保留原有 __tablename__**，因此现有数据库无需任何数据迁移。

已删除的死表（在被删除前均为 0 行，且无任何路由引用）：
``products`` / ``part_cross_references`` / ``inventory_transactions``
（注意：真正在用的流水表是 ``inventorytransaction``，无下划线。）
"""

from datetime import datetime
from typing import List, Optional
import json

from pydantic import NaiveDatetime
from sqlmodel import Field, Relationship, SQLModel, Column, Text

# 说明：SQLModel 0.0.48 默认拒绝 naive datetime（要求带时区）。而本库历史数据全部是以
# "2026-10-13 06:23:37.238411" 形式存储的 naive UTC 时间，因此所有 datetime 字段统一
# 标注为 NaiveDatetime，保持读写格式与存量数据完全兼容。


# ══════════════════════════ 细粒度权限定义 ══════════════════════════
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
    """配件主表（原 main.py 内联定义，表名 autopart，是实际在用的一张表）。"""

    __tablename__ = "autopart"

    id: Optional[int] = Field(default=None, primary_key=True)
    oem: str = Field(index=True)                      # 原厂号 / 互换号
    name: str                                         # 配件名称
    brand: str = Field(default="GENERAL")             # 品牌
    category: str = Field(default="未分类")            # 分类
    stock: int = Field(default=0)                     # 总库存
    price: float = Field(default=0.0)                 # 销售单价 (USD)
    bin_location: Optional[str] = Field(default="Estante A-1")   # 货架库位
    image_url: Optional[str] = Field(default="")                 # 图片链接（JSON 数组字符串）
    cross_references: Optional[str] = Field(default="")          # 互换号 / 交叉参考
    compatible_models: Optional[str] = Field(default="")         # 适配车型矩阵


class InventoryTransaction(SQLModel, table=True):
    """库存出入库流水（表名 inventorytransaction，无下划线，138 行存量数据）。"""

    __tablename__ = "inventorytransaction"

    id: Optional[int] = Field(default=None, primary_key=True)
    part_oem: str = Field(index=True)
    part_name: str
    type: str                                         # "IN" / "OUT" / "PURCHASE_RECEIVE"
    quantity: int
    unit_price: float
    total_amount: float
    customer_or_supplier: str
    timestamp: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M"))


# ══════════════════════════ 客户与挂账 ══════════════════════════
class Client(SQLModel, table=True):
    """客户档案。"""

    __tablename__ = "client"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)                     # 客户名称 / 公司名
    phone: Optional[str] = Field(default="")          # 联系电话
    address: Optional[str] = Field(default="")        # 地址 / 城市
    rif_or_cedula: Optional[str] = Field(default="")  # 税号或身份证件 (RIF / Cédula)
    client_type: Optional[str] = Field(default="Regular")   # Regular / Taller / Mayorista
    debt: float = Field(default=0.0)                  # 当前欠款 (USD)
    credit_limit: float = Field(default=500.0)        # 信用额度上限 (USD)
    notes: Optional[str] = Field(default="")
    timestamp: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M"))


class ClientPaymentRecord(SQLModel, table=True):
    """客户还款流水。"""

    __tablename__ = "clientpaymentrecord"

    id: Optional[int] = Field(default=None, primary_key=True)
    client_name: str = Field(index=True)
    amount_usd: float                                 # 折合还款金额 (USD)
    payment_method: str
    reference_no: Optional[str] = Field(default="")
    notes: Optional[str] = Field(default="")
    timestamp: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M"))


# ══════════════════════════ 采购与供应商 ══════════════════════════
class Supplier(SQLModel, table=True):
    """供应商档案与应付账款。"""

    __tablename__ = "suppliers"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True, max_length=150)
    contact_person: Optional[str] = Field(default=None, max_length=100)
    phone: Optional[str] = Field(default=None, max_length=50)
    address: Optional[str] = Field(default=None)
    debt_usd: float = Field(default=0.0)
    updated_at: Optional[NaiveDatetime] = Field(default_factory=datetime.utcnow)

    purchase_orders: List["PurchaseOrder"] = Relationship(back_populates="supplier")


class PurchaseOrder(SQLModel, table=True):
    """采购订单与收货入库流转。"""

    __tablename__ = "purchase_orders"

    id: Optional[int] = Field(default=None, primary_key=True)
    po_no: str = Field(index=True, unique=True, max_length=50)
    supplier_id: int = Field(foreign_key="suppliers.id")
    status: str = Field(default="PENDING", max_length=30)   # PENDING / RECEIVED / CANCELLED
    total_amount_usd: float = Field(default=0.0)
    items_json: str                                          # 采购明细快照 (JSON)
    created_at: NaiveDatetime = Field(default_factory=datetime.utcnow)
    received_at: Optional[NaiveDatetime] = Field(default=None)

    supplier: Optional[Supplier] = Relationship(back_populates="purchase_orders")


# ══════════════════════════ POS 销售订单 ══════════════════════════
class Order(SQLModel, table=True):
    """POS 销售订单主表。"""

    __tablename__ = "orders"

    id: Optional[int] = Field(default=None, primary_key=True)
    order_no: str = Field(index=True, unique=True, max_length=50)
    client_name: str = Field(max_length=150)
    operator: str = Field(max_length=100)
    total_usd: float
    total_bs: float
    bcv_rate: float
    payment_method: str = Field(max_length=50)
    payment_reference: Optional[str] = Field(default=None, max_length=150)
    status: str = Field(default="COMPLETED", max_length=30)  # COMPLETED / REFUNDED
    created_at: NaiveDatetime = Field(default_factory=datetime.utcnow)

    items: List["OrderItem"] = Relationship(
        back_populates="order",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class OrderItem(SQLModel, table=True):
    """POS 销售订单明细。"""

    __tablename__ = "order_items"

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
    """报价 / 开单记录（PDF 快照）。"""

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
    """收银员交接班 / 日结记录。"""

    __tablename__ = "cashregistersession"

    id: Optional[int] = Field(default=None, primary_key=True)
    closed_at: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M"))
    operator: str = Field(default="Elias")
    bcv_rate_snapshot: float = Field(default=0.0)
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
    """管理员账号。"""

    __tablename__ = "adminuser"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    password_hash: str
    role: str = Field(default="super_admin")
    timestamp: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M"))


class StaffUser(SQLModel, table=True):
    """店员账号（支持细粒度权限存储）。"""

    __tablename__ = "staffuser"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    password_hash: str
    role: str = Field(default="staff")
    permissions_json: str = Field(default="[]", sa_column=Column(Text))  # 细粒度权限列表 JSON
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
    """操作审计日志。"""

    __tablename__ = "auditlog"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True)
    role: str = Field(default="staff")
    action: str
    details: str
    ip_address: Optional[str] = Field(default=None)
    created_at: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


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
]


class HeldOrder(SQLModel, table=True):
    __tablename__ = "held_orders"

    id: Optional[int] = Field(default=None, primary_key=True)
    hold_no: str = Field(index=True)  # 挂单编号，如 HOLD-17290001
    client_name: str                  # 客户名称
    payment_method: str               # 支付方式
    items_json: str                   # 购物车商品明细 JSON 串
    total_amount: float               # 订单总金额
    timestamp: str                    # 挂单时间文本



# ══════════════════════════ 收银交接班审计表 ══════════════════════════
class ShiftRecord(SQLModel, table=True):
    """收银员交接班盲盘点钞与盈亏审计记录。"""

    __tablename__ = "shift_records"

    id: Optional[int] = Field(default=None, primary_key=True)
    shift_no: str = Field(index=True)     # 班次流水号，如 SHIFT-17290001
    operator: str                         # 交班收银员
    start_time: str                       # 班次开始时间
    end_time: str                         # 交班时间
    
    # 系统统计值
    system_cash_usd: float                # 系统应收现金
    system_electronic_usd: float          # 系统电子支付（Zelle/PagoMovil）
    system_debt_usd: float                # 本班挂账
    system_total_usd: float               # 本班总营业额
    
    # 实盘与盈亏
    actual_cash_usd: float                # 实盘现金
    difference_usd: float                 # 现金盈亏差额
    notes: Optional[str] = Field(default="")  # 盈亏原因备注

