"""HTTP 请求体模型（Pydantic / SQLModel 校验层）。

只放"入参"，出参结构化由各路由内联字典负责，与重构前保持一致。
"""

from typing import List, Optional

from pydantic import BaseModel


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


# ──────────────────────────── 报价 / 开单 ────────────────────────────
class QuotationItemPayload(BaseModel):
    oem: str
    name: str
    brand: str
    quantity: int
    price: float


class CreateQuotationRequest(BaseModel):
    client_name: str = "Cliente General"
    lang: str = "es"
    payment_method: Optional[str] = "Cash_USD"
    payment_reference: Optional[str] = ""
    items: List[QuotationItemPayload]


# ──────────────────────────── 客户还款 ────────────────────────────
class ClientPaymentPayload(BaseModel):
    client_name: str
    amount_paid: float
    currency: str                    # 'USD' / 'BS' / 'USDT' ...
    payment_method: str
    reference_no: Optional[str] = ""
    notes: Optional[str] = ""


# ──────────────────────────── 采购收货 ────────────────────────────
class PurchaseItemPayload(BaseModel):
    oem: str
    name: str
    quantity: int
    unit_price: float


class CreatePurchaseOrderRequest(BaseModel):
    supplier_name: str
    items: List[PurchaseItemPayload]


# ──────────────────────────── POS 收银 ────────────────────────────
class POSItemPayload(BaseModel):
    oem: str
    name: str
    brand: Optional[str] = "GENERAL"
    quantity: int
    price: float


class POSOrderCreatePayload(BaseModel):
    client_name: str = "Cliente General"
    payment_method: str = "Cash_USD"
    payment_reference: Optional[str] = ""
    bcv_rate: float
    items: List[POSItemPayload]


# ──────────────────────────── 收银班结 ────────────────────────────
class CashRegisterCreatePayload(BaseModel):
    operator: str = "Elias"
    bcv_rate_snapshot: float = 0.0
    system_cash_usd: float = 0.0
    system_zelle: float = 0.0
    system_pago_movil: float = 0.0
    system_transfer_bs: float = 0.0
    system_usdt: float = 0.0
    actual_cash_usd: float = 0.0
    actual_zelle: float = 0.0
    actual_pago_movil: float = 0.0
    actual_transfer_bs: float = 0.0
    actual_usdt: float = 0.0
    total_revenue_usd: float = 0.0
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
