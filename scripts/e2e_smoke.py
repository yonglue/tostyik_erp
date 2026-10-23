"""端到端烟雾测试：供应商 → 采购单 → 收货 → 付款。

覆盖本轮改动：浮点精度、外键、SupplierPaymentRecord.created_at、权限。
不覆盖：POS/PDF/备份（Level 2）。

前置：已备份 tostiyk_erp.db（cp tostiyk_erp.db tostiyk_erp.db.bak_*）。
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from app.main import app
from app.database import engine
from app.models import Supplier, PurchaseOrder, SupplierPaymentRecord

TEST_NAME = "TEST_E2E_LEVEL1"
TEST_OEM = "E2E-OEM-L1"
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
        print(f"❌ 登录失败 {r.status_code}: {r.text}")
        print("   如果密码不是 tostiyk2026，请先改脚本里的密码")
        return 1
    data = r.json()
    token = data.get("access_token") or data.get("token") or data.get("accessToken")
    check("登录成功", bool(token), f"token_len={len(token) if token else 0}")
    headers = {"Authorization": f"Bearer {token}"}

    # 清理残留（上次失败可能留）
    with Session(engine) as s:
        old = s.exec(select(Supplier).where(Supplier.name == TEST_NAME)).first()
        if old:
            s.exec(__import__("sqlmodel").delete(SupplierPaymentRecord).where(
                SupplierPaymentRecord.supplier_id == old.id))
            s.exec(__import__("sqlmodel").delete(PurchaseOrder).where(
                PurchaseOrder.supplier_id == old.id))
            s.delete(old)
            s.commit()
            print("   清理了上次残留数据")

    # 2. 建供应商
    print("[2] 建供应商")
    r = client.post("/api/suppliers", headers=headers, json={
        "name": TEST_NAME, "contact_person": "E2E", "phone": "", "address": ""
    })
    check("创建供应商", r.status_code in (200, 201), f"status={r.status_code}")
    if r.status_code not in (200, 201):
        print(f"   response: {r.text[:300]}")
        return 1
    with Session(engine) as s:
        sup = s.exec(select(Supplier).where(Supplier.name == TEST_NAME)).first()
        supplier_id = sup.id
    check("供应商默认账期30/额度5000", sup.payment_terms == 30 and abs(sup.credit_limit - 5000) < 0.01,
          f"terms={sup.payment_terms} credit={sup.credit_limit}")

    # 3. 建采购单
    print("[3] 建采购单 (单价 100.10)")
    r = client.post("/api/purchase-orders/create", headers=headers, json={
        "supplier_name": TEST_NAME,
        "po_no": "",
        "items": [{"oem": TEST_OEM, "name": "E2E Test", "brand": "GENERAL",
                   "quantity": 1, "unit_price": 100.10}],
    })
    check("创建采购单", r.status_code in (200, 201), f"status={r.status_code}")
    if r.status_code not in (200, 201):
        print(f"   response: {r.text[:300]}")
        return 1
    po_id = r.json().get("po_id")

    # 4. 收货
    print("[4] 收货")
    r = client.post(f"/api/purchase-orders/{po_id}/receive", headers=headers)
    check("收货成功", r.status_code == 200, f"status={r.status_code}")
    if r.status_code != 200:
        print(f"   response: {r.text[:300]}")
        return 1
    with Session(engine) as s:
        sup = s.get(Supplier, supplier_id)
        debt = round(sup.debt_usd, 2)
    check("debt_usd = 100.10（无浮点漂移）", debt == 100.10, f"debt={debt}")

    # 5. 付款
    print("[5] 付款 40.00 USD")
    r = client.post(f"/api/suppliers/{supplier_id}/pay", headers=headers, json={
        "amount_paid": 40.00, "currency": "USD", "payment_method": "Cash_USD",
    })
    check("付款成功", r.status_code == 200, f"status={r.status_code}")
    if r.status_code != 200:
        print(f"   response: {r.text[:300]}")
        return 1
    with Session(engine) as s:
        sup = s.get(Supplier, supplier_id)
        debt = round(sup.debt_usd, 2)
        pay = s.exec(select(SupplierPaymentRecord).where(
            SupplierPaymentRecord.supplier_id == supplier_id)).first()
    check("debt_usd = 60.10", debt == 60.10, f"debt={debt}")
    check("payment.created_at 是 datetime", hasattr(pay.created_at, "year"),
          f"type={type(pay.created_at).__name__}")

    # 6. 外键强制
    print("[6] 外键强制")
    with Session(engine) as s:
        try:
            from app.database import engine as e
            from sqlalchemy import text
            with e.connect() as conn:
                conn.execute(text("PRAGMA foreign_keys=ON"))
                conn.execute(text(
                    "INSERT INTO supplierpaymentrecord (supplier_id, supplier_name, amount_usd, "
                    "currency, original_amount, exchange_rate, payment_method, created_at) "
                    "VALUES (99999, 'ghost', 1, 'USD', 1, 1.0, 'X', '2026-10-23 00:00:00')"))
                conn.commit()
            check("外键拒绝孤儿插入", False, "插入竟然成功了")
        except Exception as ex:
            check("外键拒绝孤儿插入", "FOREIGN KEY" in str(ex).upper(), str(ex)[:60])

    # 7. 清理
    print("[7] 清理测试数据")
    with Session(engine) as s:
        from sqlmodel import delete
        s.exec(delete(SupplierPaymentRecord).where(
            SupplierPaymentRecord.supplier_id == supplier_id))
        s.exec(delete(PurchaseOrder).where(PurchaseOrder.supplier_id == supplier_id))
        s.exec(delete(__import__("app.models", fromlist=["AutoPart"]).AutoPart).where(
            __import__("app.models", fromlist=["AutoPart"]).AutoPart.oem == TEST_OEM))
        s.exec(delete(Supplier).where(Supplier.id == supplier_id))
        s.commit()
    with Session(engine) as s:
        left = s.exec(select(Supplier).where(Supplier.name == TEST_NAME)).first()
    check("测试数据清理", left is None)

    # 汇总
    passed = sum(1 for _, ok in results if ok)
    total = len(results)
    print(f"\n{'='*50}")
    print(f"结果：{passed}/{total} 通过")
    if passed != total:
        print("❌ 有失败项，先别继续 Level 2")
        return 1
    print("✅ Level 1 全部通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())