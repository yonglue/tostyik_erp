"""FastAPI 应用装配。

重构要点：
* 原先 `@app.on_event("startup")` 注册了两遍（一次建 SQLAlchemy 表、一次建 SQLModel 表
  并种数据），现在合并为唯一一个 lifespan 处理器，建表统一走 `init_db()`。
* 原先模块内先后创建了两个引擎并互相覆盖，现在只从 `app.database` 取唯一引擎。
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session, select

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


def bootstrap() -> None:
    """建表 + 首次启动的账号与演示数据播种 + 安全自检。

    这里通过 `database.engine` 动态取引擎（而非在导入时静态绑定），
    以便测试可以把引擎替换成隔离的测试库，避免测试污染生产数据库。
    """
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
            # 运维已在 .env 配了强密码，而库里还是出厂弱密码 → 一次性替换掉。
            # 只在"当前确实是出厂密码"时才动手，避免覆盖用户后来自己改的密码。
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

# 前端来源白名单由 TK_CORS_ORIGINS 控制（见 app/config.py）
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

# 路由注册顺序与原 main.py 中的定义顺序保持一致
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


@app.get("/")
def read_root():
    return {"message": "TOSTIKYK ERP API is running", "version": __version__}