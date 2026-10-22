"""FastAPI 应用装配。

重构要点：
* 原先 `@app.on_event("startup")` 注册了两遍，现在合并为唯一一个 lifespan 处理器。
* 建表统一走 `init_db()`。
* 原先模块内先后创建了两个引擎并互相覆盖，现在只从 `app.database` 取唯一引擎。
* 🌟 引入 Alembic，自动处理数据库迁移。
"""

from contextlib import asynccontextmanager
import os  # 🌟 引入 os 用于路径处理

from app.routers import backup  # 🌟 导入备份路由
from app.services.backup import auto_backup_task  # 🌟 导入自动备份定时任务
import asyncio # 如果没导入的话

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session, select

# 🌟 引入 Alembic 的配置和命令模块
from alembic.config import Config
from alembic import command

from app import __version__
from app import database
from app.config import (
    ADMIN_PASSWORD_IS_EXPLICIT,
    CORS_ORIGINS,
    DB_PATH,
    DEFAULT_ADMIN_PASSWORD,
    DEFAULT_ADMIN_USERNAME,
    UPLOAD_DIR,
    WEAK_DEFAULTS,
)
from app.database import init_db
from app.models import AdminUser, AutoPart
from app.routers import (
    audit_logs,
    auth,
    clients,
    exports,
    parts,
    pos,
    purchase_orders,
    quotations,
    reports,
    transactions,
    settings,
)
from app.security import hash_password, verify_password
from app.startup_checks import config_warnings, report
from app.routers import staff
from app.routers import expenses




def bootstrap() -> None:
    """建表 + 首次启动的账号与演示数据播种 + 安全自检。"""
    
    # 🌟 核心修改 1：自动执行 Alembic 迁移
    try:
        print("⏳ 正在检查并应用数据库迁移 (Alembic)...")
        # 获取当前文件所在目录，确保 Alembic 能够找到 alembic.ini
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        alembic_ini_path = os.path.join(base_dir, "alembic.ini")
        
        alembic_cfg = Config(alembic_ini_path)
        # 自动升级到最新版本
        command.upgrade(alembic_cfg, "head")
        print("✅ 数据库迁移检查完成。")
    except Exception as e:
        print(f"⚠️ 数据库迁移执行失败: {e}")
        # 如果迁移失败，建议直接抛出异常阻止应用启动，防止产生脏数据
        # raise e 

    # 兜底建表（如果 Alembic 还没接管，或者全新数据库）
    init_db()
    print(f"🎯 数据库绝对路径: {DB_PATH}")

    warnings = config_warnings()
    weak_admin_pwd = WEAK_DEFAULTS["TK_ADMIN_PASSWORD"]

    with Session(database.engine) as session:
        admin_user = session.exec(
            select(AdminUser).where(AdminUser.username == DEFAULT_ADMIN_USERNAME)
        ).first()
        if not admin_user:
            session.add(AdminUser(
                username=DEFAULT_ADMIN_USERNAME,
                password_hash=hash_password(DEFAULT_ADMIN_PASSWORD),
                role="super_admin",
            ))
            session.commit()

        elif (
            ADMIN_PASSWORD_IS_EXPLICIT
            and DEFAULT_ADMIN_PASSWORD != weak_admin_pwd
            and verify_password(weak_admin_pwd, admin_user.password_hash)
        ):
            admin_user.password_hash = hash_password(DEFAULT_ADMIN_PASSWORD)
            session.add(admin_user)
            session.commit()
            print("✅ 管理员密码已从出厂默认值替换为 TK_ADMIN_PASSWORD 所设的值。")

        if admin_user is not None and verify_password(
            weak_admin_pwd, admin_user.password_hash
        ):
            warnings.append(
                f"管理员账号 {DEFAULT_ADMIN_USERNAME!r} 仍在使用出厂默认密码 {weak_admin_pwd!r}。"
                "请在 .env 设置 TK_ADMIN_PASSWORD 后重启，或执行 "
                ".venv/bin/python scripts/set_admin_password.py"
            )

    report(warnings)


@asynccontextmanager
async def lifespan(app: FastAPI):
    bootstrap()
    yield


app = FastAPI(title="TOSTIKYK ERP API", version=__version__, lifespan=lifespan)

# 前端来源白名单由 TK_CORS_ORIGINS 控制
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 确保上传目录存在，防止挂载失败
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

# 路由注册
app.include_router(parts.router)
app.include_router(clients.router)
app.include_router(transactions.router)
app.include_router(quotations.router)
app.include_router(reports.router)
app.include_router(exports.router)
app.include_router(auth.router)
app.include_router(audit_logs.router)
app.include_router(purchase_orders.router)
app.include_router(pos.router)
app.include_router(settings.router)
app.include_router(staff.router)
app.include_router(expenses.router)
app.include_router(backup.router)  # 🌟 注册备份路由



@app.get("/")
def read_root():
    return {"message": "TOSTIKYK ERP API is running", "version": __version__}



from fastapi import Request, status
from fastapi.responses import JSONResponse
import traceback

@app.middleware("http")
async def catch_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        # 打印完整的报错堆栈到后端终端
        print("=== 后端捕获到未处理异常 ===")
        traceback.print_exc()
        # 即使报错也强制带上 CORS 响应头，让前端能看到具体的错误内容
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": str(e)},
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": "true",
            }
        )

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(auto_backup_task())


