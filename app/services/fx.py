"""服务端权威汇率（全项目唯一入口）。
任何把 Bs 折算成 USD 的业务，都只能调用此模块，绝不采信客户端传来的 exchange_rate。
"""
from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

from app.config import DEFAULT_BCV_RATE
from app.services.bcv import get_official_rate
from app.services.config_service import get_system_settings

CACHE_TTL_SECONDS = 300

_HARD_CURRENCIES = {"USD", "USDT"}
_BS_CURRENCIES = {"BS", "VES"}

_lock = threading.Lock()
_cached: RateSnapshot | None = None
_cached_at: float = 0.0


@dataclass(frozen=True)
class RateSnapshot:
    rate: Decimal
    source: str


def _manual_rate() -> Decimal | None:
    """从数据库获取手动配置的汇率"""
    try:
        settings = get_system_settings()
        rate = Decimal(str(settings.bcv_rate))
        return rate if rate > 0 else None
    except Exception as e:
        print(f"⚠️ 读取数据库汇率失败，将使用在线/兜底汇率: {e}")
        return None


def get_effective_rate(force_refresh: bool = False) -> RateSnapshot:
    global _cached, _cached_at

    now = time.monotonic()
    with _lock:
        if not force_refresh and _cached is not None and now - _cached_at < CACHE_TTL_SECONDS:
            return _cached

    manual = _manual_rate()
    if manual is not None:
        # 🌟 来源改成明确的 database_settings
        snapshot = RateSnapshot(manual.quantize(Decimal("0.0001")), "database_settings")
    else:
        official = Decimal(str(get_official_rate())).quantize(Decimal("0.0001"))
        fallback = Decimal(str(DEFAULT_BCV_RATE)).quantize(Decimal("0.0001"))
        snapshot = RateSnapshot(official, "fallback" if official == fallback else "dolarapi")

    with _lock:
        _cached, _cached_at = snapshot, time.monotonic()
    return snapshot


def to_usd(amount, currency: str) -> tuple[Decimal, RateSnapshot | None]:
    """把原币金额折算成 USD，返回 (金额, 用到的汇率快照)。"""
    cur = (currency or "USD").strip().upper()
    value = Decimal(str(amount))

    if cur in _HARD_CURRENCIES:
        return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP), None

    if cur in _BS_CURRENCIES:
        snapshot = get_effective_rate()
        if snapshot.rate <= 0:
            raise ValueError("当前汇率不可用，无法以玻利瓦尔结算")
        return (value / snapshot.rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP), snapshot

    raise ValueError(f"不支持的币种: {currency}")