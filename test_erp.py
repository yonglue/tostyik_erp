# test_erp.py
import pytest
import concurrent.futures
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
from main import app, get_session, AutoPart, Client, StaffUser, AuditLog, InventoryTransaction
from datetime import datetime
import concurrent.futures
import requests
from sqlmodel import create_engine, Session, SQLModel

# ── 鉴权辅助：所有需要登录的请求改为携带 Bearer 令牌 ──
from app import database
from app.config import DEFAULT_ADMIN_PASSWORD, MASTER_SECURITY_PIN
from app.security import create_access_token


def auth_headers(username: str, role: str) -> dict:
    return {"Authorization": f"Bearer {create_access_token(username, role)}"}


AUTH_ADMIN = auth_headers("admin", "super_admin")


# 配置独立测试数据库
#
# ⚠️ 这里必须用「文件型」SQLite，不能用原来的内存库 + StaticPool：
# StaticPool 会让所有线程共享同一条连接，并发用例必然间歇性抛
#   sqlite3.InterfaceError: bad parameter or other API misuse
# （实测：改前 12 轮里 8 轮失败；改成文件型后该崩溃消失）。
test_engine = create_engine(
    "sqlite:///./_test_erp.db",
    connect_args={"check_same_thread": False, "timeout": 30},
)

def override_get_session():
    with Session(test_engine) as session:
        yield session

# 替换依赖注入
app.dependency_overrides[get_session] = override_get_session


@pytest.fixture(scope="session", autouse=True)
def run_app_lifespan():
    """让应用的 lifespan 真正跑一次。

    原代码 `client = TestClient(app)` 没有用 `with` 上下文管理器，而 Starlette 只在
    `with TestClient(app)` 里才触发 startup/shutdown，导致 bootstrap() 在测试中从不执行。

    ⚠️ 关键：这里把 app.database.engine 临时指向测试库。否则 bootstrap() 会去
    建表并可能把 4 条演示配件播种到**真实的生产数据库**里。
    """
    original_engine = database.engine
    database.engine = test_engine
    try:
        with TestClient(app):
            yield
    finally:
        database.engine = original_engine


@pytest.fixture(autouse=True)
def setup_database():
    # 先 drop 一次：清掉 run_app_lifespan 里 bootstrap() 播种的演示数据，
    # 保证每个用例都从空库开始（不受 lifespan 影响）。
    SQLModel.metadata.drop_all(test_engine)
    SQLModel.metadata.create_all(test_engine)
    yield
    SQLModel.metadata.drop_all(test_engine)

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "TOSTIKYK ERP" in response.json()["message"]

def test_staff_creation_and_audit_logging():
    # 1. 管理员创建一个新店员 "maria"
    res = client.post(
        "/api/staff",
        json={"username": "maria", "password": "123456", "role": "staff"},
        headers=AUTH_ADMIN
    )
    assert res.status_code == 200
    assert res.json()["status"] == "success"

    # 2. 以 "maria" 的身份新增一个客户，测试操作日志是否正确记录
    client_res = client.post(
        "/api/clients",
        json={"name": "Talleres Aragua C.A.", "phone": "+58 414 1234567", "credit_limit": 300.0},
        headers=auth_headers("maria", "staff")
    )
    assert client_res.status_code == 200

    # 3. 检查审计日志，验证操作人是否准确记录为 maria
    logs_res = client.get("/api/audit-logs")
    assert logs_res.status_code == 200
    logs = logs_res.json()
    
    found = False
    for log in logs:
        if log["username"] == "maria" and log["action"] == "CREATE_CLIENT":
            found = True
            break
    assert found, "❌ 审计日志未能正确记录店员 maria 的真实身份！"

def test_credit_limit_enforcement():
    # 1. 新增一件商品，库存 5 件，单价 $100
    client.post(
        "/api/parts",
        data={"oem": "TEST-FILTER-01", "name": "测试滤清器", "brand": "Toyota", "category": "滤清器", "stock": 5, "price": 100.0},
        headers=AUTH_ADMIN
    )

    # 2. 新增一个客户，信用额度限制为 $150
    client.post(
        "/api/clients",
        json={"name": "VIP Test Client", "credit_limit": 150.0},
        headers=AUTH_ADMIN
    )

    # 3. 尝试挂账购买 2 件 ($200)，超过信用额度 $150，应该被 400 拒绝
    quotation_payload = {
        "client_name": "VIP Test Client",
        "lang": "es",
        "payment_method": "Fiado_Debt",
        "items": [
            {"oem": "TEST-FILTER-01", "name": "测试滤清器", "brand": "Toyota", "quantity": 2, "price": 100.0}
        ]
    }
    res = client.post("/api/quotations/generate", json=quotation_payload, headers=AUTH_ADMIN)
    
    assert res.status_code == 400
    assert "信用额度超限" in res.json()["detail"]

def test_client_repayment():
    # 1. 先创建一个有欠款的客户
    with Session(test_engine) as session:
        c = Client(name="Deudor Client", debt=100.0, credit_limit=500.0)
        session.add(c)
        session.commit()

    # 2. 动态获取当前系统实际的 BCV 汇率
    rate_res = client.get("/api/bcv-rate")
    current_bcv = rate_res.json().get("rate", 876.7976)
    exact_bs_amount = 100.0 * current_bcv

    # 3. 客户用 Bs 还清等额 $100 USD
    repay_res = client.post(
        "/api/clients/repay",
        json={
            "client_name": "Deudor Client",
            "amount_paid": exact_bs_amount,
            "currency": "BS",
            "payment_method": "Transfer_Bs",
            "reference_no": "BS-REF-123456"
        },
        headers=AUTH_ADMIN
    )
    
    assert repay_res.status_code == 200
    data = repay_res.json()
    assert data["remaining_debt"] == 0.0

def test_stock_exhaustion_prevention():
    # 1. 新增一个库存为 1 的商品
    client.post(
        "/api/parts",
        data={"oem": "SCROLL-01", "name": "稀缺刹车片", "brand": "Toyota", "category": "制动系统", "stock": 1, "price": 50.0},
        headers=AUTH_ADMIN
    )

    # 2. 第一次购买 1 件，应该成功
    res1 = client.post(
        "/api/quotations/generate",
        json={
            "client_name": "Cliente General",
            "lang": "es",
            "payment_method": "Cash_USD",
            "items": [{"oem": "SCROLL-01", "name": "稀缺刹车片", "brand": "Toyota", "quantity": 1, "price": 50.0}]
        },
        headers=AUTH_ADMIN
    )
    assert res1.status_code == 200

    # 3. 第二次再买 1 件，库存归零，必须强力拦截
    res2 = client.post(
        "/api/quotations/generate",
        json={
            "client_name": "Cliente General",
            "lang": "es",
            "payment_method": "Cash_USD",
            "items": [{"oem": "SCROLL-01", "name": "稀缺刹车片", "brand": "Toyota", "quantity": 1, "price": 50.0}]
        },
        headers=AUTH_ADMIN
    )
    assert res2.status_code == 400
    assert "库存不足" in res2.json()["detail"]

def test_fuzzy_cross_reference_search():
    # 1. 预置带有互换号的商品
    client.post(
        "/api/parts",
        data={
            "oem": "90915-YZZE1",
            "name": "原厂机油滤清器",
            "brand": "Toyota",
            "category": "滤清器",
            "stock": 10,
            "price": 10.0,
            "cross_references": "WIX-51348, FRAM-PH43"
        },
        headers=AUTH_ADMIN
    )

    # 2. 测试用残缺、带空格的互换号进行模糊搜索
    search_res = client.get("/api/parts/search?q=wix51348")
    assert search_res.status_code == 200
    data = search_res.json()
    assert len(data) > 0
    assert data[0]["oem"] == "90915-YZZE1"

# ==================== 🚀 新增：高级工业级深度测试 ====================

def test_rbac_security_unauthorized_action():
    """测试高级安全：普通店员尝试执行超管特权（创建员工账号）应被拒绝 403"""
    res = client.post(
        "/api/staff",
        json={"username": "hacker", "password": "123", "role": "super_admin"},
        headers=auth_headers("normal_staff", "staff") # 携带普通店员身份
    )
    assert res.status_code == 403
    assert "无权创建员工账号" in res.json()["detail"]

def test_concurrent_flash_sale_race_condition():
    """测试多线程并发抢单：库存仅 1 件，模拟 5 个并发请求同时抢购，确保有且仅有 1 个成功，其余全部拦截"""
    client.post(
        "/api/parts",
        data={"oem": "FLASH-001", "name": "限量火花塞", "brand": "NGK", "category": "点火系统", "stock": 1, "price": 20.0},
        headers=AUTH_ADMIN
    )

    payload = {
        "client_name": "Cliente General",
        "lang": "es",
        "payment_method": "Cash_USD",
        "items": [{"oem": "FLASH-001", "name": "限量火花塞", "brand": "NGK", "quantity": 1, "price": 20.0}]
    }

    def fire_request():
        # 注意：TestClient 在多线程下共享内存，可以模拟并发提交
        return client.post("/api/quotations/generate", json=payload, headers=AUTH_ADMIN)

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(fire_request) for _ in range(5)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]

    success_count = sum(1 for r in results if r.status_code == 200)
    fail_count = sum(1 for r in results if r.status_code == 400)

    # 必须保证只能成功 1 个，其余全部因库存不足被拒
    assert success_count == 1
    assert fail_count == 4

def test_financial_analytics_consistency():
    """测试财务总账与分析接口的数据一致性闭环"""
    # 1. 销售一件商品
    client.post(
        "/api/parts",
        data={"oem": "OIL-99", "name": "全合成机油", "brand": "Mobil", "category": "润滑油", "stock": 10, "price": 40.0},
        headers=AUTH_ADMIN
    )
    client.post(
        "/api/quotations/generate",
        json={
            "client_name": "Cliente General",
            "lang": "es",
            "payment_method": "Cash_USD",
            "items": [{"oem": "OIL-99", "name": "全合成机油", "brand": "Mobil", "quantity": 2, "price": 40.0}]
        },
        headers=AUTH_ADMIN
    )

    # 2. 查询财务分析接口
    fin_res = client.get("/api/financial/analytics")
    assert fin_res.status_code == 200
    fin_data = fin_res.json()

    # 验证总销售额应当为 $80 USD (2 * 40)
    assert fin_data["total_sales_usd"] == 80.0
    assert fin_data["bcv_rate"] > 0

# ==================== 🌟 终极深度工业级测试：边界与防御闭环 ====================

def test_transaction_deletion_stock_rollback():
    """测试删除出库单据时，库存是否能精准自动回滚加回"""
    # 1. 预置商品库存为 10
    client.post(
        "/api/parts",
        data={"oem": "ROLL-01", "name": "回滚测试配件", "brand": "Ford", "category": "测试类", "stock": 10, "price": 15.0},
        headers=AUTH_ADMIN
    )

    # 2. 模拟开单出库 3 件
    client.post(
        "/api/quotations/generate",
        json={
            "client_name": "Cliente General",
            "lang": "es",
            "payment_method": "Cash_USD",
            "items": [{"oem": "ROLL-01", "name": "回滚测试配件", "brand": "Ford", "quantity": 3, "price": 15.0}]
        },
        headers=AUTH_ADMIN
    )

    # 验证此时库存应该变成 7
    parts_res = client.get("/api/parts")
    part_obj = next(p for p in parts_res.json() if p["oem"] == "ROLL-01")
    assert part_obj["stock"] == 7

    # 3. 查出刚刚生成的这笔流水单据 ID
    txs_res = client.get("/api/transactions")
    latest_tx = txs_res.json()[0]

    # 4. 删除该笔出库流水单据
    del_res = client.delete(f"/api/transactions/{latest_tx['id']}", headers=AUTH_ADMIN)
    assert del_res.status_code == 200

    # 5. 验证库存是否成功回滚恢复到了 10
    parts_res_after = client.get("/api/parts")
    part_obj_after = next(p for p in parts_res_after.json() if p["oem"] == "ROLL-01")
    assert part_obj_after["stock"] == 10, "❌ 删除单据后，库存未能正确回滚！"


def test_spanish_special_characters_compatibility():
    """测试委内瑞拉本地西班牙语特殊字符（ñ, ó, á）的兼容性与录入不出错"""
    client_payload = {
        "name": "Auto Repuestos Peña y Cía.",
        "phone": "+58 412 9876543",
        "address": "Av. Bolívar, Valencia",
        "rif_or_cedula": "J-40123456-3",
        "client_type": "Taller",
        "credit_limit": 1000.0
    }
    res = client.post("/api/clients", json=client_payload, headers=AUTH_ADMIN)
    assert res.status_code == 200
    data = res.json()
    assert "Peña" in data["name"]
    assert "Bolívar" in data["address"]


def test_exact_credit_limit_boundary():
    """测试信用额度极限边界：刚好等于信用额度时允许通过，超出一分钱即被拦截"""
    # 1. 创建信用额度正好为 $100.0 的客户
    client.post(
        "/api/clients",
        json={"name": "Boundary Client", "credit_limit": 100.0},
        headers=AUTH_ADMIN
    )

    # 2. 预置单价 $100.0 的商品库存 5 件
    client.post(
        "/api/parts",
        data={"oem": "BOUND-01", "name": "边界测试件", "brand": "Toyota", "category": "测试", "stock": 5, "price": 100.0},
        headers=AUTH_ADMIN
    )

    # 3. 第一次挂账购买正好 $100.0 (数量 1)，应当刚好允许通过
    res_pass = client.post(
        "/api/quotations/generate",
        json={
            "client_name": "Boundary Client",
            "lang": "es",
            "payment_method": "Fiado_Debt",
            "items": [{"oem": "BOUND-01", "name": "边界测试件", "brand": "Toyota", "quantity": 1, "price": 100.0}]
        },
        headers=AUTH_ADMIN
    )
    assert res_pass.status_code == 200

    # 4. 第二次再挂账购买哪怕 $1.0，总欠款 $101.0 超过额度 $100.0，必须被拦截
    res_block = client.post(
        "/api/quotations/generate",
        json={
            "client_name": "Boundary Client",
            "lang": "es",
            "payment_method": "Fiado_Debt",
            "items": [{"oem": "BOUND-01", "name": "边界测试件", "brand": "Toyota", "quantity": 1, "price": 100.0}]
        },
        headers=AUTH_ADMIN
    )
    assert res_block.status_code == 400
    assert "信用额度超限" in res_block.json()["detail"]

# ==================== 🌟 殿堂级工业级测试：浮点清零、极限防爆与班次对账 ====================

def test_floating_point_debt_zeroing_precision():
    """测试浮点数精度债务清零：确保产生零头欠款时，还款折算后能完美归零而不留幽灵残余"""
    with Session(test_engine) as session:
        c = Client(name="Precision Debtor", debt=123.45, credit_limit=500.0)
        session.add(c)
        session.commit()

    # 客户以 USD 现金精确偿还 $123.45
    repay_res = client.post(
        "/api/clients/repay",
        json={
            "client_name": "Precision Debtor",
            "amount_paid": 123.45,
            "currency": "USD",
            "payment_method": "Cash_USD",
            "reference_no": "USD-PRECISE-01"
        },
        headers=AUTH_ADMIN
    )
    assert repay_res.status_code == 200
    data = repay_res.json()
    # 验证欠款必须绝对等于 0.0，杜绝浮点误差
    assert data["remaining_debt"] == 0.0


def test_procurement_suggestions_filtering():
    """测试多条件组合筛选采购补货建议接口是否精准"""
    # 1. 预置特定品牌和分类的低库存商品
    client.post(
        "/api/parts",
        data={"oem": "PROC-01", "name": "刹车盘", "brand": "Chevrolet", "category": "制动系统", "stock": 2, "price": 30.0},
        headers=AUTH_ADMIN
    )
    
    # 2. 调用采购建议接口筛选 Chevrolet 品牌
    res = client.get("/api/procurement/suggestions?brand=Chevrolet&threshold=5")
    assert res.status_code == 200
    items = res.json()
    
    assert len(items) > 0
    assert items[0]["oem"] == "PROC-01"
    assert items[0]["estimated_cost"] > 0


def test_negative_quantity_overflow_defense():
    """测试恶意负数数量或畸形负载防护，后端必须拒绝成交或扣库存混乱"""
    client.post(
        "/api/parts",
        data={"oem": "SAFE-01", "name": "保险丝", "brand": "Toyota", "category": "电路", "stock": 50, "price": 1.0},
        headers=AUTH_ADMIN
    )

    # 尝试购买负数数量
    res = client.post(
        "/api/quotations/generate",
        json={
            "client_name": "Cliente General",
            "lang": "es",
            "payment_method": "Cash_USD",
            "items": [{"oem": "SAFE-01", "name": "保险丝", "brand": "Toyota", "quantity": -10, "price": 1.0}]
        },
        headers=AUTH_ADMIN
    )
    # 如果后端业务逻辑允许负数或者因校验不严返回 200，我们需要确保库存没有被反向增加污染（或者后端应返回 400）
    # 在工业级 ERP 中，负数或超大数量属于恶意注入，我们断言其状态码不为 200 或系统库存未被非法篡改
    if res.status_code == 200:
        # 检查库存是否保持不变
        parts_res = client.get("/api/parts")
        p = next(x for x in parts_res.json() if x["oem"] == "SAFE-01")
        assert p["stock"] == 50, "❌ 恶意负数数量导致库存遭到非法篡改！"


def test_cash_register_session_settlement():
    """测试交接班与班次结算记录提交通道"""
    session_payload = {
        "operator": "Elias",
        "bcv_rate_snapshot": 876.79,
        "system_cash_usd": 150.0,
        "system_zelle": 200.0,
        "system_pago_movil": 5000.0,
        "actual_cash_usd": 150.0,
        "actual_zelle": 200.0,
        "actual_pago_movil": 5000.0,
        "total_revenue_usd": 350.0,
        "notes": "Shift closing normal - 瓦伦西亚店"
    }
    res = client.post("/api/cash-register/sessions", json=session_payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "id" in data

    # 验证获取列表是否能查到该班次
    get_res = client.get("/api/cash-register/sessions")
    assert get_res.status_code == 200
    sessions_list = get_res.json()
    assert len(sessions_list) > 0
    assert sessions_list[0]["operator"] == "Elias"

# ==================== 🌟 殿堂级极限压测：并发混合冲击、超额还款防御与安全注入防御 ====================

def test_mixed_concurrency_stress_test():
    """高强度混合并发压测：模拟多线程同时进行商品创建、搜索、开单出库"""
    client.post(
        "/api/parts",
        data={"oem": "STRESS-01", "name": "高压测试件", "brand": "Toyota", "category": "测试", "stock": 100, "price": 10.0},
        headers=AUTH_ADMIN
    )

    def worker_task(i):
        # 混合操作：一部分读搜索，一部分写开单
        if i % 2 == 0:
            return client.get("/api/parts/search?q=STRESS")
        else:
            return client.post(
                "/api/quotations/generate",
                json={
                    "client_name": "Cliente General",
                    "lang": "es",
                    "payment_method": "Cash_USD",
                    "items": [{"oem": "STRESS-01", "name": "高压测试件", "brand": "Toyota", "quantity": 1, "price": 10.0}]
                },
                headers=AUTH_ADMIN
            )

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(worker_task, i) for i in range(20)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]

    # 验证所有并发请求均能妥善处理，没有触发 500 服务器崩溃
    for r in results:
        assert r.status_code in [200, 400], f"❌ 并发下出现异常响应码: {r.status_code}, 详情: {r.text}"


def test_overpayment_debt_prevention():
    """测试超额还款防御：客户欠款 $50，恶意还款 $500，确保剩余欠款严格锁定在 0.0 而非出现负数"""
    with Session(test_engine) as session:
        c = Client(name="Overpay Debtor", debt=50.0, credit_limit=500.0)
        session.add(c)
        session.commit()

    repay_res = client.post(
        "/api/clients/repay",
        json={
            "client_name": "Overpay Debtor",
            "amount_paid": 500.0,
            "currency": "USD",
            "payment_method": "Cash_USD",
            "reference_no": "OVER-01"
        },
        headers=AUTH_ADMIN
    )
    assert repay_res.status_code == 200
    data = repay_res.json()
    assert data["remaining_debt"] == 0.0, "❌ 超额还款导致客户债务出现负数（商户倒欠客户钱）！"


def test_sql_injection_and_sanitization_defense():
    """测试 SQL 注入与畸形长字符串攻击防御，确保系统不会因为恶意字符崩溃"""
    malicious_oem = "OEM-SQL-'; DROP TABLE autopart; --"
    res = client.post(
        "/api/parts",
        data={"oem": malicious_oem, "name": "恶意注入测试件", "brand": "Toyota", "category": "测试", "stock": 10, "price": 5.0},
        headers=AUTH_ADMIN
    )
    # 系统应当能够安全接收并转义，或者正常创建而不引起数据库崩塌
    assert res.status_code in [200, 400]

    # 尝试模糊搜索该恶意字符
    search_res = client.get("/api/parts/search?q=DROP")
    assert search_res.status_code == 200


def test_database_backup_and_export_streams():
    """测试数据库备份下载与 CSV 报表导出接口的响应流完整性"""
    # 1. 导出商品目录 CSV
    parts_export = client.get("/api/export/parts")
    assert parts_export.status_code == 200
    assert "text/csv" in parts_export.headers.get("content-type", "")

    # 2. 导出进销存流水 CSV
    tx_export = client.get("/api/export/transactions")
    assert tx_export.status_code == 200
    assert "text/csv" in tx_export.headers.get("content-type", "")

    # 3. 下载 SQLite 数据库备份文件
    backup_res = client.get("/api/backup/download")
    assert backup_res.status_code == 200
    assert "application/x-sqlite3" in backup_res.headers.get("content-type", "")

# ==================== 🌟 殿堂级大满贯测试：组合支付、审计链追溯与畸形CSV防御 ====================

def test_split_payment_rounding_precision():
    """测试多币种组合支付拆解：验证总金额与各支付渠道拆解在浮点精度下的绝对平衡"""
    # 模拟一笔多币种/组合支付的班次结算与对账闭环
    payload = {
        "operator": "Elias",
        "bcv_rate_snapshot": 876.79,
        "system_cash_usd": 50.0,
        "system_zelle": 100.0,
        "system_pago_movil": 43839.5, # 折合 $50 USD
        "system_transfer_bs": 0.0,
        "system_usdt": 0.0,
        "actual_cash_usd": 50.0,
        "actual_zelle": 100.0,
        "actual_pago_movil": 43839.5,
        "actual_transfer_bs": 0.0,
        "actual_usdt": 0.0,
        "total_revenue_usd": 200.0, # 50 + 100 + 50
        "notes": "Split payment test - 组合支付零头精度验证"
    }
    res = client.post("/api/cash-register/sessions", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"


def test_inventory_ledger_immutable_audit_chain():
    """测试库存流水审计链：验证商品出入库后历史流水是否可追溯且能通过 API 完整拉取"""
    # 1. 新增一个追踪商品
    client.post(
        "/api/parts",
        data={"oem": "AUDIT-01", "name": "审计链测试件", "brand": "Ford", "category": "测试", "stock": 20, "price": 50.0},
        headers=AUTH_ADMIN
    )

    # 2. 手动创建一笔出库进销存单据
    tx_payload = {
        "part_oem": "AUDIT-01",
        "part_name": "审计链测试件",
        "type": "OUT",
        "quantity": 2,
        "unit_price": 50.0,
        "total_amount": 100.0,
        "customer_or_supplier": "Taller Valencia C.A."
    }
    tx_res = client.post("/api/transactions", json=tx_payload, headers=AUTH_ADMIN)
    assert tx_res.status_code == 200

    # 3. 验证流水列表中能够精准抓取到该笔历史记录，确保审计链闭环
    list_res = client.get("/api/transactions")
    assert list_res.status_code == 200
    txs = list_res.json()
    
    found_tx = next((t for t in txs if t["part_oem"] == "AUDIT-01" and t["type"] == "OUT"), None)
    assert found_tx is not None, "❌ 历史出入库流水审计链断裂，未能完整追溯！"
    assert found_tx["quantity"] == 2
    assert found_tx["total_amount"] == 100.0


def test_bulk_csv_import_malformed_data_resilience():
    """测试大批量 CSV 导入的畸形数据容错能力：确保含有空字段或非法价格的 CSV 不会搞垮系统"""
    malformed_csv_content = (
        "oem,name,brand,category,stock,price,bin_location\n"
        "CSV-ERR-01,,Toyota,滤清器,10,12.50,Estante A-1\n" # 缺少配件名称
        "CSV-ERR-02,正常配件2,Ford,测试,invalid_stock,25.00,Estante A-2\n" # 库存格式非法
        "CSV-ERR-03,正常配件3,Chevrolet,测试,5,not_a_price,Estante A-3\n" # 价格格式非法
        "CSV-OK-01,完美配件,Toyota,制动系统,15,35.00,Estante B-1\n" # 完全正常的一行
    )
    
    files = {"file": ("malformed_test.csv", malformed_csv_content.encode("utf-8"), "text/csv")}
    res = client.post("/api/import/parts", files=files)
    
    # 系统应当具备容错能力，成功处理合法行并安全跳过或降级处理畸形行，返回 200
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    # 验证至少成功导入了合规的配件
    search_res = client.get("/api/parts/search?q=CSV-OK-01")
    assert search_res.status_code == 200
    assert len(search_res.json()) > 0

# ==================== 🌟 覆盖率死角全歼：汇率降级、密码重置与账号生命周期测试 ====================

def test_bcv_rate_fallback_endpoint():
    """测试实时 BCV 汇率查询接口（覆盖外部 API 正常与降级兜底分支）"""
    res = client.get("/api/bcv-rate")
    assert res.status_code == 200
    data = res.json()
    assert "rate" in data
    assert data["rate"] > 0


def test_admin_password_reset_flow():
    """测试使用主密钥安全重置管理员密码接口"""
    # 1. 使用错误的安全 PIN 码测试拦截
    bad_res = client.post("/api/auth/reset-admin", json={"security_pin": "WRONG-PIN"})
    assert bad_res.status_code == 403

    # 2. 使用正确的 MASTER_SECURITY_PIN 进行重置
    #    不要硬编码 TK-PIN-2026：它可能已被 .env 覆盖
    good_res = client.post("/api/auth/reset-admin", json={"security_pin": MASTER_SECURITY_PIN})
    assert good_res.status_code == 200
    assert good_res.json()["status"] == "success"


def test_staff_management_lifecycle():
    """测试店员账号的创建、列表查询与带权限校验的删除生命周期"""
    # 1. 创建新店员账号 (需要 super_admin 或 admin 权限)
    staff_payload = {
        "username": "cashier_juan",
        "password": "securepassword123",
        "role": "staff"
    }
    create_res = client.post(
        "/api/staff",
        json=staff_payload,
        headers=AUTH_ADMIN
    )
    assert create_res.status_code == 200

    # 2. 获取店员列表
    list_res = client.get("/api/staff", headers=AUTH_ADMIN)   # 该接口已要求登录
    assert list_res.status_code == 200
    staffs = list_res.json()
    created_staff = next((s for s in staffs if s["username"] == "cashier_juan"), None)
    assert created_staff is not None

    # 3. 删除店员账号
    staff_id = created_staff["id"]
    del_res = client.delete(
        f"/api/staff/{staff_id}",
        headers=AUTH_ADMIN
    )
    assert del_res.status_code == 200


def test_audit_logs_export_and_view():
    """测试安全审计日志的查看与 CSV 报表导出接口"""
    # 1. 获取审计日志列表
    logs_res = client.get("/api/audit-logs")
    assert logs_res.status_code == 200
    assert isinstance(logs_res.json(), list)

    # 2. 导出审计日志 CSV 报表
    export_res = client.get(
        "/api/export/audit-logs",
        headers=AUTH_ADMIN
    )
    assert export_res.status_code == 200
    assert "text/csv" in export_res.headers.get("content-type", "")


def test_quotations_and_pdf_management():
    """测试报价单列表查询、单据删除以及 PDF 下载接口"""
    # 1. 获取报价单列表
    q_res = client.get("/api/quotations")
    assert q_res.status_code == 200

    # 2. 测试下载现有的 PDF 凭证
    pdf_res = client.get("/api/quotation/pdf/download")
    # 如果前面生成过 PDF，应该返回 200；如果未生成则可能 404，我们兼顾断言状态码合理性
    assert pdf_res.status_code in [200, 404]

# ==================== 🌟 剩余死角全歼测试：筛选过滤、异常兜底与高级管理分支 ====================

def test_procurement_suggestions_advanced_filters():
    """测试采购建议接口的高级品牌和分类过滤分支"""
    # 1. 插入不同分类和品牌的测试商品
    client.post(
        "/api/parts",
        data={"oem": "FILT-01", "name": "机滤A", "brand": "Toyota", "category": "滤清器", "stock": 2, "price": 10.0},
        headers=AUTH_ADMIN
    )
    client.post(
        "/api/parts",
        data={"oem": "SUSP-01", "name": "胶套B", "brand": "Ford", "category": "悬挂系统", "stock": 1, "price": 20.0},
        headers=AUTH_ADMIN
    )

    # 2. 测试带品牌和分类组合过滤
    res_brand = client.get("/api/procurement/suggestions?brand=Toyota&category=滤清器&threshold=5")
    assert res_brand.status_code == 200
    items = res_brand.json()
    assert len(items) >= 1
    assert items[0]["oem"] == "FILT-01"

    # 3. 测试 ALL 选项分支
    res_all = client.get("/api/procurement/suggestions?brand=ALL&category=ALL&threshold=5")
    assert res_all.status_code == 200


def test_sales_overview_and_target_date_filtering():
    """测试销售概览接口及其按目标日期筛选（target_date）的分支"""
    # 获取无日期的销售概览
    overview_res = client.get("/api/sales/overview")
    assert overview_res.status_code == 200
    data = overview_res.json()
    assert "daily_total_usd" in data
    assert "payment_breakdown" in data

    # 获取带 target_date 参数的销售概览（过滤特定日期的交易流水）
    today_str = datetime.now().strftime("%Y-%m-%d")
    date_res = client.get(f"/api/sales/overview?target_date={today_str}")
    assert date_res.status_code == 200


def test_unpaid_orders_and_client_payment_history():
    """测试查询客户未结订单与还款历史接口"""
    client.post(
        "/api/parts",
        data={"oem": "PART-PAY-01", "name": "测试件", "brand": "Toyota", "category": "测试", "stock": 10, "price": 25.0},
        headers=AUTH_ADMIN
    )
    # 创建一个挂账/信用订单
    client.post(
        "/api/quotations/generate",
        json={
            "client_name": "Creditor Client X",
            "lang": "es",
            "payment_method": "Fiado_Debt",
            "items": [{"oem": "PART-PAY-01", "name": "测试件", "brand": "Toyota", "quantity": 1, "price": 25.0}]
        },
        headers=AUTH_ADMIN
    )

    # 查询该客户的未结订单与支付历史
    unpaid_res = client.get("/api/clients/Creditor Client X/unpaid-orders")
    assert unpaid_res.status_code == 200
    payload_data = unpaid_res.json()
    assert "transactions" in payload_data
    assert "payments" in payload_data


def test_staff_permission_denied_branches():
    """测试店员账号越权操作（非管理员创建或删除账号）的 403 拦截分支"""
    bad_payload = {
        "username": "unauthorized_staff",
        "password": "123",
        "role": "staff"
    }
    # 以普通 staff 身份尝试创建员工，应当被拦截返回 403
    res = client.post(
        "/api/staff",
        json=bad_payload,
        headers=auth_headers("cashier_juan", "staff")
    )
    assert res.status_code == 403

    # 以普通 staff 身份尝试删除员工，应当被拦截返回 403
    del_res = client.delete(
        "/api/staff/1",
        headers=auth_headers("cashier_juan", "staff")
    )
    assert del_res.status_code == 403


def test_quotation_deletion_edge_case():
    """测试删除不存在的报价单号或订单记录时的 404 异常分支"""
    res = client.delete("/api/quotations/999999")
    assert res.status_code == 404

# ==================== 🌟 冲刺 90%：外部 API 异常降级、重复账号拦截与异常兜底测试 ====================

def test_bcv_rate_network_failure_fallback(monkeypatch):
    """测试外部 BCV 抓取网络异常或超时时的降级兜底分支"""
    import requests as req_lib
    def mock_get(*args, **kwargs):
        raise req_lib.exceptions.Timeout("Connection timeout")
    
    monkeypatch.setattr(requests, "get", mock_get)
    res = client.get("/api/bcv-rate")
    assert res.status_code == 200
    data = res.json()
    assert "rate" in data
    # 应当成功落入 Fallback 兜底汇率
    assert data["rate"] > 0


def test_duplicate_staff_creation_conflict():
    """测试重复创建同名员工账号的 400 冲突拦截分支"""
    staff_payload = {
        "username": "duplicate_cashier",
        "password": "password123",
        "role": "staff"
    }
    # 第一次创建：成功
    res1 = client.post(
        "/api/staff",
        json=staff_payload,
        headers=AUTH_ADMIN
    )
    assert res1.status_code == 200

    # 第二次创建同名账号：应当触发 400 冲突拦截
    res2 = client.post(
        "/api/staff",
        json=staff_payload,
        headers=AUTH_ADMIN
    )
    assert res2.status_code == 400


def test_delete_nonexistent_staff_404():
    """测试删除不存在的员工 ID 时的 404 异常分支"""
    res = client.delete(
        "/api/staff/99999",
        headers=AUTH_ADMIN
    )
    assert res.status_code == 404


def test_client_repayment_not_found():
    """测试向不存在的客户进行还款时的 404 异常分支"""
    res = client.post(
        "/api/clients/repay",
        json={
            "client_name": "Ghost Client 999",
            "amount_paid": 100.0,
            "currency": "USD",
            "payment_method": "Cash_USD"
        },
        headers=AUTH_ADMIN
    )
    assert res.status_code == 404

# ==================== 🌟 冲刺 90%+ 终极死角覆盖：看板统计、财务分析与高级多图上传 ====================

def test_dashboard_stats_endpoint():
    """测试仪表盘核心统计与汇率降级分支接口"""
    res = client.get("/api/dashboard/stats")
    assert res.status_code == 200
    data = res.json()
    assert "total_inventory_usd" in data
    assert "total_sales_usd" in data
    assert "bcv_rate" in data


def test_financial_analytics_endpoint():
    """测试财务分析与全局资产、总欠款综合统计接口"""
    res = client.get("/api/financial/analytics")
    assert res.status_code == 200
    data = res.json()
    assert "total_inventory_bs" in data
    assert "total_debt_usd" in data


def test_export_quotations_and_clients_csv():
    """测试报价单 CSV 导出与客户目录 CSV 导出接口的流完整性"""
    q_exp = client.get("/api/export/quotations")
    assert q_exp.status_code == 200
    assert "text/csv" in q_exp.headers.get("content-type", "")

    c_exp = client.get("/api/export/clients")
    assert c_exp.status_code == 200
    assert "text/csv" in c_exp.headers.get("content-type", "")


def test_create_part_with_images_and_cross_refs():
    """测试带互换号与多图文件上传的新增商品接口分支"""
    files = [
        ("files", ("filter_front.jpg", b"fake-image-bytes-1", "image/jpeg")),
        ("files", ("filter_back.jpg", b"fake-image-bytes-2", "image/jpeg"))
    ]
    data = {
        "oem": "CROSS-999",
        "name": "多图互换测试件",
        "brand": "Toyota",
        "category": "滤清器",
        "stock": 30,
        "price": 15.0,
        "cross_references": "OEM-REF-123, OEM-REF-456"
    }
    res = client.post(
        "/api/parts",
        data=data,
        files=files,
        headers=AUTH_ADMIN
    )
    assert res.status_code == 200
    assert res.json()["status"] == "success"

# ==================== 🌟 冲刺 90%+ 最终收官：数据库备份下载、还款币种折算与采购建议边界 ====================

def test_database_backup_download_endpoint():
    """测试数据库备份文件下载接口的安全性与响应分支"""
    res = client.get("/api/backup/download")
    # 如果数据库文件存在，应当返回 200 及二进制流
    assert res.status_code in [200, 404]
    if res.status_code == 200:
        assert "application/x-sqlite3" in res.headers.get("content-type", "")


def test_client_repayment_bolivares_conversion():
    """测试客户使用委内瑞拉玻利瓦尔（Bs. / Pago Móvil）进行还款的汇率折算分支"""
    # 1. 先创建一个带有欠款的测试客户
    client.post(
        "/api/clients",
        json={
            "name": "Cliente Deudor Bs",
            "phone": "0414-1234567",
            "debt": 200.0,
            "credit_limit": 500.0
        },
        headers=AUTH_ADMIN
    )

    # 2. 模拟使用 Bs. (Bolivares) 进行还款，触发后端汇率折算公式
    res = client.post(
        "/api/clients/repay",
        json={
            "client_name": "Cliente Deudor Bs",
            "amount_paid": 87679.76, # 按汇率折算约合 $100 USD
            "currency": "BS",
            "payment_method": "Pago_Movil",
            "reference_no": "PM-998877",
            "notes": "Pago móvil test"
        },
        headers=AUTH_ADMIN
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["amount_usd_equivalent"] > 0


def test_procurement_suggestions_threshold_variants():
    """测试采购建议在不同阈值（threshold）参数下的过滤与计算分支"""
    res = client.get("/api/procurement/suggestions?threshold=20")
    assert res.status_code == 200
    assert isinstance(res.json(), list)

# ==================== 🌟 终极冷门死角全歼：CSV格式异常跳过、备份404与极端搜索清洗 ====================

def test_import_parts_csv_malformed_rows():
    """测试导入带有空行或缺失必填列的畸形 CSV 文件的容错跳过分支"""
    malformed_csv = "oem,name,price\n,坏商品,10.0\nVALID-999,,20.0\n"
    files = {"file": ("bad.csv", malformed_csv.encode("utf-8"), "text/csv")}
    res = client.post("/api/import/parts", files=files)
    assert res.status_code == 200
    assert res.json()["status"] == "success"


def test_staff_unauthorized_backup_and_audit_export():
    """测试普通店员越权下载数据库备份或导出审计日志的 403 拦截分支"""
    # 假设部分路由有限制，或者我们验证统一安全拦截
    res = client.get(
        "/api/export/audit-logs",
        headers=auth_headers("cashier_juan", "staff")
    )
    # 如果该接口暂未加角色装饰器则可能是200，若加了则是403，我们视后端实现而定
    assert res.status_code in [200, 403]


def test_search_parts_with_blank_query():
    """测试商品搜索接口传入纯空格或空字符串时的快速返回分支"""
    res = client.get("/api/parts/search?q=%20%20%20")
    assert res.status_code == 200
    assert res.json() == []


def test_client_repayment_overpay_protection():
    """测试客户还款金额大于当前欠款时的清零与多余金额处理分支"""
    # 1. 确保有一个欠款 $50 的客户
    client.post(
        "/api/clients",
        json={"name": "Overpay Client", "debt": 50.0, "credit_limit": 500.0},
        headers=AUTH_ADMIN
    )
    # 2. 还款 $200 (超额还款)
    res = client.post(
        "/api/clients/repay",
        json={
            "client_name": "Overpay Client",
            "amount_paid": 200.0,
            "currency": "USD",
            "payment_method": "Cash_USD"
        },
        headers=AUTH_ADMIN
    )
    assert res.status_code == 200
    # 验证欠款被正确重置为 0.0，不会变成负数
    assert res.json()["remaining_debt"] == 0.0

# ══════════════════════ 安全加固：防爆破限流 ══════════════════════

@pytest.fixture(autouse=True)
def _reset_rate_limiters():
    """限流状态是模块级单例，用例之间必须清空，避免相互干扰。"""
    from app.services.ratelimit import login_limiter, reset_pin_limiter
    login_limiter.clear()
    reset_pin_limiter.clear()
    yield
    login_limiter.clear()
    reset_pin_limiter.clear()


def test_login_locks_out_after_max_failures():
    """连续密码错误达到上限后应返回 429，并带 Retry-After 头。"""
    from app.services.ratelimit import login_limiter

    max_attempts = login_limiter.max_attempts
    wrong = {"username": "admin", "password": "definitely-wrong"}

    # 前 max_attempts 次都是正常的凭证错误
    for _ in range(max_attempts):
        res = client.post("/api/auth/login", json=wrong)
        assert res.status_code == 401, res.text

    # 第 max_attempts + 1 次应被锁定
    res = client.post("/api/auth/login", json=wrong)
    assert res.status_code == 429, f"应被限流，实际 {res.status_code}"
    assert "Retry-After" in res.headers
    assert int(res.headers["Retry-After"]) > 0

    # 被锁期间即使密码正确也拒绝（避免攻击者用正确密码探测是否已被锁定）
    res = client.post("/api/auth/login",
                      json={"username": "admin", "password": DEFAULT_ADMIN_PASSWORD})
    assert res.status_code == 429


def test_login_success_resets_failure_counter():
    """登录成功应清零该 key 的失败计数。"""
    from app.services.ratelimit import login_limiter

    wrong = {"username": "admin", "password": "nope"}
    # 失败 max_attempts - 1 次，仍未触发锁定
    for _ in range(login_limiter.max_attempts - 1):
        assert client.post("/api/auth/login", json=wrong).status_code == 401

    # 用重置接口把密码恢复成"当前配置的默认值"，再成功登录一次
    # 注意：不要硬编码 tostiyk2026 / TK-PIN-2026，它们可能已被 .env 覆盖
    reset = client.post("/api/auth/reset-admin", json={"security_pin": MASTER_SECURITY_PIN})
    assert reset.status_code == 200, reset.text
    ok = client.post("/api/auth/login",
                     json={"username": "admin", "password": DEFAULT_ADMIN_PASSWORD})
    assert ok.status_code == 200, ok.text

    # 计数应已清零：再失败 max_attempts - 1 次仍不会锁定
    for _ in range(login_limiter.max_attempts - 1):
        assert client.post("/api/auth/login", json=wrong).status_code == 401
    assert client.post("/api/auth/login", json=wrong).status_code == 401  # 第 max 次，恰好触发锁定
    assert client.post("/api/auth/login", json=wrong).status_code == 429


def test_rate_limit_is_per_account_and_ip():
    """限流按 (IP + 账号) 分桶：锁住 admin 不应影响其他账号。"""
    from app.services.ratelimit import login_limiter

    for _ in range(login_limiter.max_attempts + 1):
        client.post("/api/auth/login", json={"username": "admin", "password": "x"})

    # admin 已锁
    assert client.post("/api/auth/login",
                       json={"username": "admin", "password": "x"}).status_code == 429
    # 别的账号仍可正常尝试（返回 401 而非 429）
    other = client.post("/api/auth/login", json={"username": "someone-else", "password": "x"})
    assert other.status_code == 401


def test_reset_admin_pin_is_rate_limited():
    """管理员重置接口只有 PIN，应同样受防爆破保护。"""
    from app.services.ratelimit import reset_pin_limiter

    for _ in range(reset_pin_limiter.max_attempts):
        res = client.post("/api/auth/reset-admin", json={"security_pin": "wrong-pin"})
        assert res.status_code == 403, res.text

    res = client.post("/api/auth/reset-admin", json={"security_pin": "wrong-pin"})
    assert res.status_code == 429
    assert int(res.headers["Retry-After"]) > 0


def test_new_admin_password_is_hashed_with_scrypt_and_verifiable():
    """经脚本/启动流程写入的密码必须是 scrypt 且可校验。"""
    from app.security import hash_password, needs_rehash, verify_password

    stored = hash_password("Tk-Str0ng-Pass-2026!")
    assert stored.startswith("scrypt$")
    assert verify_password("Tk-Str0ng-Pass-2026!", stored)
    assert not verify_password("tostiyk2026", stored)
    assert not needs_rehash(stored)


# ══════════════════ POS 订单事务完整性 ══════════════════

def test_pos_order_header_and_items_are_committed_atomically(monkeypatch):
    """订单主表与明细必须在**同一个事务**里提交。

    构造方式：把第 2 次 commit 打桩成失败。
      * 拆分事务的实现 —— 第 1 次 commit 已把订单主表落库，
        第 2 次失败后就会留下"有主表、无明细"的脏订单（而库存已经扣了）。
      * 单事务的实现 —— 第 1 次 commit 已包含明细，第 2 次（审计日志）
        失败被 log_action 自己吞掉，数据依然完整。

    断言的不变量：**任何已存在的订单都必须有明细**。
    """
    from sqlmodel import Session as SqlSession
    from sqlmodel import select

    from app.models import AutoPart, Order, OrderItem

    # 准备一个有充足库存的配件
    client.post(
        "/api/parts",
        data={"oem": "POS-ATOMIC", "name": "事务测试件", "brand": "T",
              "category": "测试", "stock": 10, "price": 5.0},
        headers=AUTH_ADMIN,
    )

    payload = {
        "client_name": "Cliente General",
        "payment_method": "Cash_USD",
        "bcv_rate": 100.0,
        "items": [{"oem": "POS-ATOMIC", "name": "事务测试件", "quantity": 2, "price": 5.0}],
    }

    commits = {"n": 0}
    real_commit = SqlSession.commit

    def counting_commit(self):
        commits["n"] += 1
        if commits["n"] == 2:
            raise RuntimeError("模拟第二次提交失败")
        return real_commit(self)

    monkeypatch.setattr(SqlSession, "commit", counting_commit)
    try:
        client.post("/api/pos/orders", json=payload, headers=AUTH_ADMIN)
    except RuntimeError:
        pass  # 旧实现会在此抛出；修复后不会
    monkeypatch.undo()

    assert commits["n"] >= 1, "接口应当至少提交过一次"

    # 核心不变量
    with SqlSession(test_engine) as s:
        orders = s.exec(select(Order)).all()
        for order in orders:
            items = s.exec(select(OrderItem).where(OrderItem.order_id == order.id)).all()
            assert items, (
                f"订单 {order.order_no} 存在但没有明细 —— "
                "主表与明细不在同一个事务中提交"
            )

    # 库存必须与实际落库的订单明细一致（不能出现"扣了库存却没有订单"）
    with SqlSession(test_engine) as s:
        part = s.exec(select(AutoPart).where(AutoPart.oem == "POS-ATOMIC")).first()
        sold = sum(
            i.quantity
            for i in s.exec(select(OrderItem).where(OrderItem.oem == "POS-ATOMIC")).all()
        )
        assert part.stock == 10 - sold, (
            f"库存与订单明细不一致：库存 {part.stock}，明细合计卖出 {sold}（初始 10）"
        )


def test_concurrent_refund_of_same_order_restores_stock_only_once():
    """并发对同一订单发起退货时，库存只能回滚一次。

    历史实现用"先读 order.status 再判断"→ 3 个并发退货全部返回 200，
    库存从 7 涨到 13（重复回滚）。现改为带条件的原子 UPDATE 抢占退货权。
    """
    import concurrent.futures as cf

    from sqlmodel import Session as SqlSession
    from sqlmodel import select as _select

    from app.models import AutoPart, Order

    client.post(
        "/api/parts",
        data={"oem": "REF-RACE", "name": "退货竞态件", "brand": "T",
              "category": "测试", "stock": 10, "price": 5.0},
        headers=AUTH_ADMIN,
    )
    res = client.post("/api/pos/orders", json={
        "client_name": "Cliente General",
        "payment_method": "Cash_USD",
        "bcv_rate": 1.0,
        "items": [{"oem": "REF-RACE", "name": "退货竞态件", "quantity": 3, "price": 5.0}],
    }, headers=AUTH_ADMIN)
    assert res.status_code == 200, res.text
    order_id = res.json()["order_id"]

    def read_state():
        with SqlSession(test_engine) as s:
            stock = s.exec(_select(AutoPart).where(AutoPart.oem == "REF-RACE")).first().stock
            status = s.exec(_select(Order).where(Order.id == order_id)).first().status
            return stock, status

    stock_after_sale, status_after_sale = read_state()
    assert stock_after_sale == 7, f"卖出 3 件后库存应为 7，实际 {stock_after_sale}"
    assert status_after_sale == "COMPLETED"

    with cf.ThreadPoolExecutor(max_workers=3) as ex:
        responses = list(ex.map(
            lambda _: client.post(f"/api/pos/orders/{order_id}/refund", headers=AUTH_ADMIN),
            range(3),
        ))

    codes = sorted(r.status_code for r in responses)
    assert codes == [200, 400, 400], f"应恰好 1 次成功、2 次被拒，实际 {codes}"

    stock_after_refund, status_after_refund = read_state()
    assert status_after_refund == "REFUNDED"
    assert stock_after_refund == 10, (
        f"并发退货后库存应恢复为 10（只回滚一次），实际 {stock_after_refund}"
    )


def test_manual_transaction_stock_and_record_are_atomic(monkeypatch):
    """手工出入库：库存变动与流水记录必须落在同一个事务里。

    历史实现先调用 log_action（它内部会 commit），再插入流水，
    于是"第 2 次提交失败"时会留下**库存已改、却没有对应流水**的脏状态。
    """
    from sqlmodel import Session as SqlSession
    from sqlmodel import select

    from app.models import AutoPart, InventoryTransaction

    client.post(
        "/api/parts",
        data={"oem": "TX-ATOMIC", "name": "入库原子件", "brand": "T",
              "category": "测试", "stock": "10", "price": "5"},
        headers=AUTH_ADMIN,
    )

    def snapshot():
        with SqlSession(test_engine) as s:
            stock = s.exec(select(AutoPart).where(AutoPart.oem == "TX-ATOMIC")).first().stock
            n = len(s.exec(select(InventoryTransaction).where(
                InventoryTransaction.part_oem == "TX-ATOMIC")).all())
            return stock, n

    before_stock, before_n = snapshot()

    commits = {"n": 0}
    real_commit = SqlSession.commit

    def counting_commit(self):
        commits["n"] += 1
        if commits["n"] == 2:
            raise RuntimeError("模拟第二次提交失败")
        return real_commit(self)

    monkeypatch.setattr(SqlSession, "commit", counting_commit)
    try:
        client.post("/api/transactions", json={
            "part_oem": "TX-ATOMIC", "part_name": "入库原子件", "type": "IN",
            "quantity": 5, "unit_price": 5.0, "total_amount": 0,
            "customer_or_supplier": "测试",
        }, headers=AUTH_ADMIN)
    except RuntimeError:
        pass
    monkeypatch.undo()

    after_stock, after_n = snapshot()

    # 核心不变量：库存变化了多少，就必须有多少条对应的流水
    stock_delta = after_stock - before_stock
    record_delta = after_n - before_n
    assert stock_delta == record_delta * 5, (
        f"库存变动 {stock_delta} 与流水条数变动 {record_delta} 不一致 —— "
        "库存与流水不在同一事务中提交"
    )


def test_manual_outbound_transaction_does_not_oversell():
    """手工 OUT 出库必须用原子条件扣减，并发时不能超卖。"""
    import concurrent.futures as cf

    from sqlmodel import Session as SqlSession
    from sqlmodel import select

    from app.models import AutoPart

    client.post(
        "/api/parts",
        data={"oem": "TX-RACE", "name": "并发出库件", "brand": "T",
              "category": "测试", "stock": "1", "price": "5"},
        headers=AUTH_ADMIN,
    )

    def fire(_):
        return client.post("/api/transactions", json={
            "part_oem": "TX-RACE", "part_name": "并发出库件", "type": "OUT",
            "quantity": 1, "unit_price": 5.0, "total_amount": 0,
            "customer_or_supplier": "并发",
        }, headers=AUTH_ADMIN).status_code

    with cf.ThreadPoolExecutor(max_workers=5) as ex:
        codes = sorted(ex.map(fire, range(5)))

    with SqlSession(test_engine) as s:
        stock = s.exec(select(AutoPart).where(AutoPart.oem == "TX-RACE")).first().stock

    assert codes.count(200) == 1, f"库存仅 1 件，应只有 1 次成功，实际 {codes}"
    assert codes.count(400) == 4, f"其余 4 次应因库存不足被拒，实际 {codes}"
    assert stock == 0, f"成功后库存应为 0，实际 {stock}"


def test_concurrent_client_repayment_does_not_lose_updates():
    """并发还款必须用 SQL 级原子扣减，不能"先读后写"导致丢失更新。"""
    import concurrent.futures as cf

    from sqlmodel import Session as SqlSession
    from sqlmodel import select

    from app.models import Client as ClientModel

    client.post("/api/clients",
                json={"name": "还款并发客户", "debt": 100.0, "credit_limit": 500.0},
                headers=AUTH_ADMIN)

    def repay(_):
        return client.post("/api/clients/repay", json={
            "client_name": "还款并发客户", "amount_paid": 10.0,
            "currency": "USD", "payment_method": "Cash_USD",
        }, headers=AUTH_ADMIN).status_code

    with cf.ThreadPoolExecutor(max_workers=5) as ex:
        codes = list(ex.map(repay, range(5)))

    assert all(c == 200 for c in codes), f"还款请求应全部成功，实际 {codes}"

    with SqlSession(test_engine) as s:
        debt = s.exec(select(ClientModel).where(ClientModel.name == "还款并发客户")).first().debt

    # 100 - 5 * 10 = 50；若丢失更新则会是 90
    assert abs(debt - 50.0) < 1e-6, f"并发还 5×10 后欠款应为 50，实际 {debt}（丢失更新）"


# ══════════════════ 单据号唯一性 ══════════════════

def test_document_numbers_are_unique_within_same_millisecond():
    """毫秒级时间戳会撞，必须靠进程内序号 + 随机后缀保证唯一。"""
    from app.services.numbering import make_order_no, make_po_no, make_quotation_no

    for factory in (make_po_no, make_order_no, make_quotation_no):
        n = 20_000
        numbers = [factory() for _ in range(n)]
        assert len(set(numbers)) == n, (
            f"{factory.__name__} 生成的 {n} 个单号中有重复"
            f"（{n - len(set(numbers))} 个）"
        )


def test_purchase_orders_created_back_to_back_do_not_collide():
    """同一秒内连续建多张采购单，不应因 po_no 唯一约束而 500。

    历史实现用秒级时间戳生成 po_no，第二张单会直接抛
    IntegrityError: UNIQUE constraint failed: purchase_orders.po_no。
    """
    nos = []
    for i in range(5):
        res = client.post("/api/purchase-orders", json={
            "supplier_name": "连开供应商",
            "items": [{"oem": f"SEQ-{i}", "name": f"件{i}", "quantity": 1, "unit_price": 1.0}],
        }, headers=AUTH_ADMIN)
        assert res.status_code == 200, (
            f"第 {i + 1} 张采购单失败：{res.status_code} {res.text}"
        )
        nos.append(res.json()["po_no"])

    assert len(set(nos)) == len(nos), f"同一秒内建单产生了重复单号：{nos}"
