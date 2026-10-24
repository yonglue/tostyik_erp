from fastapi.testclient import TestClient
from sqlmodel import Session, select
from app.models import AutoPart, Supplier
from decimal import Decimal

def create_test_part(session: Session, oem: str, stock: int, cost: float):
    part = AutoPart(
        oem=oem, name=f"测试件-{oem}", brand="GENERAL",
        stock=stock, price=100.0, cost_price=cost
    )
    session.add(part)
    session.commit()
    return part

def test_create_and_receive_po_via_api(client: TestClient, session: Session):
    """通过真实 API 测试：建单 -> 收货 -> 验证移动加权平均成本"""
    # 1. 准备初始数据：库存 10，成本 $10
    create_test_part(session, oem="TEST-001", stock=10, cost=10.0)
    
    supplier = Supplier(name="API测试供应商")
    session.add(supplier)
    session.commit()

    # 2. 发起 POST 请求：创建采购单 (进 10 个，单价 $20)
    po_payload = {
        "supplier_id": supplier.id,
        "supplier_name": supplier.name,
        "items": [
            {"oem": "TEST-001", "name": "测试件-001", "brand": "GENERAL", "quantity": 10, "unit_price": 20.0}
        ]
    }
    
    res = client.post("/api/purchase-orders", json=po_payload)
    assert res.status_code == 200, f"建单失败: {res.text}"
    po_id = res.json().get("po_id")

    # 3. 发起 POST 请求：确认收货
    receive_res = client.post(f"/api/purchase-orders/{po_id}/receive")
    assert receive_res.status_code == 200, f"收货失败: {receive_res.text}"

    # 4. 验证数据库：库存和成本是否精准联动
    session.expire_all() # 清除缓存，强制从数据库读取最新值
    part = session.exec(select(AutoPart).where(AutoPart.oem == "TEST-001")).first()
    
    # 预期库存 = 原库存 10 + 进货 10 = 20
    assert part.stock == 20
    
    # 预期成本 = (10 * 10 + 10 * 20) / 20 = 15.0
    assert part.cost_price == 15.0
    print(f"\n✅ API 集成测试通过：库存变更为 {part.stock}，加权成本变为 ${part.cost_price}")

def test_prevent_overselling_via_api(client: TestClient, session: Session):
    """通过真实 API 测试：库存不足时，手工出库接口必须拦截并返回 400"""
    # 1. 准备数据：库存只有 5 个
    create_test_part(session, oem="TEST-OVERSALE", stock=5, cost=10.0)

    # 2. 发起 POST 请求：尝试出库 10 个
    out_payload = {
        "type": "OUT",
        "part_oem": "TEST-OVERSALE",
        "part_name": "测试件-TEST-OVERSALE",
        "quantity": 10,
        "unit_price": 100.0,
        "customer_or_supplier": "测试客户"
    }
    
    res = client.post("/api/transactions", json=out_payload)
    
    # 3. 断言：接口必须返回 400 错误，且提示库存不足
    assert res.status_code == 400
    assert "库存不足" in res.json()["detail"]
    
    # 4. 断言：数据库里的库存必须还是 5（没有被扣减）
    session.expire_all()
    part = session.exec(select(AutoPart).where(AutoPart.oem == "TEST-OVERSALE")).first()
    assert part.stock == 5
    print(f"\n✅ 超卖拦截验证通过：HTTP 400 拦截成功，库存依然保持为 {part.stock}")
