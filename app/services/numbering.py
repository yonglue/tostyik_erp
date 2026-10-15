"""单据号生成。

历史实现用 `datetime.now().strftime(...)` 只精确到秒，而
`purchase_orders.po_no` / `orders.order_no` 都带 UNIQUE 约束，
于是同一秒内创建两张单据就会
`IntegrityError: UNIQUE constraint failed` → 500。
（`order_no` 里的 `int(timestamp) % 1000` 也精确到秒，同样会撞。）

现改为三段拼接：

    PO-20261014-174201891-0001b7
       └ 日期    └ 时分秒+毫秒  └ 进程内序号+随机

* **毫秒** 解决"同一秒内连续建单"；
* **进程内序号** 解决"同一毫秒内并发建单"（同进程内保证不重复）；
* **随机字节** 解决"多 worker / 多副本各自计数"导致的跨进程碰撞。
"""

import secrets
import threading
from datetime import datetime
from itertools import count

_lock = threading.Lock()
_seq = count(1)


def _suffix() -> str:
    now = datetime.now()
    with _lock:
        n = next(_seq)
    return (
        f"{now.strftime('%Y%m%d-%H%M%S')}{now.microsecond // 1000:03d}"
        f"-{n % 10000:04d}{secrets.token_hex(1)}"
    )


def make_po_no() -> str:
    """采购单号，如 PO-20261014-174201891-0001b7"""
    return f"PO-{_suffix()}"


def make_order_no() -> str:
    """POS 订单号，如 POS-20261014-174201891-0002c4"""
    return f"POS-{_suffix()}"


def make_quotation_no() -> str:
    """报价单号，如 TK-20261014-174201891-0003d9

    该列没有 UNIQUE 约束，但重复单号会让对账与打印小票产生歧义，故一并加后缀。
    """
    return f"TK-{_suffix()}"
