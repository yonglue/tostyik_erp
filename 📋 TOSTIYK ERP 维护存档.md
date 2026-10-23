# 📋 TOSTIYK ERP 维护存档

> 本文件记录 2026-10-22 至 2026-10-23 期间的一次系统性基础设施修复。
> 目的：让下一个维护者（可能是未来的你）理解"为什么代码长这样"，避免回退或误改。

---

## 一、项目概况

| 项     | 值                                                      |
| ------ | ------------------------------------------------------- |
| 项目名 | TOSTIYK ERP                                             |
| 后端   | FastAPI + SQLModel + SQLite + Alembic                   |
| 前端   | Vue 3 + Vite + Tailwind                                 |
| 数据库 | `tostiyk_erp.db`（生产）、`_test_erp.db`（测试，空库）  |
| 主入口 | `app/main.py`（根目录 `main.py` 已废弃，仅转发 import） |

---

## 二、本轮修复时间线

### 阶段 1：迁移链修复（P0，最关键）

**问题**：`alembic upgrade head` 从未真正跑通过。所有表靠 `SQLModel.metadata.create_all()` 兜底建。

**根因**：
- `082a363b8b44_initial_migration.py`（初始迁移）是空的
- `48722d41581c_add_expense_table.py` 是 `pass`（注释写"表已存在"）
- `2abce90f8fce_add_supplier_payment_table.py` 是 `pass`
- `alembic current` 长期停在 `c3e5f7a9b1d2`，落后 head 4 个迁移

**修复**：把 3 个迁移改成幂等版（`inspect(bind)` 判断存在再执行），`alembic upgrade head` 首次真正跑通。

**验证**：
```bash
alembic revision --autogenerate -m "verify_no_drift"
# 生成的文件 upgrade() 里只有 pass → 零漂移
```

**注意**：`tostiyk_erp.db` 里的 `expenses` 表**一直在**（此前诊断为"缺失"是查询用错了单数 `expense`，实际表名是 `expenses`）。

**相关文件**：
- `alembic/versions/edf6251cee6c_*.py`（加幂等）
- `alembic/versions/48722d41581c_*.py`（加幂等）
- `alembic/versions/4136d0a0c9ac_*.py`（加幂等）

---

### 阶段 2：启动兜底开关（Step A + Step B）

**问题**：`app/database.py:33` 的 `create_all` 和 Alembic 并行，迁移失败被 `except` 静默吞掉，生产环境可能带残缺 schema 启动。

**修复**：

**`app/config.py`** 新增两个开关：
```python
AUTO_CREATE_TABLES: bool = os.getenv("TK_AUTO_CREATE_TABLES", "1").strip().lower() in (
    "1", "true", "yes", "on",
)
STRICT_MIGRATION: bool = os.getenv("TK_STRICT_MIGRATION", "").strip().lower() in (
    "1", "true", "yes", "on",
)
```

**`app/database.py`** 的 `init_db()`：
```python
if not AUTO_CREATE_TABLES:
    print("⏭️  TK_AUTO_CREATE_TABLES=0，已跳过 create_all")
    return
SQLModel.metadata.create_all(engine)
```

**`app/main.py`** 的 `bootstrap()`：
```python
except Exception as e:
    print(f"❌ 数据库迁移执行失败: {e}")
    if not AUTO_CREATE_TABLES or STRICT_MIGRATION:
        raise RuntimeError(...) from e
    print("⚠️  继续启动，依赖 create_all 兜底")
```

**环境变量默认值**（保持现状，生产按需开启）：

| 变量                    | 默认        | 生产建议    |
| ----------------------- | ----------- | ----------- |
| `TK_AUTO_CREATE_TABLES` | `1`（开启） | `0`（关闭） |
| `TK_STRICT_MIGRATION`   | 空（关闭）  | `1`（开启） |
| `TK_STRICT_SECURITY`    | 空（关闭）  | `1`（开启） |

**验证**（三条启动日志）：
```
默认：              ✅ 迁移 → ✅ create_all
TK_AUTO_CREATE_TABLES=0：  ✅ 迁移 → ⏭️ 跳过
TK_STRICT_MIGRATION=1：    ✅ 迁移 → ✅ create_all（因为迁移成功）
```

**未验证**：`raise` 分支未实测（迁移一直成功）。如果哪天迁移失败，注意观察是否真的拒绝启动。

---

### 阶段 3：供应商权限漏洞（P0 安全）

**问题**：`app/routers/purchase_orders.py` 里 `create_supplier` / `update_supplier` / `delete_supplier` 三处使用 `RequirePermission("procurement:view")`（只读权限），任何只读角色能删供应商。

**修复**：三处改为 `RequirePermission("procurement:manage")`。`get_suppliers`（列表查询）保持 `view`。

**验证**：
```bash
grep -n "RequirePermission" app/routers/purchase_orders.py
# 41: view （get，不动）
# 51: manage（create）
# 76: manage（update）
# 103: manage（delete）
# 128: manage（pay，原本就对）
```

**行为变化**：`procurement:view` 用户点"新建/修改/删除供应商"会收到 403。**前端如果没处理 403 弹窗，可能显示"操作失败"无细节** —— 这是后续一个前端小改进点。

---

### 阶段 4：收货路径浮点精度（P0 数据正确性）

**问题**：收货累加 `debt_usd` 时浮点误差跨记录传播。

**根因**：
```python
# 旧代码 purchase_orders.py
total_order_amount = total_order_amount_cents / 100  # ← float 除法
.values(debt_usd=func.coalesce(Supplier.debt_usd, 0.0) + total_order_amount)  # ← 不 round
```

两次 100.10 收货后，`debt_usd = 200.20000000000002`（漂移）。

**修复**（2 行）：
```python
# purchase_orders.py:370
total_order_amount = Decimal(total_order_amount_cents) / Decimal("100")

# purchase_orders.py:373-376
.values(debt_usd=func.round(
    func.coalesce(Supplier.debt_usd, 0.0) + float(total_order_amount), 2
))
```

**为什么这就够了**：`float` 本身不是问题，"无边界地累加 float"才是。每次写入 `round(..., 2)` 让误差不跨记录传播。和付款路径（第 155-156 行）风格统一。

**验证**：
```
收货 100.10 → 100.10
收货 100.10 → 200.20  ← 不漂
付款 150.00 →  50.20  ← 不漂
```

**未解决**：快照型金额（`OrderItem.price_usd`、`Order.total_usd`、POS 各字段、`bcv_rate`）仍是 `float`，但它们是写一次只读，**不参与累加**，精度可接受。**不要贸然把它们改成 Decimal**。

---

### 阶段 5：供应商欠款审计脚本

**新增文件**：`scripts/audit_supplier_debt.py`

**功能**：
```
真值 = sum(received PO 按 items_json 重算) - sum(付款 amount_usd)
diff = debt_usd - 真值
|diff| > 0.005 → 标记漂移
```

**关键设计**：
- 真值用 `items_json` 重算，**不用** `total_amount_usd`（后者可能已经漂）
- 默认 dry-run，`--fix` 前自动备份到 `backups/`
- 只算 `status='received'` 的 PO
- 孤儿付款记录只报告不删除

**用法**：
```bash
python scripts/audit_supplier_debt.py          # 只报告
python scripts/audit_supplier_debt.py --fix    # 修复（需交互确认）
python scripts/audit_supplier_debt.py --fix --yes  # 跳过确认
```

**当前状态**：`elias` 供应商 dry-run 输出 `0 漂移`。

---

### 阶段 6：开启 SQLite 外键强制

**问题**：`PRAGMA foreign_keys = 0`（SQLite 默认）。所有 `foreign_key=` 声明从未真正强制。

**修复**：`app/database.py` 的 `engine` 之后加：
```python
from sqlalchemy import event

if DATABASE_URL.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def _enable_sqlite_foreign_keys(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
```

**现有真外键（只有 2 个）**：
- `PurchaseOrder.supplier_id → suppliers.id`
- `OrderItem.order_id → orders.id`

**其他"逻辑外键"**（`SupplierPaymentRecord.supplier_id` 等）不受这个 PRAGMA 影响。

**验证**：
```bash
python -c "from app.database import engine; from sqlalchemy import text; print(engine.connect().execute(text('PRAGMA foreign_keys')).scalar())"
# 预期：1
```

**风险**：所有未来 DELETE 都会被真正检查。已确认 9 个删除路径全部安全（`delete_supplier` 有 `has_po` 保护）。

---

### 阶段 7：SupplierPaymentRecord 加外键 + created_at 改 datetime

**改动**（`app/models.py`）：
```python
class SupplierPaymentRecord(SQLModel, table=True):
    __tablename__ = "supplierpaymentrecord"

    id: Optional[int] = Field(default=None, primary_key=True)
    supplier_id: int = Field(foreign_key="suppliers.id", index=True)  # ← 加 foreign_key
    # ...
    created_at: NaiveDatetime = Field(                          # ← 从 str 改
        default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )
```

**迁移**：`alembic/versions/a1b2c3d4e5f6_supplier_payment_record_fk_datetime.py`
- 表是空的（0 条记录），直接 `drop + create`
- 如果表非空，`upgrade()` 会 `raise RuntimeError`（需改用 `batch_alter_table`）

**验证**：
```
写入后 type: datetime   value: 2026-10-23 01:49:54.775076
读出后 type: datetime   value: 2026-10-23 01:49:54.775076
```

**前端影响**：`grep` 确认前端未引用 `created_at`，零影响。

---

## 三、环境变量清单

| 变量                    | 默认                    | 用途                                  |
| ----------------------- | ----------------------- | ------------------------------------- |
| `TK_AUTO_CREATE_TABLES` | `1`                     | `0` = 跳过 `create_all`，仅靠 Alembic |
| `TK_STRICT_MIGRATION`   | 空                      | `1` = 迁移失败强制拒绝启动            |
| `TK_STRICT_SECURITY`    | 空                      | `1` = 弱默认凭据拒绝启动              |
| `TK_MASTER_PIN`         | `TK-PIN-2026`           | **生产必须改**                        |
| `TK_ADMIN_PASSWORD`     | `tostiyk2026`           | **生产必须改**                        |
| `TK_JWT_SECRET`         | 自动生成                | 多实例部署必须共享                    |
| `TK_CORS_ORIGINS`       | 见 `config.py`          | 生产白名单                            |
| `TK_PUBLIC_BASE_URL`    | `http://localhost:8000` | 生产改域名                            |

---

## 四、生产部署建议

```bash
# .env（生产）
TK_AUTO_CREATE_TABLES=0
TK_STRICT_MIGRATION=1
TK_STRICT_SECURITY=1
TK_MASTER_PIN=<强随机>
TK_ADMIN_PASSWORD=<强随机>
TK_JWT_SECRET=<强随机>
TK_CORS_ORIGINS=https://your-domain.com
```

**部署流程**：
1. `alembic upgrade head`（手动跑，失败就不启动）
2. 启动 `uvicorn app.main:app`
3. 迁移失败 → `TK_STRICT_MIGRATION=1` 会让应用拒绝启动

---

## 五、已知技术债 / 待办

### 🟡 优先级中

1. **快照型金额未改 Decimal** —— POS 订单、报价单等的金额字段仍是 `float`。**不建议改**（见阶段 4 说明），除非有精确对账需求。
2. **`Supplier` 缺账期字段** —— 没有 `payment_terms` / `credit_limit` / `rating`。业务上需要时再补。
3. **前端 403 无友好提示** —— 供应商权限收紧后，只读角色点写操作会静默失败。前端 `SuppliersView.vue` 需要补 403 处理。
4. **备份无保留策略** —— `backups/` 目录会无限增长。需要 `services/housekeeping.py` 定期清理。
5. **`uploads/` 无生命周期管理** —— `quotation_*.pdf` 和商品图混放，半年后失控。

### 🟢 优先级低

6. **根目录 `main.py` 与 `app/main.py` 重复** —— 根目录 `main.py` 只转发 import，容易误启动。
7. **`root package.json` 与 `frontend/package.json` 重复** —— 二选一。
8. **`system_settings.json` 是文件不是表** —— 无法审计、多实例不安全。
9. **`SupplierPaymentRecord` 的 `float` 字段** —— `amount_usd` 等仍是 `float`，理论上也应该 `round(..., 2)`。当前依赖调用侧已 round，但未在 DB 层强制。
10. **测试覆盖** —— 只有单文件 `test_erp.py`。财务/库存核心逻辑建议拆成 `tests/` 目录。

---

## 六、Commit 记录

按时间顺序，本轮应该是以下 commit（可分离回滚）：

```
fix(alembic): 重建可信迁移链并加固启动迁移失败处理
fix(purchase_orders): 供应商增改删权限从 procurement:view 收紧为 manage
fix(purchase_orders): 收货累加按分精确计算，debt_usd 数据库端 round 到 2 位
feat(scripts): 新增供应商欠款审计脚本 audit_supplier_debt.py
feat(database): SQLite 开启 PRAGMA foreign_keys=ON
feat(supplier_payment_record): 加 foreign_key + created_at 改 datetime
```

---

## 七、当前数据库状态快照（2026-10-23）

```bash
# 供应商
id=1  name=elias  debt_usd=22.20

# 采购单
2 张 received（PO-20261021-*、PO-20261022-*），总额 22.20

# 付款记录
0 条

# Alembic
current = a1b2c3d4e5f6 (head)

# 表数
17 张（含 alembic_version）
```

**如果未来发现数据异常，先跑**：
```bash
python scripts/audit_supplier_debt.py
```

---

## 八、给下一个维护者的三条忠告

1. **永远用 `alembic revision --autogenerate` + 人工 review 生成新迁移**。迁移链现在是可信的，别再用 `create_all` 或手动 `ALTER TABLE`。

2. **`app/database.py:33` 的 `create_all` 是过渡兜底**。生产环境通过 `TK_AUTO_CREATE_TABLES=0` 关闭。开发环境保留它，但**新增字段时必须同时写迁移**，否则开发环境"能用"但生产跑不起来。

3. **改金额相关代码时，任何 `+` / `-` 操作都要有边界**。`round(..., 2)` 是最低要求，`Decimal` + `quantize` 是更好选择。快照型金额（写一次只读）可以 `float`，累加型金额必须谨慎。

---

## 附：关键文件变更速查

| 文件                                 | 变更性质                                                   |
| ------------------------------------ | ---------------------------------------------------------- |
| `app/config.py`                      | 加 `AUTO_CREATE_TABLES` / `STRICT_MIGRATION`               |
| `app/database.py`                    | 加 `if AUTO_CREATE_TABLES` 判断 + `PRAGMA foreign_keys`    |
| `app/main.py`                        | `bootstrap()` 迁移失败时按需 raise                         |
| `app/models.py`                      | `SupplierPaymentRecord` 加 foreign_key + `created_at` 类型 |
| `app/routers/purchase_orders.py`     | 3 处权限 + 收货金额 round                                  |
| `alembic/versions/edf*.py`           | 加 `inspect` 幂等判断                                      |
| `alembic/versions/487*.py`           | 加 `inspect` 幂等判断                                      |
| `alembic/versions/4136*.py`          | 加 `inspect` 幂等判断                                      |
| `alembic/versions/a1b2c3d4e5f6_*.py` | 新建（SupplierPaymentRecord 迁移）                         |
| `scripts/audit_supplier_debt.py`     | 新建                                                       |

---

*文档生成时间：2026-10-23 | 对应代码状态：commit 完成后*

---

**保存方式**：把以上内容保存为项目根目录的 `NOTES.md` 或 `docs/MAINTENANCE.md`，然后 `git add` + `git commit -m "docs: 维护存档 2026-10-23"`。

下次开新对话时，**贴这个文件 + `alembic history | head -10`** 就能快速接上上下文。