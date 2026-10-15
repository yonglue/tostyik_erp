"""BCV / 官方汇率获取。

重构前这段"requests.get(dolarapi) + try/except pass"在 main.py 里被复制了 4 次，
现已统一到本模块。
"""

import re

import requests
from bs4 import BeautifulSoup
from curl_cffi import requests as crequests

from app.config import (
    BCV_API_TIMEOUT,
    BCV_API_URL,
    BCV_SCRAPE_TIMEOUT,
    BCV_SCRAPE_URL,
    DEFAULT_BCV_RATE,
)


def get_official_rate(default: float = DEFAULT_BCV_RATE) -> float:
    """从 dolarapi 取官方汇率；失败时返回 default（默认沿用旧硬编码兜底值）。"""
    try:
        res = requests.get(BCV_API_URL, timeout=BCV_API_TIMEOUT)
        if res.status_code == 200:
            value = res.json().get("promedio")
            if value is not None:
                return float(value)
    except Exception as e:  # noqa: BLE001 - 外网不可用时必须降级而非报错
        print(f"官方汇率接口异常，使用兜底值 {default}: {e}")
    return default


def scrape_bcv_rate() -> dict:
    """实时抓取 BCV 官网汇率（带 curl_cffi 指纹伪装），失败时回落到兜底值。"""
    try:
        response = crequests.get(
            BCV_SCRAPE_URL,
            timeout=BCV_SCRAPE_TIMEOUT,
            impersonate="chrome110",
            verify=False,
        )
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            usd_div = soup.find("div", id="dolar")
            if usd_div:
                strong_tag = usd_div.find("strong")
                if strong_tag:
                    rate_text = strong_tag.text.strip().replace(",", ".")
                    return {
                        "rate": float(rate_text),
                        "source": "BCV Live Official (curl_cffi)",
                    }
            match = re.search(r"USD.*?([0-9]+[.,][0-9]+)", response.text)
            if match:
                return {
                    "rate": float(match.group(1).replace(",", ".")),
                    "source": "BCV Regex Match",
                }
    except Exception as e:  # noqa: BLE001 - 抓取失败走兜底
        print(f"BCV 自动抓取异常: {e}")
    return {"rate": DEFAULT_BCV_RATE, "source": "Fallback Cache"}
