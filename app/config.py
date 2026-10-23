"""集中式配置：所有路径均基于项目根目录的绝对路径，与启动时的工作目录无关。"""

import os
import secrets
from pathlib import Path

# ──────────────────────────── 路径 ────────────────────────────
# config.py 位于 <项目根>/app/config.py，因此上溯两级即项目根
BASE_DIR: Path = Path(__file__).resolve().parent.parent

DB_PATH: Path = BASE_DIR / "tostiyk_erp.db"
UPLOAD_DIR: Path = BASE_DIR / "uploads"
FONT_PATH: Path = BASE_DIR / "STHeiti Light.ttc"
BACKUP_DIR: Path = BASE_DIR / "backups"

# SQLite 需要绝对路径，否则会随启动目录漂移到不同的库文件
DATABASE_URL: str = f"sqlite:///{DB_PATH}"

DOTENV_PATH: Path = BASE_DIR / ".env"


def load_dotenv(path: Path = DOTENV_PATH) -> None:
    """极简 .env 加载器。

    用标准库自解析，避免为了读一个文件而引入 python-dotenv
    （注意：uvicorn 的 --env-file 参数正是依赖 python-dotenv 才能工作）。

    已存在的真实环境变量优先，不会被文件里的值覆盖；
    支持 # 注释、空行、以及值两端的引号。
    """
    if not path.is_file():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


# 必须在下面任何 os.getenv 之前执行：真实环境变量 > .env > 代码默认值
load_dotenv()

# ──────────────────────── 运行期常量 ────────────────────────
DEFAULT_BCV_RATE: float = 876.7976
BCV_API_URL: str = "https://ve.dolarapi.com/v1/dolares/oficial"
BCV_SCRAPE_URL: str = "https://www.bcv.org.ve/"
BCV_SCRAPE_TIMEOUT: int = 10
BCV_API_TIMEOUT: int = 2

# 生成报价单后回传给前端的下载地址前缀
PUBLIC_BASE_URL: str = os.getenv("TK_PUBLIC_BASE_URL", "http://localhost:8000")

# 允许跨站访问的前端来源（逗号分隔）
# 单独配置以避免 allow_origins=["*"] 与 allow_credentials=True 共存的非法/不安全组合
CORS_ORIGINS: list[str] = [
    origin.strip()
    for origin in os.getenv(
        "TK_CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
    ).split(",")
    if origin.strip()
]

# ─────────────────────── 安全凭据 ───────────────────────
# 代码里保留的"出厂弱默认值"。启动自检会检测它们是否仍在使用，
# 详见 app/startup_checks.py。
DEV_JWT_SECRET: str = "dev-only-change-me"
WEAK_DEFAULTS: dict[str, str] = {
    "TK_MASTER_PIN": "TK-PIN-2026",
    "TK_ADMIN_PASSWORD": "tostiyk2026",
}

MASTER_SECURITY_PIN: str = os.getenv("TK_MASTER_PIN", WEAK_DEFAULTS["TK_MASTER_PIN"])
DEFAULT_ADMIN_USERNAME: str = os.getenv("TK_ADMIN_USER", "admin")
DEFAULT_ADMIN_PASSWORD: str = os.getenv(
    "TK_ADMIN_PASSWORD", WEAK_DEFAULTS["TK_ADMIN_PASSWORD"]
)

# `TK_ADMIN_PASSWORD` / `TK_MASTER_PIN` 是否由运维显式配置（而非走代码默认值）
ADMIN_PASSWORD_IS_EXPLICIT: bool = "TK_ADMIN_PASSWORD" in os.environ
MASTER_PIN_IS_EXPLICIT: bool = "TK_MASTER_PIN" in os.environ

# 严格模式：检测到仍在使用弱默认值就拒绝启动（公网部署建议开启）
STRICT_SECURITY: bool = os.getenv("TK_STRICT_SECURITY", "").strip().lower() in (
    "1", "true", "yes", "on",
)

# 是否允许 SQLModel.metadata.create_all() 在启动时兜底建表。
# 默认 True（保持现状）；设为 0 后由 Alembic 独立管理表结构。
AUTO_CREATE_TABLES: bool = os.getenv("TK_AUTO_CREATE_TABLES", "1").strip().lower() in (
    "1", "true", "yes", "on",
)


# 迁移失败时是否拒绝启动。默认 False（保持 warn 行为）；
# 设为 1，或 AUTO_CREATE_TABLES=0 时，迁移失败将强制 raise。
STRICT_MIGRATION: bool = os.getenv("TK_STRICT_MIGRATION", "").strip().lower() in (
    "1", "true", "yes", "on",
)

# ─────────────────────── JWT 签名密钥 ───────────────────────
# 不再保留可预测的默认密钥：未配置时自动生成一份随机密钥并持久化到
# <项目根>/.jwt_secret（0600，已 gitignore），这样即使运维忘了配环境变量，
# 也不会出现"所有人都知道密钥、可任意伪造令牌"的情况。
JWT_SECRET_FILE: Path = BASE_DIR / ".jwt_secret"


def _resolve_jwt_secret() -> tuple[str, str]:
    """返回 (密钥, 来源说明)。优先级：环境变量 > 本地密钥文件 > 新生成并落盘。"""
    from_env = os.getenv("TK_JWT_SECRET", "").strip()
    # 显式写成开发占位值等同于没配，避免误以为已经安全
    if from_env and from_env != DEV_JWT_SECRET:
        return from_env, "环境变量 TK_JWT_SECRET"

    if JWT_SECRET_FILE.is_file():
        saved = JWT_SECRET_FILE.read_text(encoding="utf-8").strip()
        if saved:
            return saved, f"本地密钥文件 {JWT_SECRET_FILE.name}"

    generated = secrets.token_urlsafe(48)
    JWT_SECRET_FILE.write_text(generated + "\n", encoding="utf-8")
    try:
        JWT_SECRET_FILE.chmod(0o600)
    except OSError:
        pass  # Windows 等不支持 POSIX 权限时忽略
    return generated, f"新生成并写入 {JWT_SECRET_FILE.name}（请妥善保管）"


JWT_SECRET: str
JWT_SECRET_SOURCE: str
JWT_SECRET, JWT_SECRET_SOURCE = _resolve_jwt_secret()
# 同步回环境变量，便于其它模块或子进程读取到最终生效值
os.environ["TK_JWT_SECRET"] = JWT_SECRET

# ─────────────────────── 登录防爆破 ───────────────────────
# 滑动窗口 + 锁定：同一 (账号, IP) 在 WINDOW 秒内失败超过 MAX 次，
# 则锁定 LOCKOUT 秒。详细实现见 app/services/ratelimit.py。
LOGIN_MAX_ATTEMPTS: int = int(os.getenv("TK_LOGIN_MAX_ATTEMPTS", "5"))
LOGIN_WINDOW_SECONDS: int = int(os.getenv("TK_LOGIN_WINDOW_SECONDS", "300"))
LOGIN_LOCKOUT_SECONDS: int = int(os.getenv("TK_LOGIN_LOCKOUT_SECONDS", "900"))

# 部署在反向代理后面时，客户端 IP 需从 X-Forwarded-For 取；
# 直连暴露时保持 False，否则攻击者可伪造该头绕过限流。
TRUST_PROXY: bool = os.getenv("TK_TRUST_PROXY", "").strip().lower() in (
    "1", "true", "yes", "on",
)

# ───────────────────────── 启动时初始化 ─────────────────────────
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
