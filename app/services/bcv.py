"""BCV / 官方汇率获取。"""
import re
import requests
from bs4 import BeautifulSoup
from curl_cffi import requests as crequests
from app.config import (
    BCV_API_TIMEOUT, BCV_API_URL, BCV_SCRAPE_TIMEOUT, BCV_SCRAPE_URL, DEFAULT_BCV_RATE,
)

def get_official_rate(default: float = DEFAULT_BCV_RATE) -> float:
    """从 dolarapi 取官方汇率；失败时返回 default。"""
    try:
        res = requests.get(BCV_API_URL, timeout=BCV_API_TIMEOUT)
        if res.status_code == 200:
            value = res.json().get("promedio")
            if value is not None:
                return round(float(value), 2) # 🌟 保留 2 位小数
    except Exception as e:
        print(f"官方汇率接口异常，使用兜底值 {default}: {e}")
    return round(default, 2)

def scrape_bcv_rate() -> dict:
    """实时抓取 BCV 官网汇率。"""
    try:
        response = crequests.get(
            BCV_SCRAPE_URL, timeout=BCV_SCRAPE_TIMEOUT, impersonate="chrome110", verify=False,
        )
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            usd_div = soup.find("div", id="dolar")
            if usd_div:
                strong_tag = usd_div.find("strong")
                if strong_tag:
                    rate_text = strong_tag.text.strip().replace(",", ".")
                    return {
                        "rate": round(float(rate_text), 2), # 🌟 保留 2 位小数
                        "source": "BCV Live Official (curl_cffi)",
                    }
            match = re.search(r"USD.*?([0-9]+[.,][0-9]+)", response.text)
            if match:
                return {
                    "rate": round(float(match.group(1).replace(",", ".")), 2), # 🌟 保留 2 位小数
                    "source": "BCV Regex Match",
                }
    except Exception as e:
        print(f"BCV 自动抓取异常: {e}")
    return {"rate": round(DEFAULT_BCV_RATE, 2), "source": "Fallback Cache"}