# Tostiyk (TK) ERP — 汽配进销存 / 报价 / POS 系统

委内瑞拉汽配业务管理系统：库存、客户挂账、采购收货、报价单 PDF、POS 收银、BCV 汇率、审计日志。

## 技术栈

| 层 | 技术 |
|---|---|
| 后端 | FastAPI + SQLModel (SQLAlchemy) + SQLite |
| 前端 | Vue 3 + Vite + Tailwind + Element Plus |
| PDF | ReportLab（中文用 华文细黑 STHeiti） |

## 目录结构

```
.
├── app/                  # 后端应用包（所有业务代码）
│   ├── main.py           #   FastAPI 实例、lifespan、CORS、路由注册
│   ├── config.py         #   路径与常量（全部基于项目根绝对路径）
│   ├── database.py       #   唯一引擎 / Session / get_session
│   ├── models.py         #   全部数据表（统一 SQLModel，含原 models.py 迁移过来的表）
│   ├── schemas.py        #   请求体 Pydantic 模型
│   ├── security.py       #   密码哈希与 JWT 令牌（标准库实现，无额外依赖）
│   ├── deps.py           #   鉴权依赖 get_current_actor / require_admin
│   ├── services/         #   可复用业务能力（审计日志 / BCV 汇率 / PDF）
│   └── routers/          #   按业务域拆分的路由（10 个模块，43 个端点）
├── main.py               # 兼容入口 + uvicorn 启动
├── test_erp.py           # 测试套件
├── frontend/             # Vue 3 前端
│   ├── .env.development  #   VITE_API_BASE（开发指向 localhost:8000）
│   ├── .env.production   #   留空 = 与后端同源
│   └── src/
│       ├── utils/api.js      #   统一请求层：地址注入 + Bearer 令牌 + 401 处理
│       ├── composables/      #   useAuth / useNotifications / useInventory /
│       │                     #   usePosCart / useClock / useGallery / useI18n
│       └── components/       #   视图组件 + 可复用弹窗（ConfirmDialog 等）
├── uploads/              # 配件图片 + 生成的报价单 PDF（不进版本库）
├── backups/              # 本地数据库备份归档（不进版本库）
└── tostiyk_erp.db        # SQLite 数据库（不进版本库）
```

## 启动

```bash
# 1. 后端
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env          # 首次运行：填入真实密钥（见下方「环境变量」）
.venv/bin/uvicorn app.main:app --reload --port 8000
#   API 文档: http://localhost:8000/docs

# 2. 前端（另开一个终端）
cd frontend
npm install
cp .env.development .env.development.local   # 如需覆盖后端地址
npm run dev            # 开发: http://localhost:5173
npm run build          # 生产: 产物在 frontend/dist
```

## 环境变量

`app/config.py` 内置了一个标准库实现的 `.env` 加载器（**不依赖 python-dotenv**，
因此启动命令不需要 `uvicorn --env-file`）。优先级为：**真实环境变量 > `.env` > 代码默认值**。

| 变量 | 说明 | 默认值 |
|---|---|---|
| `TK_JWT_SECRET` | 访问令牌签名密钥，**生产必须设置** | `dev-only-change-me` |
| `TK_TOKEN_TTL_MINUTES` | 令牌有效期（分钟） | `720` |
| `TK_MASTER_PIN` | 管理员密码重置密钥 | `TK-PIN-2026` |
| `TK_ADMIN_USER` / `TK_ADMIN_PASSWORD` | 全新数据库初始化时的管理员 | `admin` / `tostiyk2026` |
| `TK_CORS_ORIGINS` | 允许跨域的前端来源，逗号分隔 | `http://localhost:5173,http://127.0.0.1:5173` |
| `TK_PUBLIC_BASE_URL` | 报价单 PDF 下载地址前缀 | `http://localhost:8000` |

## 鉴权

登录 `POST /api/auth/login` 返回 `access_token`，之后请求带 `Authorization: Bearer <token>`。

```bash
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"tostiyk2026"}' | python3 -c "import sys,json;print(json.load(sys.stdin)['access_token'])")
curl http://localhost:8000/api/staff -H "Authorization: Bearer $TOKEN"
```

- 密码使用 **scrypt**（每用户独立随机盐）；迁移前遗留的无盐 SHA-256 哈希仍可登录，
  并在登录成功那一刻**自动就地升级**为 scrypt。
- 令牌为 HMAC-SHA256 签名的 HS256 JWT，密钥由 `TK_JWT_SECRET` 提供。

## 前端构建与体积

业务页签全部走 `defineAsyncComponent` 按需加载，各自切分为独立 chunk。

| | 优化前 | 优化后 |
|---|---|---|
| 首屏 JS + CSS | 1707 kB（gzip 454 kB） | **206 kB（gzip 64 kB）** |
| CSS | 411.9 kB | 51.4 kB |
| 全部 JS 合计 | 1295 kB（单 chunk） | 240 kB（19 个 chunk） |

两处主要优化：

1. **移除 Element Plus**：模板中并无任何 `el-*` 组件或 `ElMessage` 调用，
   唯一实际使用的是全局注册的图标（`Sidebar.vue` 的 `<Cpu>`，未 import 而靠全局解析）。
   改为从 `lucide-vue-next` 显式导入后，整个依赖可安全删除。
   > ⚠️ 教训：全局注册的组件会被裸标签隐式引用，grep `el-` 查不出来。
   > 排查方式：找出模板里用了 PascalCase 标签但本文件未 import 的组件。
2. **页签级代码分割**：11 个业务页签改为 `defineAsyncComponent`，
   首屏只加载仪表盘，其余页签在点击时才下载。

### ⚠️ `.env.production` 需要同源反向代理

`frontend/.env.production` 里 `VITE_API_BASE` 为空 → 前端向后端发**同源**请求。
因此生产部署必须由 Nginx 等把 `/api` 与 `/uploads` 反代到后端，例如：

```nginx
location /api/     { proxy_pass http://127.0.0.1:8000; }
location /uploads/ { proxy_pass http://127.0.0.1:8000; }
location /         { root /path/to/frontend/dist; try_files $uri /index.html; }
```

若前后端不同源，则必须同时设置 `VITE_API_BASE` **和** 后端 `TK_CORS_ORIGINS`
（否则会被 CORS 白名单拒绝——这是预期行为，`vite preview` 默认端口 4173 不在白名单内）。

## 默认账号

| 项 | 值 |
|---|---|
| 管理员 | `admin` / `tostiyk2026` |
| 重置密钥 | `TK-PIN-2026` |

> ⚠️ 以上仅为代码默认值，公网部署前务必通过环境变量替换。

> ⚠️ 以上为代码内硬编码的默认凭据，公网部署前必须修改（见"安全待办"）。

## 数据库与备份

- 数据库文件固定为项目根目录的 `tostiyk_erp.db`（绝对路径，与启动目录无关）。
- 运行中下载备份：`GET /api/backup/download`。
- 手工备份：`cp tostiyk_erp.db backups/tostiyk_erp_$(date +%F).db`。

## 不进版本库的资源

| 路径 | 原因 | 说明 |
|---|---|---|
| `STHeiti Light.ttc` | 55MB 二进制字体 | PDF 中文渲染依赖，缺失时中文报价单会报字体异常。换机器需手工拷贝；如需入库：`git add -f "STHeiti Light.ttc"` |
| `*.db` | 运行期数据 | 用 `backups/` 或备份接口 |
| `uploads/` | 用户上传内容 | 配件图片与生成的 PDF |
| `backups/` | 本地归档 | 含重构前的数据库快照 |

## 安全状态

已处理：

1. ✅ 鉴权改为 **JWT（HS256）Bearer 令牌**，废弃可伪造的 `X-Username` / `X-Role` 请求头。
   伪造头访问受保护接口一律返回 401。
2. ✅ 密码哈希由无盐 SHA-256 升级为 **scrypt**；存量哈希在登录成功时自动就地升级。
3. ✅ `TK-PIN-2026` 与默认密码改为环境变量可覆盖，并提供 `.env.example`。
4. ✅ CORS 由 `allow_origins=["*"]` 收敛为 `TK_CORS_ORIGINS` 白名单。
5. ✅ **JWT 密钥不再有可预测默认值**：未配置 `TK_JWT_SECRET` 时自动生成随机密钥并
   写入 `.jwt_secret`（0600，已 gitignore），重启复用。
6. ✅ **启动安全自检**：仍在用出厂弱默认值会打印醒目告警；
   `TK_STRICT_SECURITY=1` 时**直接拒绝启动**。
7. ✅ **管理员密码可轮换**：`scripts/set_admin_password.py`（带强度校验）；
   若 `.env` 配了 `TK_ADMIN_PASSWORD` 而库里仍是出厂密码，启动时自动替换。
8. ✅ **登录/重置接口防爆破限流**：滑动窗口 + 锁定，超限返回 429 与 `Retry-After`。

仍待处理：

1. ⚠️ 限流状态存在**进程内存**中：如改用 `uvicorn --workers N` 或多副本部署，
   需把 `app/services/ratelimit.py` 的 `_buckets` 换成 Redis 等共享存储。
2. ⚠️ 已签发的令牌在过期前始终有效（默认 12 小时）；改密码不会使其失效，
   需要更换 `TK_JWT_SECRET` 或删除 `.jwt_secret` 后重启。

### 凭据管理速查

```bash
# 生成强随机值
.venv/bin/python -c "import secrets; print(secrets.token_urlsafe(48))"

# 改管理员（或店员）密码
.venv/bin/python scripts/set_admin_password.py
.venv/bin/python scripts/set_admin_password.py --username cashier_juan

# 让所有已签发令牌立刻失效
rm -f .jwt_secret   # 或在 .env 换一个 TK_JWT_SECRET，然后重启
```

| 环境变量 | 默认 | 说明 |
|---|---|---|
| `TK_JWT_SECRET` | 自动生成 | 令牌签名密钥；多实例必须共享同一值 |
| `TK_MASTER_PIN` | 弱默认值 ⚠️ | 重置管理员密码的密钥 |
| `TK_ADMIN_PASSWORD` | 弱默认值 ⚠️ | 仅用于初始化；库中仍是出厂密码时启动会自动替换 |
| `TK_STRICT_SECURITY` | 空 | `1` = 检出弱默认凭据就拒绝启动 |
| `TK_LOGIN_MAX_ATTEMPTS` | `5` | 窗口内允许的失败次数 |
| `TK_LOGIN_WINDOW_SECONDS` | `300` | 失败计数窗口 |
| `TK_LOGIN_LOCKOUT_SECONDS` | `900` | 超限后的锁定时长 |
| `TK_TRUST_PROXY` | 空 | 在反代后面设 `1`，限流才按 `X-Forwarded-For` 取真实 IP |

> ⚠️ `TK_TRUST_PROXY` 直连暴露时**必须留空**，否则攻击者可伪造 `X-Forwarded-For`
> 把头换掉从而绕过限流。

## 并发安全

**库存扣减必须使用原子条件更新**，不能用 `select(...).with_for_update()`：

```python
# ❌ 错误：SQLite 不支持 SELECT ... FOR UPDATE，with_for_update() 被静默忽略，
#    "先读库存再写库存"之间存在竞态 → 并发超卖
part = session.exec(select(AutoPart).where(...).with_for_update()).first()
if part.stock < qty: raise ...
part.stock -= qty

# ✅ 正确：原子条件更新 + 校验影响行数
result = session.exec(
    update(AutoPart)
    .where(AutoPart.oem == oem, AutoPart.stock >= qty)
    .values(stock=AutoPart.stock - qty)
)
if result.rowcount == 0:
    session.rollback()
    raise HTTPException(status_code=400, detail="库存不足")
```

已按此修复 `app/routers/quotations.py`（开单出库）与 `app/routers/pos.py`（POS 收银）。

**另一个并发/一致性陷阱**：`app/services/audit.py` 的 `log_action()` 内部会 `session.commit()`。
因此**绝不能在多步写操作的循环中调用它** —— 它会把前面几步提前提交，导致后续步骤失败时
无法整体回滚。

`/api/quotations/generate` 曾因此出现"拒单但已扣库存"：一单两件，第二件库存不足返回 400，
第一件的库存却已被 `log_action` 提交。修法是：循环内只做扣减并记录明细，等**所有校验
（含挂账信用额度）都通过后**才统一落审计日志。

## 测试

`test_erp.py` 使用独立的**文件型** SQLite 测试库（`_test_erp.db`，已 gitignore）：

- 不能用内存库 + `StaticPool`：它让所有线程共享同一条连接，并发用例必然抛
  `sqlite3.InterfaceError: bad parameter or other API misuse`。
- `run_app_lifespan` fixture 会把 `app.database.engine` 临时指向测试库后再进入
  `with TestClient(app)`，因此 lifespan 真正执行，且**不会**把演示数据播种到生产库。
- `setup_database` fixture 每个用例前后各 `drop_all` 一次，保证用例从空库开始。

## 历史问题处理记录

| # | 问题 | 状态 |
|---|---|---|
| 1 | `test_root` 断言与 `/` 响应文案不一致 | ✅ 已修复 |
| 2 | 并发用例因共享 SQLite 连接间歇崩溃 | ✅ 已修复（改文件型测试库，`InterfaceError` 归零） |
| 3 | **并发超卖**（`with_for_update()` 在 SQLite 上无效） | ✅ 已修复（原子条件 UPDATE） |
| 4 | `TestClient` 未触发 lifespan | ✅ 已修复（session 级 fixture + 引擎隔离） |
| 5 | 4 张无引用、0 行的历史空表 | ✅ 已清理（备份在 `backups/pre_drop_tables_*.db`） |
| 6 | **开单部分生效**：`log_action` 在循环内 `commit`，导致拒单但已扣库存 | ✅ 已修复（审计日志移出循环 + 拒单时 `rollback`） |
| 7 | **POS 订单主表与明细分两次 `commit`**，第二次失败会留下无明细的脏订单 | ✅ 已修复（改为 `flush()` + 单次原子 `commit`） |
| 8 | **并发退货重复回滚库存**：先读 `order.status` 再判断，3 个并发退货全部成功 | ✅ 已修复（带条件的原子 `UPDATE` 抢占退货权） |
| 9 | **手工出入库**：`log_action` 提前 `commit`，流水插入失败时库存已被改掉 | ✅ 已修复（库存+流水单次提交） |
| 10 | **手工出库先读后写**：库存 1 件时 5 个并发出库全部成功 | ✅ 已修复（原子条件扣减） |
| 11 | **欠款/收货读改写丢失更新**：并发还款 5×10 只扣 1 次 | ✅ 已修复（`SQL 级 max()` / 自增） |

| 12 | **同一秒内建两张单会 500**：`po_no` / `order_no` 用秒级时间戳且有 UNIQUE 约束 | ✅ 已修复（`app/services/numbering.py` 加毫秒+序号+随机后缀） |

残留观察项（经审计确认属有意行为，非缺陷）：

- `/api/backup/download` 会读取真实数据库文件 —— 这是该接口的正确语义。
- `POST /api/import/parts` 里 `existing.stock = stock_val` 是 **CSV 绝对值赋值**
  （CSV 即数据源），不是自增，因此天然是 last-write-wins；导入属管理员批量操作，
  与销售并发时以最后一次导入为准。

## 数据一致性规则（改代码前必读）

这个项目在 SQLite 上跑，**三件事必须遵守**：

### 1. 多步写操作只能有一次 `commit()`，需要主键用 `flush()`

```python
session.add(new_order)
session.flush()          # ✅ INSERT 在本事务内执行并回填 id，但不提交
# session.commit()       # ❌ 提前提交 → 后续步骤失败时无法整体回滚

for item in payload.items:
    session.add(OrderItem(order_id=new_order.id, ...))
session.commit()         # 唯一一次提交，要么全成功要么全不生效
```

### 2. 库存/欠款等数值变动必须用 SQL 级原子表达式，不能"先读后写"

```python
# ❌ 先读后写：并发时 5 个请求都读到 stock=1，全部通过 → 超卖 + 丢失更新
part = session.exec(select(AutoPart).where(...)).first()
if part.stock < qty: raise ...
part.stock -= qty

# ✅ 条件自减 + 校验影响行数
changed = session.exec(update(AutoPart)
                       .where(AutoPart.oem == oem, AutoPart.stock >= qty)
                       .values(stock=AutoPart.stock - qty))
if changed.rowcount == 0:
    session.rollback(); raise HTTPException(400, "库存不足")

# ✅ 无条件自增 / 下限钳制
session.exec(update(AutoPart).where(...).values(stock=AutoPart.stock + qty))
session.exec(update(Client).where(...).values(debt=func.max(0.0, Client.debt - amount)))
```

> `with_for_update()` 在 SQLite 上会被**静默忽略**，不能拿来当行锁用。

### 3. 状态流转也要用带条件的原子 `UPDATE`，不能先读后写

```python
# ❌ 3 个并发退货请求全部读到 status="COMPLETED"，全部通过
# ✅ 由数据库保证只有一个事务能改成功
claimed = session.exec(update(Order)
                       .where(Order.id == order_id, Order.status != "REFUNDED")
                       .values(status="REFUNDED"))
if claimed.rowcount == 0:
    session.rollback(); raise HTTPException(400, "该订单已经退货")
```

### ⚠️ `log_action()` 内部会 `commit()`

`app/services/audit.py` 的 `log_action()` 自带 `commit()`，因此：

- **绝不能在多步写操作的中间调用它** —— 它会把前面的改动提前落库；
- 正确位置是**数据写完之后**（作为本事务的最后一步），或业务 `commit()` 之后（纯审计）。

历史上 #6（开单部分生效）与 #9（出入库库存/流水不一致）都是踩了这个坑。


## 已摘除的无效前端入口

前端历史上调用了两个后端**从未实现**的接口，对应按钮已移除（2026-10-14）：

| 前端调用 | 状态 | 影响 |
|---|---|---|
| `POST /api/clients/payment` | ❌ 后端无此路由 | 「登记还款/销账」按钮已移除 |
| `GET /api/clients/{id}/statement/pdf` | ❌ 后端无此路由 | 「📄 对账单」按钮已移除 |

> 注意：后端**存在**一个可用的 `POST /api/clients/repay`（见 `app/routers/clients.py`），
> 走 JSON 请求体、会自动折算币种并写入还款流水与审计日志。
> 若日后要恢复还款功能，应把前端接到这个接口上，而不是恢复已删除的 `clients/payment`。

## 数据库中的历史空表

4 张无引用、0 行的历史空表已于 2026-10-14 清理完毕（删除前备份在 `backups/pre_drop_tables_*.db`）：

```sql
-- 已执行，仅作记录
DROP TABLE products;              -- 被遮蔽的 Product 模型遗留
DROP TABLE part_cross_references;
DROP TABLE inventory_transactions;  -- 注意：在用的是无下划线的 inventorytransaction
DROP TABLE inventorytransactions;
```





TOSTIYK ERP (汽车配件多币种经营系统)
├── 1. 基础与安全层
│   ├── 登录与鉴权 (JWT Token, Token复核拦截 401)
│   ├── 权限控制 (角色: 超管/店长/收银/仓管; 细粒度权限键值控制)
│   └── 多语言支持 (中文, 西班牙语, 英语无缝切换)
│
├── 2. 数据看板 (Dashboard)
│   ├── 核心指标 (总资产USD/Bs, 累计销售, SKU总数, 低库存预警)
│   └── 快捷导航
│
├── 3. 仓储与商品 (Parts & Inventory)
│   ├── 档案管理 (OEM, 品名, 库位, 进价, 售价, 税率)
│   ├── 图片管理 (多图上传与画廊查看)
│   ├── 侧边栏详情 (抽屉式只读/编辑，含毛利润计算)
│   └── 批量导入 (CSV模板下载与导入)
│
├── 4. 销售与收银 (POS Desk)
│   ├── 商品检索 (快捷键 / 呼出，OEM/名称模糊搜索)
│   ├── 客户挂载 (快捷新建与选择，特殊纳税人标识)
│   ├── 购物车 (行选中高亮，*号乘数语法)
│   ├── 混合支付 (Cash USD, Cash Bs, Pago Movil, Card POS，快捷键F4-F7)
│   ├── 报价模式 (备注输入，生成PDF，不扣减库存)
│   ├── 历史报价载入 (侧边栏直接拉取历史记录填充购物车)
│   ├── 云端挂单 (暂存订单，支持恢复与作废)
│   └── 出单与打印 (自动调起 80mm 热敏小票打印)
│
├── 5. 客户与账本 (Clients)
│   ├── 档案与欠款 (RIF税号，客户分类)
│   ├── 赊账还款 (多币种收款，实时汇率折算)
│   └── 客户欠款总览联动
│
├── 6. 采购与供应商 (Procurement)
│   ├── 供应商管理 (档案，欠款，付款核销)
│   ├── 采购建单 (选择供应商，搜索添加商品)
│   ├── 确认收货 (联动库存增加，更新商品成本价)
│   └── 智能补货 (筛选低于5个库存的商品一键建单)
│
├── 7. 财务与报表 (Financials)
│   ├── 核心指标 (营收，成本，日常开支，应收欠款，净利润)
│   ├── 图表分析 (ECharts 营收利润柱状图，支付渠道环形图)
│   ├── 每日利润流水 (按时间过滤，多币种展示)
│   └── 导出报表 (多语言表头的 CSV 导出)
│
├── 8. 进销存流水 (Transactions)
│   ├── 流水列表 (全部/出库/入库过滤)
│   ├── 详情抽屉 (显示操作金额、关联订单、执行人)
│   └── 手工补录与作废 (单据删除自动回滚库存)
│
└── 9. 系统运维 (System)
    ├── 日常开支 (房租工资登记，折合USD)
    ├── 收银交接对账 (系统应盘金额 vs 收银员实盘金额，盈亏计算)
    ├── 审计日志 (操作记录追踪，CSV导出)
    └── 数据备份 (DB下载，VACUUM清理)
