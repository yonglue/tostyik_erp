"""验证报价转订单标记。"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from sqlmodel import Session, select, delete
from app.main import app
from app.database import engine
from app.models import QuotationRecord

results = []
def check(label, ok, detail=""):
    results.append(ok)
    print(f"  {'✅' if ok else '❌'} {label}" + (f"  ({detail})" if detail else ""))

def main():
    client = TestClient(app)
    r = client.post("/api/auth/login", json={"username": "admin", "password": "x"})
    token = r.json().get("access_token") or r.json().get("token")
    headers = {"Authorization": f"Bearer {token}"}

    # 建测试报价单
    with Session(engine) as s:
        q = QuotationRecord(
            quotation_no="TEST-Q-CONV", client_name="Test Client",
            total_usd=100.0, total_bs=4000.0, bcv_rate=40.0, lang="zh",
            items_json='[{"oem":"X","name":"T","quantity":1,"price":100}]'
        )
        s.add(q); s.commit(); s.refresh(q)
        qid = q.id

    oid = 99999  # 假 order_id，仅测试标记逻辑

    # 标记转换
    r = client.post(f"/api/quotations/{qid}/mark-converted", headers=headers,
                    json={"order_id": oid})
    check("mark-converted 200", r.status_code == 200, f"status={r.status_code}")

    with Session(engine) as s:
        q = s.get(QuotationRecord, qid)
        check("converted_order_id 写入", q.converted_order_id == oid, f"val={q.converted_order_id}")
        check("converted_at 是 datetime", hasattr(q.converted_at, "year"),
              f"type={type(q.converted_at).__name__}")

    # 幂等
    r = client.post(f"/api/quotations/{qid}/mark-converted", headers=headers,
                    json={"order_id": 88888})
    check("幂等（第二次不覆盖）", r.json().get("status") == "already_converted")

    # 清理
    with Session(engine) as s:
        s.exec(delete(QuotationRecord).where(QuotationRecord.id == qid))
        s.commit()

    passed, total = sum(results), len(results)
    print(f"\n{passed}/{total} 通过")
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())