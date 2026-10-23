"""验证报价 → 订单标记的完整链路（真实建 Order + mark-converted）。"""
import sys
import uuid
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from sqlmodel import Session, select, delete
from app.main import app
from app.database import engine
from app.models import QuotationRecord, Order

results = []
def check(label, ok, detail=""):
    results.append(ok)
    print(f"  {'✅' if ok else '❌'} {label}" + (f"  ({detail})" if detail else ""))

def main():
    client = TestClient(app)
    r = client.post("/api/auth/login", json={"username": "admin", "password": "x"})
    token = r.json().get("access_token") or r.json().get("token")
    headers = {"Authorization": f"Bearer {token}"}

    suffix = uuid.uuid4().hex[:6]
    qno = f"TEST-Q-{suffix}"
    ono = f"TEST-POS-{suffix}"

    # 建测试报价单
    with Session(engine) as s:
        q = QuotationRecord(
            quotation_no=qno, client_name="Verify Client",
            total_usd=100.0, total_bs=4000.0, bcv_rate=40.0, lang="zh",
            items_json='[{"oem":"X","name":"T","quantity":1,"price":100}]'
        )
        s.add(q); s.commit(); s.refresh(q)
        qid = q.id

    # 建真实 Order（必填字段全填）
    with Session(engine) as s:
        o = Order(
            order_no=ono,
            client_name="Verify Client",
            operator="admin",
            total_usd=100.0,
            total_bs=4000.0,
            bcv_rate=40.0,
            payment_method="Cash_USD",
        )
        s.add(o); s.commit(); s.refresh(o)
        oid = o.id

    # 模拟前端下单成功后标记
    r = client.post(f"/api/quotations/{qid}/mark-converted", headers=headers,
                    json={"order_id": oid})
    check("mark-converted 200", r.status_code == 200, f"status={r.status_code}")

    # 验证库写入
    with Session(engine) as s:
        q = s.get(QuotationRecord, qid)
        check("converted_order_id 写入", q.converted_order_id == oid, f"val={q.converted_order_id}")
        check("converted_at 是 datetime", hasattr(q.converted_at, "year"),
              f"type={type(q.converted_at).__name__}")

    # 验证 GET /api/quotations 返回里带 converted_order_id（前端列表依赖这个）
    r = client.get("/api/quotations", headers=headers)
    rows = r.json()
    target = next((x for x in rows if x["id"] == qid), None)
    check("列表 API 返回 converted_order_id", target and target.get("converted_order_id") == oid,
          f"val={target.get('converted_order_id') if target else 'NOT FOUND'}")

    # 幂等
    r = client.post(f"/api/quotations/{qid}/mark-converted", headers=headers,
                    json={"order_id": 99999})
    check("幂等（第二次不覆盖）", r.json().get("status") == "already_converted")

    # 清理
    with Session(engine) as s:
        s.exec(delete(QuotationRecord).where(QuotationRecord.id == qid))
        s.exec(delete(Order).where(Order.id == oid))
        s.commit()

    passed, total = sum(results), len(results)
    print(f"\n{passed}/{total} 通过")
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())