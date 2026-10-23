"""Level 2 端到端：POS 开单 + 备份触发。"""
import sys
import uuid
import time
import sqlite3
import glob
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from sqlmodel import Session, select
from app.main import app
from app.database import engine
from app.models import AutoPart, Order, OrderItem, InventoryTransaction, AdminUser

TEST_OEM = "E2E-POS-L2"
results = []


def check(label, ok, detail=""):
    results.append((label, ok))
    print(f"  {'✅' if ok else '❌'} {label}" + (f"  ({detail})" if detail else ""))


def main():
    print("⚠️  确保已备份 tostiyk_erp.db\n")
    client = TestClient(app)

    # 1. 登录
    print("[1] 登录")
    r = client.post("/api/auth/login", json={"username": "admin", "password": "x"})
    if r.status_code != 200:
        print(f"❌ 登录失败 {r.status_code}: {r.text[:200]}")
        return 1
    token = r.json().get("access_token") or r.json().get("token")
    headers = {"Authorization": f"Bearer {token}"}
    check("登录成功", bool(token))

    # 2. 准备测试商品（SQL 插入，因为商品不是本轮改的重点）
    print("[2] 准备测试商品")
    with Session(engine) as s:
        old = s.exec(select(AutoPart).where(AutoPart.oem == TEST_OEM)).first()
        if old:
            s.delete(old); s.commit()
        part = AutoPart(
            name="E2E POS Test", oem=TEST_OEM, brand="GENERAL",
            stock=10, price=50.0, cost_price=30.0, category="Test",
        )
        s.add(part); s.commit(); s.refresh(part)
        part_id = part.id
    check("测试商品插入 stock=10", part_id is not None)

    # 3. POS 开单
    print("[3] POS 开单（数量 1，单价 50.00）")
    req_id = str(uuid.uuid4())
    r = client.post("/api/pos/orders", headers=headers, json={
        "client_name": "Cliente General",
        "payment_method": "Cash_USD",
        "bcv_rate": 40.00,
        "igtf_amount": 0,
        "request_id": req_id,
        "items": [{"oem": TEST_OEM, "name": "E2E POS Test", "brand": "GENERAL",
                   "quantity": 1, "price": 50.00}],
    })
    check("POS 创建订单", r.status_code in (200, 201), f"status={r.status_code}")
    if r.status_code not in (200, 201):
        print(f"   response: {r.text[:400]}")
        # 清理
        with Session(engine) as s:
            p = s.exec(select(AutoPart).where(AutoPart.oem == TEST_OEM)).first()
            if p: s.delete(p); s.commit()
        return 1
    order_resp = r.json()
    print(f"   response keys: {list(order_resp.keys())}")

    # 4. 验证订单 + 库存 + 流水
    print("[4] 验证落库")
    with Session(engine) as s:
        # 找刚才的订单：用 order_id 或 total 找
        order_id = order_resp.get("order_id") or order_resp.get("id")
        if not order_id:
            # 兜底：查最新订单
            o = s.exec(select(Order).order_by(Order.id.desc())).first()
            order_id = o.id if o else None
        order = s.get(Order, order_id) if order_id else None
        check("Order 存在", order is not None, f"id={order_id}")
        if order:
            check("Order.total_usd = 50.00", abs(float(order.total_usd) - 50.0) < 0.01,
                  f"total={order.total_usd}")
        item = s.exec(select(OrderItem).where(OrderItem.order_id == order_id)).first() if order_id else None
        check("OrderItem 存在", item is not None)
        part = s.exec(select(AutoPart).where(AutoPart.oem == TEST_OEM)).first()
        check("库存 10 → 9", part and part.stock == 9, f"stock={part.stock if part else 'N/A'}")
        tx = s.exec(select(InventoryTransaction).where(
            InventoryTransaction.part_oem == TEST_OEM)).first()
        check("InventoryTransaction 记录", tx is not None,
              f"type={tx.type if tx else 'N/A'}")

    # 5. 备份触发
    print("[5] 触发备份")
    before = set(glob.glob("backups/*.db"))
    r = client.post("/api/backup/trigger", headers=headers)
    check("备份触发", r.status_code == 200, f"status={r.status_code}")
    time.sleep(0.5)  # 等文件落盘
    after = set(glob.glob("backups/*.db"))
    new_files = after - before
    check("备份文件生成", len(new_files) > 0, f"new={list(new_files)[:1]}")
    if new_files:
        latest = list(new_files)[0]
        try:
            conn = sqlite3.connect(latest)
            cnt = conn.execute("SELECT COUNT(*) FROM suppliers").fetchone()[0]
            conn.close()
            check("备份可读", cnt >= 0, f"suppliers={cnt}")
        except Exception as ex:
            check("备份可读", False, str(ex)[:80])

    # 6. 清理
    print("[6] 清理测试数据")
    with Session(engine) as s:
        from sqlmodel import delete
        if order_id:
            s.exec(delete(OrderItem).where(OrderItem.order_id == order_id))
            s.exec(delete(Order).where(Order.id == order_id))
        s.exec(delete(InventoryTransaction).where(InventoryTransaction.part_oem == TEST_OEM))
        s.exec(delete(AutoPart).where(AutoPart.oem == TEST_OEM))
        s.commit()
    with Session(engine) as s:
        left = s.exec(select(AutoPart).where(AutoPart.oem == TEST_OEM)).first()
    check("测试数据清理", left is None)

    # 汇总
    passed = sum(1 for _, ok in results if ok)
    total = len(results)
    print(f"\n{'='*50}")
    print(f"结果：{passed}/{total} 通过")
    if passed != total:
        print("❌ 有失败项")
        return 1
    print("✅ Level 2 全部通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())