"""HTTP 请求体模型（Pydantic / SQLModel 校验层）。

只放"入参"，出参结构化由各路由内联字典负责，与重构前保持一致。
"""

from typing import List, Optional
from pydantic import BaseModel, Field, condecimal
from decimal import Decimal

# 🌟 定义通用金额与汇率精度类型
# 金额最大 12 位，保留 2 位小数（例如：9999999999.99）
MoneyType = condecimal(max_digits=12, decimal_places=2)
# 汇率最大 10 位，保留 4 位小数（例如：36.5432）
RateType = condecimal(max_digits=10, decimal_places=4)

# POS / 班结入参的防呆约束：
# 单价必须 > 0；金额不得为负；汇率必须 > 0。
PositiveMoney = condecimal(max_digits=12, decimal_places=2, gt=0)
NonNegativeMoney = condecimal(max_digits=12, decimal_places=2, ge=0)
PositiveRate = condecimal(max_digits=10, decimal_places=4, gt=0)


# ──────────────────────────── 鉴权 / 员工 ────────────────────────────
class LoginPayload(BaseModel):
    username: str
    password: str


class ResetPasswordPayload(BaseModel):
    security_pin: str


class CreateStaffPayload(BaseModel):
    username: str
    password: str
    role: str = "staff"
    # 🌟 补全字段：允许前端传入权限数组
    permissions: List[str] = [] 


# ──────────────────────────── 报价 / 开单 ────────────────────────────
class QuotationItemPayload(BaseModel):
    oem: str
    name: str
    brand: str
    quantity: int
    price: MoneyType


class CreateQuotationRequest(BaseModel):
    client_name: Optional[str] = "Cliente General"
    lang: Optional[str] = "es"
    payment_method: Optional[str] = "Cash_USD"
    payment_reference: Optional[str] = ""
    items: List[QuotationItemPayload]


# ──────────────────────────── 客户还款 ────────────────────────────
class ClientPaymentPayload(BaseModel):
    client_name: str
    amount_paid: MoneyType
    currency: str                    # 'USD' / 'BS' / 'USDT' ...
    payment_method: str
    reference_no: Optional[str] = ""
    notes: Optional[str] = ""


# ──────────────────────────── 采购收货 ────────────────────────────
class PurchaseItemPayload(BaseModel):
    oem: str = Field(min_length=1, max_length=100)
    name: str = Field(min_length=1, max_length=150)
    brand: Optional[str] = Field(default=None, max_length=50)
    # 数量必须为正整数：防止负数让收货变成减库存
    quantity: int = Field(gt=0, le=1_000_000)
    # 进价必须 > 0：防止 0 元或负数入库污染加权成本
    unit_price: PositiveMoney


class CreatePurchaseOrderRequest(BaseModel):
    supplier_name: str = Field(max_length=150)
    po_no: Optional[str] = Field(default=None, max_length=50)
    items: List[PurchaseItemPayload] = Field(min_length=1)


# ──────────────────────────── 供应商付款 ────────────────────────────
class SupplierPaymentPayload(BaseModel):
    amount_paid: MoneyType
    currency: str = "USD"
    exchange_rate: Optional[PositiveRate] = None
    payment_method: str = "Cash_USD"
    reference_no: Optional[str] = ""
    notes: Optional[str] = ""


# ──────────────────────────── POS 收银 ────────────────────────────
class POSItemPayload(BaseModel):
    oem: str
    name: str
    brand: Optional[str] = "GENERAL"
    quantity: int = Field(gt=0)  # 0 / 负数直接 422
    price: PositiveMoney  # 单价必须 > 0，负数/0 元单直接 422


class POSOrderCreatePayload(BaseModel):
    client_name: str = "Cliente General"
    client_id: Optional[int] = None # 🌟 新增：如果前端选了客户，传ID过来，防同名挂错账
    payment_method: str = "Cash_USD"
    payment_reference: Optional[str] = ""
    bcv_rate: PositiveRate  # 汇率必须 > 0
    # 前端算好 IGTF 传过来，后端只做上限校验，不再写死 3%
    igtf_amount: NonNegativeMoney = Decimal("0.00")
    # 幂等键：前端一次结算生成一个 UUID，重试时复用
    request_id: Optional[str] = Field(default=None, max_length=64)
    items: List[POSItemPayload]


class HeldOrderCreatePayload(BaseModel):
    """云端挂单入参。items 不能为空，金额由后端按明细计算。"""

    client_name: str = "Cliente General"
    payment_method: str = "Cash_USD"
    items: List[POSItemPayload] = Field(min_length=1)


# ──────────────────────────── 收银班结 ────────────────────────────
class ShiftHandoverPayload(BaseModel):
    """交接班归档入参。

    币种后缀是强制约定，避免再把 Bs 金额写进 *_usd 字段：
      * `*_usd` / `*_usdt_usd`：美元金额
      * `*_bs`：玻利瓦尔金额
    """

    bcv_rate: PositiveRate

    system_base_amount_usd: NonNegativeMoney
    system_tax_amount_usd: NonNegativeMoney
    system_igtf_amount_usd: NonNegativeMoney

    system_card_pos_bs: NonNegativeMoney
    system_pago_movil_bs: NonNegativeMoney
    system_cash_bs: NonNegativeMoney
    system_cash_usd: NonNegativeMoney
    system_zelle_usd: NonNegativeMoney
    system_transfer_bs: NonNegativeMoney
    system_usdt_usd: NonNegativeMoney
    system_total_usd: NonNegativeMoney

    actual_card_pos_bs: NonNegativeMoney
    actual_pago_movil_bs: NonNegativeMoney
    actual_cash_bs: NonNegativeMoney
    actual_cash_usd: NonNegativeMoney
    actual_zelle_usd: NonNegativeMoney
    actual_transfer_bs: NonNegativeMoney
    actual_usdt_usd: NonNegativeMoney

    notes: str = ""


class CashRegisterCreatePayload(BaseModel):
    operator: str = "Elias"
    bcv_rate_snapshot: RateType = Decimal("0.0000")
    system_cash_usd: MoneyType = Decimal("0.00")
    system_zelle: MoneyType = Decimal("0.00")
    system_pago_movil: MoneyType = Decimal("0.00")
    system_transfer_bs: MoneyType = Decimal("0.00")
    system_usdt: MoneyType = Decimal("0.00")
    actual_cash_usd: MoneyType = Decimal("0.00")
    actual_zelle: MoneyType = Decimal("0.00")
    actual_pago_movil: MoneyType = Decimal("0.00")
    actual_transfer_bs: MoneyType = Decimal("0.00")
    actual_usdt: MoneyType = Decimal("0.00")
    total_revenue_usd: MoneyType = Decimal("0.00")
    notes: Optional[str] = ""


__all__ = [
    "LoginPayload",
    "ResetPasswordPayload",
    "CreateStaffPayload",
    "QuotationItemPayload",
    "CreateQuotationRequest",
    "ClientPaymentPayload",
    "PurchaseItemPayload",
    "CreatePurchaseOrderRequest",
    "SupplierPaymentPayload", # 🌟 新增
    "POSItemPayload",
    "POSOrderCreatePayload",
    "HeldOrderCreatePayload",
    "ShiftHandoverPayload",
    "CashRegisterCreatePayload",
    "PositiveMoney",
    "NonNegativeMoney",
    "PositiveRate",
]