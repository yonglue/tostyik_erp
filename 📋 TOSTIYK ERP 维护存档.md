- - # 📋 TOSTIYK ERP 核心维护交接文档
  
    > **更新周期**：2026-10-22 至 2026-10-23
    > **文档目的**：记录系统核心底层重构、前端体验升级以及未来交接注意事项，避免回退或误改。
  
    ---
  
    ## 一、项目技术栈与架构
  
    | 维度         | 技术方案                                                     |
    | :----------- | :----------------------------------------------------------- |
    | **业务定位** | 面向委内瑞拉市场的汽配 ERP + POS 系统（支持双币种、BCV 汇率） |
    | **后端**     | FastAPI + SQLModel + SQLite + Alembic                        |
    | **前端**     | Vue 3 + Vite + Tailwind CSS + Playwright (E2E)               |
    | **核心数据** | `tostiyk_erp.db`（生产库）、`_test_erp.db`（空测试库）       |
    | **主入口**   | `app/main.py`（根目录的 `main.py` 已废弃，仅作转发）         |
  
    ---
  
    ## 二、核心重构与优化纪实
  
    ### 1. 后端基建与数据安全 (2026-10-22)
    - **迁移链修复**：修复了 3 个空的/`pass` 的历史迁移，改为幂等版（`inspect(bind)`）。新增 `TK_AUTO_CREATE_TABLES` 和 `TK_STRICT_MIGRATION` 环境变量，迁移失败可强制拒绝启动。
    - **外键强制**：在 `database.py` 中开启 SQLite `PRAGMA foreign_keys=ON`。目前真外键覆盖 `purchase_orders` 和 `supplierpaymentrecord`。
    - **金额精度**：收货累加 `debt_usd` 改为 `Decimal` 计算，并在数据库端 `func.round(..., 2)`。**快照型金额（PO总额等）保持 float 不动，不参与累加。**
    - **权限收紧**：供应商的增、改、删权限从 `procurement:view` 收紧为 `procurement:manage`。
    - **表结构升级**：`Supplier` 新增 `payment_terms`（账期）和 `credit_limit`（额度）；`SupplierPaymentRecord` 补齐外键与时间字段。
  
    ### 2. 前端深度重构与 UI 升级 (2026-10-23)
    - **App.vue 史诗级瘦身**：从 1002 行降至 ~700 行。抽离了所有的 CRUD 业务动作，封装为 `useTxActions`、`usePartActions`、`useClientActions`。
    - **API 层拦截器**：重构 `apiFetch`，全局接管 401/403/500 和网络断开，并自动为所有请求生成 `X-Request-Id` 头以实现幂等。
    - **E2E 基建**：引入 Playwright，编写了 3 个核心用例（登录、切 Tab、切主题），耗时不到 2 秒。
    - **深色模式 (Dark Mode)**：实现了极简的“单点循环切换”按钮。通过 `style.css` 的全局 CSS 补丁，强制抹平了所有组件写死的浅色背景和边框，彻底告别深色模式下的“白块刺眼”问题。
    - **客户资料与体验优化**：
      - 新增 `store_name`（店铺名）字段，将“联系人”与“店铺名”完美拆分。
      - `ClientsView` 排版大修：主显店铺名，副显联系人；地址、金额强制单行/两行截断；补齐了完整的编辑态和分页功能（`pageSize=10`）。
    - **分页与审计统一**：`PartsView`、`InventoryAuditView`、`ClientsView`、`AuditLogsView` 全量接入统一的高级分页组件；盘点数据跨页不丢失；审计日志适配深色模式，且“导出 CSV”功能支持全量导出当前筛选结果。
  
    ### 3. 批量导入导出工具重构 (2026-10-23)
    - **导出模板升级**：引入 `openpyxl`，生成了带深蓝色加粗表头、自适应列宽的高级 `.xlsx` 模板。
    - **导入引擎重写**：
      - 后端完美兼容 `.xlsx` 和 `.csv`，智能识别中英文字段（如 `OEM编号` 和 `oem`）。
      - **解决路由冲突**：注释/删除了 `parts.py` 中遗留的旧导入接口，确保请求命中 `exports.py` 中的新接口。
      - **前端体验**：改用 `XMLHttpRequest` 替代 `fetch`，实现真实的上传进度条。导入完成后，精准弹出“成功 N 条 / 跳过 M 条”，并列出前 5 个错误的行号和原因。
    - **工程化清理**：删除了根目录下的冗余文件，编写了极其严格的 `.gitignore`（全面保护 `.jwt_secret`、`*.db`、`uploads/`、`backups/`）。
  
    ---
  
    ## 三、环境变量与生产部署清单
  
    | 变量                    | 默认值         | 生产建议       | 说明                       |
    | :---------------------- | :------------- | :------------- | :------------------------- |
    | `TK_AUTO_CREATE_TABLES` | `1`            | **`0`**        | 关闭自动建表，仅靠 Alembic |
    | `TK_STRICT_MIGRATION`   | 空             | **`1`**        | 迁移失败时拒绝启动         |
    | `TK_STRICT_SECURITY`    | 空             | **`1`**        | 弱默认凭据拒绝启动         |
    | `TK_MASTER_PIN`         | `TK-PIN-2026`  | **必须改**     | 超级密码重置 PIN           |
    | `TK_ADMIN_PASSWORD`     | `tostiyk2026`  | **必须改**     | 默认管理员密码             |
    | `TK_JWT_SECRET`         | 自动生成       | 多实例必须共享 | JWT 签名密钥               |
    | `TK_CORS_ORIGINS`       | 见 `config.py` | 生产白名单     | 跨域限制                   |
  
    ---
  
    ## 四、遗留技术债（下一轮待办清单）
  
    ### 🔴 P0：必须优先解决（终极雷区）
    1. **修复 `alembic autogenerate` 失效**：
       - **现状**：`env.py` 配置正常，但 `alembic revision --autogenerate` 永远生成空迁移（`pass`）。目前所有迁移全为手写，极易遗漏。
       - **对策**：清理 `__pycache__`；在 `env.py` 顶部强加 `import app.models`；如果还不行，用 `alembic revision --autogenerate --sql` 抓对比细节。
    2. **核对重建表的索引与约束**：
       - **现状**：之前手动重建 `suppliers` 表，需确认没有遗漏唯一或索引约束。
       - **对策**：跑 `PRAGMA index_list` 和 `PRAGMA foreign_key_check` 并与 `models.py` 对比。
  
    ### 🟡 P1：需要补齐的坑
    3. **备份与上传目录无生命周期**：`backups/` 和 `uploads/` 无限增长，需编写 `housekeeping.py` 定期清理。
    4. **`Supplier` 的浮点字段**：`amount_usd` 理论上也应 `round(..., 2)`，目前依赖调用侧处理。
  
    ### 🟢 P2：长期架构优化
    5. **`system_settings.json` 是文件不是表**：多实例部署不安全，建议未来迁入数据库。
    6. **测试覆盖不足**：仅单文件 `test_erp.py`，建议拆出 `tests/` 目录。
  
    ---
  
    ## 五、给下一个维护者的 5 条忠告
  
    1. **永远用 `alembic revision --autogenerate` + 人工 review 生成新迁移**。迁移链现在可信，别再用 `create_all` 或手动 `ALTER TABLE`。生产环境的 `TK_AUTO_CREATE_TABLES` 必须是 `0`。
    2. **改金额累加代码时，必须有边界**。`round(..., 2)` 是最低要求，`Decimal` 是更好选择。快照型金额（只写一次）可用 `float`，累加型必须严谨。
    3. **重建 SQLite 表后，必须核对索引和默认值**。手写重建极易丢失 `unique` 属性或 `server_default`。改完跑一遍 `alembic check`。
    4. **不要信任 `alembic autogenerate` 的 `pass`**。如果生成空迁移，先用 `alembic check` 独立判断是否有漂移。新加字段必须验证 `models.py` 注册且 DDL 已执行。
    5. **前端改代码警惕 `computed` 和重复 `import`**。不要直接改 computed 的 `.value`，调用现成的 `showXxx()` 方法；插入代码前确认光标位置，防重复粘贴。
  
    ---
  
    ## 六、当前数据库状态快照 (2026-10-23 收尾)
  
    ```text
    # Alembic 状态
    head = 092e79bcf78e
    alembic check: No new upgrade operations detected
    
    # 核心数据
    供应商: id=1 name=elias debt=22.20 terms=30 credit=5000
    采购单: 2 张 received PO (总额 22.20)
    付款记录: 0 条





## 七、关键 Commit 记录

text

```
feat(ui): add pagination and dark mode to audit logs, split client and store names
feat(import): upgrade bulk import to excel template with progress bar and detailed error reporting
fix(ui): implement global dark mode overrides and unify pagination across inventory views
chore: clean up project structure and add comprehensive .gitignore for sensitive files
feat(ui): mount ThemeSwitcher in header and expand e2e smoke tests
refactor(frontend): extract CRUD actions to composables and fix e2e setup
feat(api): global error interception and request_id idempotency
fix(suppliers): 重建 suppliers 表修正 server_default（旧迁移写入 0/0.0）
fix(alembic): 重建可信迁移链并加固启动迁移失败处理
fix(purchase_orders): 供应商增改删权限从 procurement:view 收紧为 manage
refactor(ui): split POS and Quotation views, fix cart clearing bug, and add E2E tests
```





---

### 二、Git 提交命令

今天的动作很多，但归结起来是两块：**拆分客户字段+分页**，以及**后端接口放宽+补齐**。你可以直接在终端复制并执行以下命令：

```bash
git add .
git commit -m "feat(ui): add client store_name split, unified pagination, and audit log dark mode

- Split client name and store_name in DB, API, and UI.
- Add PUT /api/clients/{id} for editing.
- Relax phone and RIF regex validations.
- Add full pagination for Clients, Audit Logs, and Inventory Audit views.
- Apply global dark mode patches to ClientsView and AuditLogsView."
```





### 4. 遗留技术债彻底清空 (2026-10-24)
- **修复 Alembic 瞎眼问题**：在 `alembic/env.py` 中补上了缺失的 `import app.models`。现在 `alembic autogenerate` 已完全恢复正常，并且测试确认当前数据库与模型零漂移。
- **验证表结构完整性**：确认 `suppliers` 表重建后，`ix_suppliers_name` 唯一索引仍然完好无损。





### 4. 核心页面架构拆分与 E2E 深度测试 (2026-10-24)
- **彻底拆分 POS 与报价**：将原本混合了收银与报价的“缝合怪”页面，重构为两个完全独立的页面：
  - `PosView.vue`（快速收银）：纯净的现金/刷卡/Pago Movil 结账界面，不含挂账功能。
  - `QuotationView.vue`（开单报价）：专门处理生成报价单 PDF 和全单挂账（Fiado）。
  - 同步更新了 `App.vue` 的异步路由和 `Sidebar.vue` 的菜单项，并补齐了 `pos` 和 `quotation` 的多语言配置。
- **权限静默失败修复**：在 `SuppliersView.vue` 中，利用 `usePermissions` 对“新建/编辑/删除”按钮进行了 `v-if` 级别的隐藏，彻底解决了越权访问引发的全局 403 弹窗冲突。
- **E2E 业务防弹衣**：新增了 `pos-quote.spec.js` 测试文件，通过 `data-testid` 精准定位，覆盖了“快速收银成功清空购物车”和“报价挂账成功清空购物车”两个核心业务闭环。
- **顺手修复的隐藏 Bug**：在编写 E2E 测试时，意外抓出并修复了“结账/挂账成功后，前端未清空购物车”的真实 Bug（通过 `props.cartItems.splice(0)` 强制执行）。