这份文档记录得非常详实，但因为是分阶段补充的，导致**时间线被打断**，且**部分结论前后矛盾**（例如阶段 1 认为 autogenerate 跑通了，阶段 9 发现其实一直是空跑），同时 Commit 记录和待办事项有重复。

我为你进行了全面梳理、去重合并，并重新排布了逻辑优先级。你可以直接用下面这份最终版覆盖原有的 `📋 TOSTIYK ERP 维护存档.md`。

---

# 📋 TOSTIYK ERP 维护存档

> **记录周期**：2026-10-22 至 2026-10-23
> **目的**：让下一个维护者理解“为什么代码长这样”，以及“还有哪些坑没填”。

## 一、项目概况

| 项     | 值                                                                  |
| ------ | ------------------------------------------------------------------- |
| 项目名 | TOSTIYK ERP                                                         |
| 后端   | FastAPI + SQLModel + SQLite + Alembic                               |
| 前端   | Vue 3 + Vite + Tailwind + Playwright(E2E)                           |
| 数据库 | `tostiyk_erp.db`（生产）、`_test_erp.db`（测试，空库）              |
| 主入口 | `app/main.py`（根目录 `main.py` 已废弃，仅转发 import，容易误启动） |

---

## 二、本轮修复时间线（按发生顺序）

### 阶段 1：迁移链修复与启动兜底（P0 基础设施）

- **问题**：`alembic upgrade head` 从未真正跑通过，表全靠 `create_all` 建；且迁移失败会被 `except` 静默吞掉。
- **修复**：
  1. 把 3 个空的/`pass` 的迁移改成幂等版（`inspect(bind)` 判断存在再执行）。
  2. 新增启动开关 `TK_AUTO_CREATE_TABLES`（默认 1，生产应为 0）和 `TK_STRICT_MIGRATION`（默认空，生产应为 1）。
  3. 迁移失败时按需 `raise RuntimeError`，拒绝启动。
- **⚠️ 认知反转**：当时验证 `alembic revision --autogenerate` 输出 `pass`，误以为“零漂移”。**但在阶段 9 发现，autogenerate 早就失效了，当时的结论不成立**。

### 阶段 2：数据正确性与安全（P0 业务）

- **金额浮点漂移**：收货累加 `debt_usd` 时，使用 `Decimal` 计算，并在数据库端 `func.round(..., 2)`。**快照型金额（PO 总额等）保持 float 不动，因为它们不参与累加**。
- **权限漏洞**：`create/update/delete_supplier` 从 `RequirePermission("procurement:view")` 收紧为 `manage`。
- **外键强制**：在 SQLite 开启 `PRAGMA foreign_keys=ON`，目前只对真外键（`purchase_orders` 和 `supplierpaymentrecord`）生效。

### 阶段 3：审计与表结构（P1 维护性）

- **审计脚本**：新增 `scripts/audit_supplier_debt.py`，用 `items_json` 重算真值，不依赖可能漂移的 `total_amount_usd`。支持 `--fix` 并自动备份。
- **外键补全**：`SupplierPaymentRecord` 加 `foreign_key="suppliers.id"`，`created_at` 从 `str` 改为 `datetime`。
- **新增字段**：`Supplier` 加 `payment_terms`（账期，默认30）和 `credit_limit`（信用，默认5000）。
- **⚠️ 坑点**：过程中产生了重复迁移文件 `32f564...` 和 `ac81df...`，通过 `stamp` 退回删除后，**手写了迁移** `b1c2d3e4f5a6`。
- **⚠️ 坑点**：手写迁移时，由于列已存在，`add_column` 被跳过，导致 `server_default` 没被修正。最终通过重建 `suppliers` 表（`PRAGMA foreign_keys=OFF` -> drop -> create -> rename）手动修复了默认值。

### 阶段 4：发现严重隐患（P0 待办，见第五部分）

- **隐患 A（阶段 9）**：`alembic autogenerate` 彻底失效，永远生成 `pass`。这意味着每次加字段必须手写迁移，否则生产必炸。
- **隐患 B（阶段 10）**：阶段 3 中重建 `suppliers` 表时，可能丢失了未被注意到的索引或唯一约束。当前已补回 `ix_suppliers_name`，但未做全表对比。

---

## 三、环境变量清单

| 变量                    | 默认                    | 生产部署建议                          |
| ----------------------- | ----------------------- | ------------------------------------- |
| `TK_AUTO_CREATE_TABLES` | `1`                     | **`0`**（关闭 create_all，仅靠 Alembic） |
| `TK_STRICT_MIGRATION`   | 空                      | **`1`**（迁移失败强制拒绝启动）       |
| `TK_STRICT_SECURITY`    | 空                      | **`1`**（弱默认凭据拒绝启动）         |
| `TK_MASTER_PIN`         | `TK-PIN-2026`           | **必须改**                            |
| `TK_ADMIN_PASSWORD`     | `tostiyk2026`           | **必须改**                            |
| `TK_JWT_SECRET`         | 自动生成                | 多实例部署必须共享                    |
| `TK_CORS_ORIGINS`       | 见 `config.py`          | 生产白名单                            |
| `TK_PUBLIC_BASE_URL`    | `http://localhost:8000` | 生产改域名                            |

---

## 四、已知技术债 / 下一轮待办

### 🔴 P0：必须优先解决

1. **修复 `alembic autogenerate` 失效**：
   - **现状**：`env.py` 里有配置，模型也真实注册了，但 CLI 跑出来永远是 `pass`（疑似 `.pyc` 缓存或 import 时机问题）。
   - **对策**：清理 `__pycache__`；在 `env.py` 顶部强加 `import app.models`；如果还不行，用 `alembic revision --autogenerate --sql` 抓出对比细节。
2. **核对重建表的索引与约束**：
   - **现状**：手动重建 `suppliers` 表后，需确认没有遗漏 `models.py` 中定义的唯一或索引约束。
   - **对策**：跑 `PRAGMA index_list` 和 `PRAGMA foreign_key_check`，并与 `models.py` 逐一对比。

### 🟡 P1：需要补齐

3. **前端 403 无友好提示**：供应商权限收紧后，只读角色点写操作会静默失败或报未知错，`SuppliersView.vue` 需补 403 拦截。
4. **备份无保留策略**：`backups/` 目录无限增长，需要 `services/housekeeping.py`。
5. **`uploads/` 无生命周期管理**：报价 PDF 和商品图混放，需要按日期归档及清理。
6. **`Supplier` 的 `float` 字段**：`amount_usd` 等理论上也应该在 DB 层 `round(..., 2)`，目前依赖调用侧处理。

### 🟢 P2：长期优化

7. **根目录 `main.py` 与 `app/main.py` 重复**。
8. **根目录 `package.json` 与 `frontend/package.json` 重复**。
9. **`system_settings.json` 是文件不是表** —— 多实例部署不安全，也无法审计。
10. **测试覆盖不足** —— 后端核心逻辑目前仅单文件 `test_erp.py`，建议拆成 `tests/` 目录。

---

## 五、Commit 记录（本轮完整历史）

```text
feat(ui): mount ThemeSwitcher in header and expand e2e smoke tests
refactor(frontend): extract CRUD actions to composables and fix e2e setup
feat(api): global error interception and request_id idempotency
feat(suppliers): 加账期 payment_terms（默认30天）和信用额度 credit_limit（默认$5000）
fix(suppliers): 重建 suppliers 表修正 server_default（旧迁移写入 0/0.0）
fix(alembic): 重建可信迁移链并加固启动迁移失败处理
fix(purchase_orders): 供应商增改删权限从 procurement:view 收紧为 manage
fix(purchase_orders): 收货累加按分精确计算，debt_usd 数据库端 round 到 2 位
feat(scripts): 新增供应商欠款审计脚本 audit_supplier_debt.py
feat(database): SQLite 开启 PRAGMA foreign_keys=ON
feat(supplier_payment_record): 加 foreign_key + created_at 改 datetime
```

---

## 六、给下一个维护者的 4 条忠告

1. **不要信任 `alembic autogenerate` 直到 P0 修复**。现在它输出 `pass` 不代表没漂移。每次加字段：手写迁移 → 跑 `python -c` 确认模型已注册 → 跑 `PRAGMA table_info` 确认 DDL 已执行。
2. **永远用迁移工具，别用 `create_all` 或手动 `ALTER TABLE` 修改生产库**。生产必须设 `TK_AUTO_CREATE_TABLES=0` 且 `TK_STRICT_MIGRATION=1`。
3. **改金额累加代码时，必须有边界**。`round(..., 2)` 是最低要求，`Decimal` 是更好选择。快照型金额可用 `float`，累加型必须严谨。
4. **重建 SQLite 表后，必须核对索引和默认值**。手写重建极易丢失 `unique` 属性或 `server_default`。

---

## 七、当前数据库快照（2026-10-23 收尾）

```text
# Alembic
head = 092e79bcf78e
alembic check: No new upgrade operations detected

# 供应商
id=1 name=elias debt=22.20 terms=30 credit=5000

# 采购单与付款
2 张 received PO (总额 22.20)
0 条 payment_record

# 审计状态
audit_supplier_debt.py dry-run 输出 0 漂移
```

---

## 八、关键文件变更速查

| 文件 | 变更性质 |
| --- | --- |
| `app/config.py` | 加 `AUTO_CREATE_TABLES` / `STRICT_MIGRATION` |
| `app/database.py` | 加判断 + `PRAGMA foreign_keys` |
| `app/main.py` | 启动迁移失败时按需 raise |
| `app/models.py` | `SupplierPaymentRecord` 外键+时间；`Supplier` 加账期和额度 |
| `app/routers/purchase_orders.py` | 权限收紧 + 金额 round |
| `alembic/versions/` | 修复 3 个空迁移、手写 `b1c2...`、新建 `a1b2...` |
| `scripts/audit_supplier_debt.py` | 新建（欠款审计） |

---

**下一步行动建议**：
先花 10 分钟执行 `PRAGMA` 核对表结构（P0 第 2 点），再花 30 分钟排查 `autogenerate` 失效的原因（P0 第 1 点）。搞定后直接 `git commit -m "docs: update maintenance archive with P0 todos"` 收工休息。



# 项目上下文：TOSTIYK ERP 开发与重构（接续前文）

你好，我们正在继续开发一个名为 TOSTIYK ERP 的全栈项目。
后端：FastAPI + SQLModel + SQLite + Alembic
前端：Vue 3 + Vite + Tailwind + Playwright(E2E)

## 当前进度：
1. **前端重构完成**：App.vue 已从 1000 行瘦身至 ~700 行，CRUD 逻辑已抽离到 `useTxActions` / `usePartActions` / `useClientActions`。
2. **E2E 基建完成**：已引入 Playwright，3 个用例（登录、切 Tab、切主题）全绿。
3. **API 层重构完成**：`apiFetch` 已加入全局 500/断网拦截，并自动生成 `X-Request-Id`。
4. **后端加固完成**：修复了权限漏洞、收货浮点精度、SQLite 外键开启、新增供应商账期字段。

## 当前 Git 状态：
HEAD -> main，最新 commit 包含前端重构和 API 层加固。

## 🚨 本次对话的绝对优先级（P0）：修复 Alembic 隐患
我们遇到了一个致命问题：`alembic revision --autogenerate` 完全失效，永远生成空迁移（`pass`）。这意味着目前所有的迁移都是手写的，极易出错。同时，之前手动重建 `suppliers` 表，需要核对索引是否丢失。

## 你（AI）现在的第一个任务：
请引导我运行以下命令来诊断：
1. 打印 SQLModel metadata 和 suppliers 表的列。
2. 检查 alembic/env.py 的 import 时序。
3. 用 sqlite3 核对 suppliers 表的 index 和 foreign_key。
先不要盲目给代码，请让我把命令输出的结果贴给你，我们再决定修复方案。

（如果有余力，搞定 P0 后，我们继续做 P1：前端 403 无提示问题，以及 backups/uploads 目录的生命周期管理。）

我们要一步一步来，我每跑完一步都会把终端结果贴给你。