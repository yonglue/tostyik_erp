"""HTTP 请求体模型（Pydantic / SQLModel 校验层）。

只放"入参"，出参结构化由各路由内联字典负责，与重构前保持一致。
"""

from typing import List, Optional
from pydantic import BaseModel, condecimal
from decimal import Decimal

# 🌟 定义通用金额与汇率精度类型
# 金额最大 12 位，保留 2 位小数（例如：9999999999.99）
MoneyType = condecimal(max_digits=12, decimal_places=2)
# 汇率最大 10 位，保留 4 位小数（例如：36.5432）
RateType = condecimal(max_digits=10, decimal_places=4)


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
    price: MoneyType # 🌟 改


class CreateQuotationRequest(BaseModel):
    client_name: Optional[str] = "Cliente General"
    lang: Optional[str] = "es"
    payment_method: Optional[str] = "Cash_USD"
    payment_reference: Optional[str] = ""
    items: List[QuotationItemPayload]


# ──────────────────────────── 客户还款 ────────────────────────────
class ClientPaymentPayload(BaseModel):
    client_name: str
    amount_paid: MoneyType # 🌟 改
    currency: str                    # 'USD' / 'BS' / 'USDT' ...
    payment_method: str
    reference_no: Optional[str] = ""
    notes: Optional[str] = ""


# ──────────────────────────── 采购收货 ────────────────────────────
class PurchaseItemPayload(BaseModel):
    oem: str
    name: str
    quantity: int
    unit_price: MoneyType # 🌟 改


class CreatePurchaseOrderRequest(BaseModel):
    supplier_name: str
    items: List[PurchaseItemPayload]


# ──────────────────────────── POS 收银 ────────────────────────────
class POSItemPayload(BaseModel):
    oem: str
    name: str
    brand: Optional[str] = "GENERAL"
    quantity: int
    price: MoneyType # 🌟 改


class POSOrderCreatePayload(BaseModel):
    client_name: str = "Cliente General"
    client_id: Optional[int] = None # 🌟 新增：如果前端选了客户，传ID过来，防同名挂错账
    payment_method: str = "Cash_USD"
    payment_reference: Optional[str] = ""
    bcv_rate: RateType # 🌟 改
    # 🌟 新增：前端算好 IGTF 传过来，后端不再写死 3%
    igtf_amount: MoneyType = Decimal("0.00") 
    items: List[POSItemPayload]


# ──────────────────────────── 收银班结 ────────────────────────────
class CashRegisterCreatePayload(BaseModel):
    operator: str = "Elias"
    bcv_rate_snapshot: RateType = Decimal("0.0000") # 🌟 改
    system_cash_usd: MoneyType = Decimal("0.00") # 🌟 改
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
    "POSItemPayload",
    "POSOrderCreatePayload",
    "CashRegisterCreatePayload",
]