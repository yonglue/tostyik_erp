# 未完成事项 —— 分步操作手册

> 本手册中所有代码都已在项目副本上**实际跑通验证**,可直接粘贴。
> 每个步骤的结构:**改哪个文件 → 放什么代码 → 怎么验证**。
> 建议按阶段顺序做,每完成一个阶段提交一次 git。

---

## 阶段 0 · 准备环境变量(先做,后面都依赖它)

### 0.1 生成一个随机密钥

```bash
cd /Users/elias/tostiyk-erp
.venv/bin/python -c "import secrets; print(secrets.token_urlsafe(48))"
```

把输出复制下来,下一步要用。

### 0.2 新建 `.env` 文件(已被 .gitignore 忽略,不会进仓库)

位置:`/Users/elias/tostiyk-erp/.env`

```dotenv
# 访问令牌签名密钥 —— 填上一步生成的那串随机字符
TK_JWT_SECRET=把上一步的输出粘贴到这里

# 令牌有效期(分钟),默认 720 = 12 小时
TK_TOKEN_TTL_MINUTES=720

# 管理员重置密码用的万能密钥(原代码硬编码为 TK-PIN-2026)
TK_MASTER_PIN=TK-PIN-2026

# 全新数据库初始化时的管理员账号
TK_ADMIN_USER=admin
TK_ADMIN_PASSWORD=换成一个强密码

# 允许跨域的前端来源,多个用逗号分隔
TK_CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# 报价单 PDF 下载地址前缀
TK_PUBLIC_BASE_URL=http://localhost:8000
```

### 0.3 新建 `.env.example`(进仓库,给别人看要配哪些变量)

位置:`/Users/elias/tostiyk-erp/.env.example`

```dotenv
TK_JWT_SECRET=change-me
TK_TOKEN_TTL_MINUTES=720
TK_MASTER_PIN=change-me
TK_ADMIN_USER=admin
TK_ADMIN_PASSWORD=change-me
TK_CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
TK_PUBLIC_BASE_URL=http://localhost:8000
```

### 0.4 让应用自己读取 `.env`(不需要启动参数)

> ⚠️ **勘误**:初版手册写的「uvicorn 原生支持 `--env-file`,不需要 python-dotenv」是**错的**。
> uvicorn 的 `--env-file` 内部 `from dotenv import load_dotenv`,而本项目没装该包,
> 加了参数会直接启动失败:`ModuleNotFoundError: No module named 'dotenv'`。

正确做法:在 `app/config.py` 里用标准库自解析 `.env`,启动命令保持原样不变。

**文件**:`app/config.py` —— 在「路径」段落之后、任何 `os.getenv` 之前插入:

```python
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
```

启动命令**不加任何参数**:

```bash
.venv/bin/uvicorn app.main:app --reload --port 8000
```

**验证**:

```bash
.venv/bin/python -c "
import app.security as s
print('JWT_SECRET 已从 .env 载入:', s.JWT_SECRET != 'dev-only-change-me')
print('长度:', len(s.JWT_SECRET))"
# 期望:True / 64

# 真实环境变量优先级更高
TK_MASTER_PIN=FROM_ENV .venv/bin/python -c "
import app.config as c; print(c.MASTER_SECURITY_PIN)"
# 期望:FROM_ENV
```

> **`.gitignore` 也要改**(初版手册的写法会误伤阶段 3 的前端 env 文件)。
> 实测:原规则 `.env.*` 会把 `frontend/.env.development` 和 `frontend/.env.production`
> 一并忽略,导致阶段 3 的环境变量文件进不了仓库。应改为:
> ```
> # ---------- 环境变量与密钥 ----------
> # 只忽略含真实密钥的 .env 及本地覆盖文件；
> # .env.example / frontend/.env.development / frontend/.env.production 需入库
> .env
> .env.local
> .env.*.local
> !.env.example
> ```
> 这样 `.env.example` 能入库,`.env` 保持忽略。

---

## 阶段 1 · 收尾三件小事

### 步骤 1 (A1) 修复 `test_root`

**文件**:`app/main.py` —— 拉到**文件最后两行**,现在是:

```python
@app.get("/")
def read_root():
    return {"message": "🎯 抓到你了！后端正在运行这个新文件！"}
```

**替换为**:

```python
@app.get("/")
def read_root():
    return {"message": "TOSTIKYK ERP API is running", "version": __version__}
```

**验证**:

```bash
.venv/bin/python -m pytest test_erp.py -q
# 期望:48 passed
```

---

### 步骤 2 (A2) 清理数据库里的 4 张历史空表

先备份,再删。这 4 张表行数均为 0,且代码中已无任何引用。

```bash
cd /Users/elias/tostiyk-erp
cp tostiyk_erp.db backups/pre_drop_tables_$(date +%F).db

.venv/bin/python - <<'EOF'
import sqlite3
TABLES = [
    "products",              # 被遮蔽的 Product 模型遗留
    "part_cross_references", # 未被任何路由使用
    "inventory_transactions",# 注意:在用的是无下划线的 inventorytransaction
    "inventorytransactions", # 更早版本遗留
]
c = sqlite3.connect("tostiyk_erp.db")
for t in TABLES:
    c.execute(f'DROP TABLE IF EXISTS "{t}"')
    print("已删除", t)
c.commit()
print("剩余表:", sorted(r[0] for r in c.execute(
    "select name from sqlite_master where type='table'")))
EOF
```

**验证**:输出里不应再出现上面 4 张表,且 `autopart` / `inventorytransaction` / `orders` 仍在。

---

### 步骤 3 (A3) 决定字体是否入库

二选一,执行对应命令即可:

```bash
# 选项 A:入库(换机器/克隆后中文 PDF 正常,代价是仓库 +55MB)
git add -f "STHeiti Light.ttc" && git commit -m "chore: 纳入中文 PDF 字体"

# 选项 B:不入库(保持现状,换机器需手工拷贝字体)
# 什么都不用做
```

---

## 阶段 2 · 安全加固(6 个改动,按顺序做)

### 步骤 4 (B3) CORS 收敛为白名单

**文件**:`app/config.py` —— 在「运行期常量」那一段的末尾(`PUBLIC_BASE_URL` 后面)追加:

```python
# 允许跨站访问的前端来源(逗号分隔),避免 allow_origins=["*"] 与凭据共存的非法组合
CORS_ORIGINS: list[str] = [
    origin.strip()
    for origin in os.getenv(
        "TK_CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
    ).split(",")
    if origin.strip()
]
```

**文件**:`app/main.py` —— 两处改动。

第 1 处,导入行(`from app.config import ...` 那一行)加上 `CORS_ORIGINS`:

```python
from app.config import (
    CORS_ORIGINS,
    DB_PATH,
    DEFAULT_ADMIN_PASSWORD,
    DEFAULT_ADMIN_USERNAME,
    UPLOAD_DIR,
)
```

第 2 处,把 `app.add_middleware(...)` 整段替换为:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,      # ← 原来的 ["*"] 换掉
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**验证**:

```bash
.venv/bin/uvicorn app.main:app --port 8000
# 另开终端:
curl -s -o /dev/null -w "%{http_code}\n" -H "Origin: http://localhost:5173" http://127.0.0.1:8000/api/parts
curl -sI -H "Origin: http://evil.example.com" http://127.0.0.1:8000/api/parts | grep -i access-control-allow-origin
# 期望:第二条无输出(非白名单来源不返回该头)
```

---

### 步骤 5 (B2 + B1 基础) 替换 `app/security.py`

**文件**:`app/security.py` —— **整个文件替换**为下面内容(用标准库实现,不装任何新依赖):

```python
"""凭据哈希与访问令牌。

全部使用标准库实现，不引入额外依赖：
* 密码派生用 hashlib.scrypt（内存硬，抗 GPU 暴力破解），每个用户独立随机盐。
* 访问令牌用 HMAC-SHA256 签名的精简 JWT（HS256）。

⚠️ 生产环境必须通过环境变量 TK_JWT_SECRET 注入随机密钥。
"""

import base64
import hashlib
import hmac
import json
import os
import secrets
import time

JWT_SECRET: str = os.getenv("TK_JWT_SECRET", "dev-only-change-me")
TOKEN_TTL_MINUTES: int = int(os.getenv("TK_TOKEN_TTL_MINUTES", str(60 * 12)))

_SCRYPT_N, _SCRYPT_R, _SCRYPT_P = 2 ** 14, 8, 1
_SCRYPT_PREFIX = "scrypt"


# ──────────────────────────── 基础编码 ────────────────────────────
def _b64e(raw: bytes) -> str:
    """URL 安全 base64，去掉末尾填充。"""
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


def _b64d(txt: str) -> bytes:
    return base64.urlsafe_b64decode(txt + "=" * (-len(txt) % 4))


# ──────────────────────────── 密码哈希 ────────────────────────────
def hash_password(raw_password: str) -> str:
    """生成 scrypt 哈希，格式：scrypt$N$r$p$盐$哈希。"""
    salt = secrets.token_bytes(16)
    dk = hashlib.scrypt(
        raw_password.encode(), salt=salt,
        n=_SCRYPT_N, r=_SCRYPT_R, p=_SCRYPT_P, dklen=32,
    )
    return f"{_SCRYPT_PREFIX}${_SCRYPT_N}${_SCRYPT_R}${_SCRYPT_P}${_b64e(salt)}${_b64e(dk)}"


def _verify_scrypt(raw_password: str, stored: str) -> bool:
    try:
        _, n, r, p, salt_b64, hash_b64 = stored.split("$")
        dk = hashlib.scrypt(
            raw_password.encode(), salt=_b64d(salt_b64),
            n=int(n), r=int(r), p=int(p), dklen=32,
        )
        return hmac.compare_digest(dk, _b64d(hash_b64))
    except Exception:
        return False


def verify_password(raw_password: str, password_hash: str) -> bool:
    """校验密码。兼容迁移前遗留的无盐 SHA-256 哈希。"""
    if not password_hash:
        return False
    if password_hash.startswith(_SCRYPT_PREFIX + "$"):
        return _verify_scrypt(raw_password, password_hash)
    # 存量 SHA-256（无盐）——只为平滑迁移保留，登录成功后会被就地升级
    return hmac.compare_digest(
        hashlib.sha256(raw_password.encode()).hexdigest(), password_hash
    )


def needs_rehash(password_hash: str) -> bool:
    """判断该哈希是否还是旧的弱算法（登录成功后可调用 hash_password 重写）。"""
    return not password_hash.startswith(_SCRYPT_PREFIX + "$")


# ──────────────────────────── 访问令牌 ────────────────────────────
def create_access_token(username: str, role: str, ttl_minutes: int | None = None) -> str:
    """签发 HS256 令牌。"""
    ttl = TOKEN_TTL_MINUTES if ttl_minutes is None else ttl_minutes
    payload = {"sub": username, "role": role, "exp": int(time.time()) + ttl * 60}
    body = _b64e(json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode())
    sig = _b64e(hmac.new(JWT_SECRET.encode(), body.encode(), hashlib.sha256).digest())
    return f"{body}.{sig}"


def decode_access_token(token: str) -> dict | None:
    """校验签名与有效期，失败返回 None。"""
    try:
        body, sig = token.split(".")
        expected = _b64e(hmac.new(JWT_SECRET.encode(), body.encode(), hashlib.sha256).digest())
        if not hmac.compare_digest(sig, expected):
            return None
        payload = json.loads(_b64d(body))
        if int(payload.get("exp", 0)) < time.time():
            return None
        return payload
    except Exception:
        return None
```

> 存量密码不用迁移:旧的无盐 SHA-256 哈希仍能登录,并在**登录成功那一刻自动升级**为 scrypt。

**验证**:

```bash
.venv/bin/python -c "
from app.security import hash_password, verify_password, needs_rehash, create_access_token, decode_access_token
import hashlib
h = hash_password('abc')
assert verify_password('abc', h) and not verify_password('x', h)
old = hashlib.sha256(b'abc').hexdigest()
assert verify_password('abc', old) and needs_rehash(old)
t = create_access_token('admin', 'super_admin')
assert decode_access_token(t)['sub'] == 'admin'
assert decode_access_token(t[:-2] + 'zz') is None
print('✅ security.py 全部通过')
"
```

---

### 步骤 6 (B1 后端) 新建 `app/deps.py`

**新建文件**:`app/deps.py`

```python
"""FastAPI 依赖：从 Authorization: Bearer <token> 解析当前操作人。"""

from dataclasses import dataclass

from fastapi import Depends, Header, HTTPException

from app.security import decode_access_token


@dataclass
class Actor:
    """当前请求的操作人身份。"""
    username: str
    role: str


def get_current_actor(authorization: str = Header(default="")) -> Actor:
    """解析并校验访问令牌；无效则 401。"""
    if not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status_code=401,
            detail="未登录或缺少访问令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )
    payload = decode_access_token(authorization[7:].strip())
    if not payload:
        raise HTTPException(
            status_code=401,
            detail="访问令牌无效或已过期",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return Actor(username=payload["sub"], role=payload.get("role", "staff"))


def require_admin(actor: Actor = Depends(get_current_actor)) -> Actor:
    """要求管理员及以上角色，否则 403。"""
    if actor.role not in ("super_admin", "admin"):
        raise HTTPException(status_code=403, detail="无权执行此操作")
    return actor
```

---

### 步骤 7 (B1 后端) 重写 `app/routers/auth.py`

**文件**:`app/routers/auth.py` —— **整个文件替换**:

```python
"""登录、管理员重置、员工账号管理。"""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.config import DEFAULT_ADMIN_PASSWORD, DEFAULT_ADMIN_USERNAME, MASTER_SECURITY_PIN
from app.database import get_session
from app.deps import Actor, get_current_actor
from app.models import AdminUser, StaffUser
from app.schemas import CreateStaffPayload, LoginPayload, ResetPasswordPayload
from app.security import (
    create_access_token,
    hash_password,
    needs_rehash,
    verify_password,
)
from app.services.audit import log_action

router = APIRouter(tags=["鉴权与员工"])


@router.post("/api/auth/login")
def login_user(payload: LoginPayload, session: Session = Depends(get_session)):
    # 保持原有查找顺序：先管理员，再店员
    for model in (AdminUser, StaffUser):
        user = session.exec(select(model).where(model.username == payload.username)).first()
        if not user or not verify_password(payload.password, user.password_hash):
            continue
        # 旧的 SHA-256 哈希在此就地升级为 scrypt
        if needs_rehash(user.password_hash):
            user.password_hash = hash_password(payload.password)
            session.add(user)
            session.commit()
        return {
            "status": "success",
            "username": user.username,
            "role": user.role,
            "access_token": create_access_token(user.username, user.role),
            "token_type": "bearer",
        }

    raise HTTPException(status_code=401, detail="账号或密码错误 (Invalid credentials)")


@router.post("/api/auth/reset-admin")
def reset_admin_password(payload: ResetPasswordPayload, session: Session = Depends(get_session)):
    if payload.security_pin != MASTER_SECURITY_PIN:
        raise HTTPException(status_code=403, detail="安全密钥错误，拒绝重置！")

    user = session.exec(select(AdminUser).where(AdminUser.username == DEFAULT_ADMIN_USERNAME)).first()
    default_hash = hash_password(DEFAULT_ADMIN_PASSWORD)
    if user:
        user.password_hash = default_hash
        session.add(user)
    else:
        session.add(AdminUser(
            username=DEFAULT_ADMIN_USERNAME,
            password_hash=default_hash,
            role="super_admin",
        ))
    session.commit()
    return {"status": "success", "message": "Password reset successfully"}


@router.get("/api/staff")
def get_staff_list(
    actor: Actor = Depends(get_current_actor),
    session: Session = Depends(get_session),
):
    return session.exec(select(StaffUser)).all()


@router.post("/api/staff")
def create_staff(
    payload: CreateStaffPayload,
    actor: Actor = Depends(get_current_actor),
    session: Session = Depends(get_session),
):
    if actor.role not in ["super_admin", "admin"]:
        raise HTTPException(status_code=403, detail="无权创建员工账号")

    existing = session.exec(select(StaffUser).where(StaffUser.username == payload.username)).first()
    if existing:
        raise HTTPException(status_code=400, detail="该员工账号已存在")

    new_staff = StaffUser(
        username=payload.username,
        password_hash=hash_password(payload.password),
        role=payload.role,
    )
    session.add(new_staff)
    session.commit()

    log_action(
        session=session, username=actor.username, role=actor.role,
        action="CREATE_STAFF",
        details=f"创建了新店员: {payload.username}，分配角色: {payload.role}",
    )
    return {"status": "success", "message": "Staff created successfully"}


@router.delete("/api/staff/{staff_id}")
def delete_staff(
    staff_id: int,
    actor: Actor = Depends(get_current_actor),
    session: Session = Depends(get_session),
):
    if actor.role not in ["super_admin", "admin"]:
        raise HTTPException(status_code=403, detail="无权删除员工账号")

    staff = session.get(StaffUser, staff_id)
    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")

    target_name = staff.username
    session.delete(staff)
    session.commit()

    log_action(
        session=session, username=actor.username, role=actor.role,
        action="DELETE_STAFF", details=f"删除了店员账号: {target_name} (ID: {staff_id})",
    )
    return {"status": "success", "message": "Staff deleted"}
```

---

### 步骤 8 (B1 后端) 批量改掉另外 7 个路由文件

**要改的文件**:`app/routers/` 下的
`clients.py`、`exports.py`、`parts.py`、`pos.py`、`purchase_orders.py`、`quotations.py`、`transactions.py`

**改动规律**(每个文件都长这样,共 12 处):

改动前:

```python
def 某个函数(
    ...,
    x_username: str = Header(default="admin"),
    x_role: str = Header(default="super_admin"),
    session: Session = Depends(get_session),
):
    ...
    log_action(session=session, username=x_username, role=x_role, ...)
```

改动后:

```python
def 某个函数(
    ...,
    actor: Actor = Depends(get_current_actor),
    session: Session = Depends(get_session),
):
    ...
    log_action(session=session, username=actor.username, role=actor.role, ...)
```

同时要:① 文件顶部加 `from app.deps import Actor, get_current_actor`;
② 从 `from fastapi import ...` 里删掉 `Header`(改完就没人用了)。

**机械替换脚本**(已实测,直接跑,跑完可删):

```bash
cd /Users/elias/tostiyk-erp
cat > /tmp/migrate_auth.py <<'PYEOF'
"""把各路由的请求头鉴权机械替换为依赖注入（一次性脚本）。"""
import pathlib
import re

DECL = re.compile(
    r'    x_username: str = Header\(default="admin"\),\n'
    r'    x_role: str = Header\(default="super_admin"\),\n'
)
SKIP = {"auth.py"}   # 已在步骤 7 手工改好


def _drop_header(m):
    names = [n.strip() for n in m.group(2).split(",") if n.strip() != "Header"]
    return m.group(1) + ", ".join(names) + "\n"


changed = []
for p in sorted(pathlib.Path("app/routers").glob("*.py")):
    if p.name in SKIP:
        continue
    s = orig = p.read_text(encoding="utf-8")
    s = DECL.sub("    actor: Actor = Depends(get_current_actor),\n", s)
    s = s.replace("x_username", "actor.username").replace("x_role", "actor.role")
    if s == orig:
        continue
    if "from app.deps import" not in s:
        s = s.replace(
            "from app.database import get_session\n",
            "from app.database import get_session\nfrom app.deps import Actor, get_current_actor\n",
            1,
        )
    if "Header(" not in s:
        s = re.sub(r'(from fastapi import )(.*)\n', _drop_header, s, count=1)
    p.write_text(s, encoding="utf-8")
    changed.append(p.name)

print("已迁移:", ", ".join(changed))
PYEOF

.venv/bin/python /tmp/migrate_auth.py
# 期望输出: 已迁移: clients.py, exports.py, parts.py, pos.py, purchase_orders.py, quotations.py, transactions.py
```

**验证替换干净**:

```bash
grep -rn "x_username\|x_role" app/routers/ && echo "❌ 还有残留" || echo "✅ 无残留"
grep -rln "Header" app/routers/ && echo "❌ 还有未清理的 Header" || echo "✅ Header 已清理"
.venv/bin/python -c "from app.main import app; print('✅ 导入正常, 端点数 =', len(app.openapi()['paths']))"
# 期望:唯一路径 = 36（路径+方法组合才是 43）
```

---

### 步骤 9 (B1 测试) 更新 `test_erp.py`

47 处请求头要换成令牌。**在 `test_erp.py` 的导入区**(`from sqlmodel import create_engine, Session, SQLModel` 那一行**之后**)插入:

```python

# ── 鉴权辅助：所有需要登录的请求改为携带 Bearer 令牌 ──
from app.security import create_access_token


def auth_headers(username: str, role: str) -> dict:
    return {"Authorization": f"Bearer {create_access_token(username, role)}"}


AUTH_ADMIN = auth_headers("admin", "super_admin")

```

然后把下面 4 种写法做**全局替换**:

| 原写法 | 替换为 |
|---|---|
| `{"x-username": "admin", "x-role": "super_admin"}` | `AUTH_ADMIN` |
| `{"x-username": "cashier_juan", "x-role": "staff"}` | `auth_headers("cashier_juan", "staff")` |
| `{"x-username": "normal_staff", "x-role": "staff"}` | `auth_headers("normal_staff", "staff")` |
| `{"x-username": "maria", "x-role": "staff"}` | `auth_headers("maria", "staff")` |

**还有一处**:`test_staff_management_lifecycle` 里 `GET /api/staff` 原来不需要登录,现在需要了。找到:

```python
    list_res = client.get("/api/staff")
```

改成:

```python
    list_res = client.get("/api/staff", headers=AUTH_ADMIN)
```

**验证**:

```bash
.venv/bin/python -m pytest test_erp.py -q
# 期望:48 passed
```

---

### 步骤 10 (B1 端到端) 真实启动验证

```bash
.venv/bin/uvicorn app.main:app --port 8000
```

另开一个终端:

```bash
# 1) 登录拿令牌
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"tostiyk2026"}' \
  | .venv/bin/python -c "import sys,json;print(json.load(sys.stdin)['access_token'])")
echo "令牌长度: ${#TOKEN}"        # 期望 115 左右

# 2) 伪造旧请求头 —— 必须被拒绝
curl -s -o /dev/null -w "伪造 X-Role  -> %{http_code}\n" -X POST http://127.0.0.1:8000/api/parts -H 'X-Role: super_admin'
# 期望 401

# 3) 带令牌可以访问,不带就不行
curl -s -o /dev/null -w "带令牌   -> %{http_code}\n" http://127.0.0.1:8000/api/staff -H "Authorization: Bearer $TOKEN"
curl -s -o /dev/null -w "无令牌   -> %{http_code}\n" http://127.0.0.1:8000/api/staff
# 期望 200 / 401
```

---

## 阶段 3 · 前端

### 步骤 11 (C1) 前端地址环境变量化

**11.1 新建两个环境文件**

`frontend/.env.development`:

```dotenv
VITE_API_BASE=http://localhost:8000
```

`frontend/.env.production`(生产与后端同源,留空即可):

```dotenv
VITE_API_BASE=
```

**11.2 替换 `frontend/src/utils/api.js` 整个文件**

```javascript
// src/utils/api.js
//
// 后端地址集中由 .env 控制（VITE_API_BASE），不再在组件里硬编码 localhost:8000。

export const API_BASE = import.meta.env.VITE_API_BASE ?? ''

/** 相对路径拼成完整地址；已是 http(s) 绝对地址则原样返回 */
export const apiUrl = (url) => (url?.startsWith('http') ? url : `${API_BASE}${url}`)

const TOKEN_KEY = 'tostiyk_token'

export const getToken = () => localStorage.getItem(TOKEN_KEY) || ''
export const setToken = (token) => localStorage.setItem(TOKEN_KEY, token)
export const clearToken = () => localStorage.removeItem(TOKEN_KEY)

export const apiFetch = async (url, options = {}) => {
  const token = getToken()

  const headers = {
    'Content-Type': 'application/json',
    // 登录后所有请求自动带上访问令牌
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(options.headers || {})
  }

  const response = await fetch(apiUrl(url), {
    ...options,
    headers
  })

  // 令牌无效/过期：清理本地登录态，交给调用方跳回登录页
  if (response.status === 401) {
    clearToken()
    localStorage.removeItem('tostiyk_logged_in')
  }

  return response
}
```

**11.3 批量替换 22 处硬编码**

先手工处理 2 处「字符串拼接」形式:

| 文件 | 行 | 改动前 | 改动后 |
|---|---|---|---|
| `frontend/src/App.vue` | 353 | `'http://localhost:8000' + currentGalleryImages[currentGalleryIndex]` | `apiUrl(currentGalleryImages[currentGalleryIndex])` |
| `frontend/src/components/PartsView.vue` | 63 | `'http://localhost:8000' + parseImages(item.image_url)[0]` | `apiUrl(parseImages(item.image_url)[0])` |

其余 20 处用脚本一次替换(已实测):

```bash
cd /Users/elias/tostiyk-erp/frontend/src
/Users/elias/tostiyk-erp/.venv/bin/python - <<'PYEOF'
import pathlib, re

PATTERNS = [
    (re.compile(r"'http://localhost:8000([^']*)'"), r"apiUrl('\1')"),
    (re.compile(r"`http://localhost:8000([^`]*)`"), r"apiUrl(`\1`)"),
]
targets = ["components/FinancialView.vue", "components/CashRegisterView.vue",
           "components/QuotationDeskView.vue", "components/BackupView.vue",
           "App.vue", "components/PartsView.vue"]

for rel in targets:
    p = pathlib.Path(rel)
    s = orig = p.read_text(encoding="utf-8")
    for rx, rep in PATTERNS:
        s = rx.sub(rep, s)
    if "apiUrl" in s and not re.search(r"import \{[^}]*\bapiUrl\b[^}]*\} from", s):
        if "import { apiFetch } from './utils/api'" in s:
            s = s.replace("import { apiFetch } from './utils/api'",
                          "import { apiFetch, apiUrl } from './utils/api'")
        elif "import { apiFetch } from '../utils/api'" in s:
            s = s.replace("import { apiFetch } from '../utils/api'",
                          "import { apiFetch, apiUrl } from '../utils/api'")
        else:
            lines = s.split("\n")
            last = max(i for i, l in enumerate(lines) if l.startswith("import "))
            lines.insert(last + 1, "import { apiUrl } from '../utils/api'")
            s = "\n".join(lines)
    if s != orig:
        p.write_text(s, encoding="utf-8")
        print("已改", rel)
PYEOF
```

**11.4 让登录/退出保存与清除令牌**

文件:`frontend/src/App.vue`

第 1 处,导入行改为:

```javascript
import { apiFetch, apiUrl, setToken, clearToken } from './utils/api'
```

第 2 处,`handleLogin` 里找到:

```javascript
      localStorage.setItem('tostiyk_logged_in', 'true')
      localStorage.setItem('tostiyk_username', data.username)
```

在它**上面**插入一行:

```javascript
      setToken(data.access_token)          // 保存访问令牌，后续请求自动携带
```

第 3 处,`handleLogout` 里找到:

```javascript
  localStorage.removeItem('tostiyk_logged_in')
```

在它**上面**插入一行:

```javascript
  clearToken()
```

**验证**:

```bash
cd /Users/elias/tostiyk-erp/frontend
grep -rn "localhost:8000" src/ || echo "✅ 组件中已无硬编码"
npm run build
# 期望:✓ built,无报错
```

---

### 步骤 12 (C2) 统一请求层,干掉 axios

只改了 `frontend/src/components/QuotationDeskView.vue` 一个文件,3 个调用点。

**12.1 删除第 683 行的 `import axios from 'axios'`**

**12.2 把 `import { apiUrl } from '../utils/api'` 改为 `import { apiFetch } from '../utils/api'`**

**12.3 三个调用点**

① 加载历史订单 —— 改动前:

```javascript
    const res = await axios.get(apiUrl('/api/pos/orders'))
    completedOrders.value = res.data
```

改动后:

```javascript
    const res = await apiFetch('/api/pos/orders')
    if (!res.ok) throw new Error('获取历史订单失败')
    completedOrders.value = await res.json()
```

② 退货 —— 改动前:

```javascript
    const headers = {
      'x-username': props.currentUser?.username || 'admin',
      'x-role': props.currentUser?.role || 'super_admin'
    }
    await axios.post(apiUrl(`/api/pos/orders/${targetReturnDbId.value}/refund`), {}, { headers })
    showToast('🔄 退货成功，库存已自动回滚！', 'success')
```

改动后(鉴权头已由 `apiFetch` 自动附加,不用再手写):

```javascript
    const res = await apiFetch(`/api/pos/orders/${targetReturnDbId.value}/refund`, {
      method: 'POST'
    })
    if (!res.ok) {
      const detail = await res.json().catch(() => ({}))
      throw new Error(detail.detail || '退货请求失败')
    }
    showToast('🔄 退货成功，库存已自动回滚！', 'success')
```

同时把该函数的 catch 里:

```javascript
    showToast(err.response?.data?.detail || '退货请求失败', 'error')
```
改为:
```javascript
    showToast(err.message || '退货请求失败', 'error')
```

③ POS 开单 —— 改动前:

```javascript
    const headers = {
      'x-username': props.currentUser?.username || 'admin',
      'x-role': props.currentUser?.role || 'super_admin'
    }

    const res = await axios.post(apiUrl('/api/pos/orders'), payload, { headers })
    
    // 🌟 核心：关闭预览弹窗，绝不弹出中间多余提示，只在右上角显示绿色成功提示
    previewModalVisible.value = false
    showToast(`✅ 开单成功！单号: ${res.data.order_no}`, 'success')
```

改动后:

```javascript
    const res = await apiFetch('/api/pos/orders', {
      method: 'POST',
      body: JSON.stringify(payload)
    })
    if (!res.ok) {
      const detail = await res.json().catch(() => ({}))
      throw new Error(detail.detail || '结账失败，请检查网络或库存！')
    }
    const data = await res.json()

    // 🌟 核心：关闭预览弹窗，绝不弹出中间多余提示，只在右上角显示绿色成功提示
    previewModalVisible.value = false
    showToast(`✅ 开单成功！单号: ${data.order_no}`, 'success')
```

同时把该函数的 catch 里:

```javascript
    const errorMsg = err.response?.data?.detail || '结账失败，请检查网络或库存！'
```
改为:
```javascript
    const errorMsg = err.message || '结账失败，请检查网络或库存！'
```

> ⚠️ 注意:`axios` 在非 2xx 时会抛异常,`fetch` 不会。所以上面每一处都补了 `if (!res.ok)` 判断,漏掉会导致失败静默通过。

---

### 步骤 13 (C3) 删除无用依赖

**文件**:`frontend/package.json` —— 从 `dependencies` 里删掉这 3 个:

```json
    "axios": "^1.20.0",
    "clsx": "^2.1.1",
    "tailwind-merge": "^3.7.0",
```

然后:

```bash
cd /Users/elias/tostiyk-erp/frontend
npm install
npm run build
```

**验证**:构建通过,且打包体积下降(实测 1346 kB → 1295 kB)。

---

## 阶段 4 · 测试与并发缺陷

### 步骤 14 (D1) 修掉并发测试的 flaky 根因

**文件**:`test_erp.py` —— 找到:

```python
test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False, "timeout": 30},
    poolclass=StaticPool,
)
```

**替换为**:

```python
# 用文件型 SQLite 代替内存 StaticPool：
# StaticPool 会让所有线程共享同一条连接，并发时必然抛
# sqlite3.InterfaceError: bad parameter or other API misuse（原有 flaky 的根因）。
test_engine = create_engine(
    "sqlite:///./_test_erp.db",
    connect_args={"check_same_thread": False, "timeout": 30},
)
```

同时把不再使用的 `from sqlmodel.pool import StaticPool` 删掉,并在 `.gitignore` 里加一行:

```
_test_erp.db
```

**验证**:

```bash
for i in 1 2 3 4 5; do .venv/bin/python -m pytest test_erp.py::test_mixed_concurrency_stress_test -q 2>&1 | tail -1; done
```

---

### 步骤 15 (D2) 修掉真实的并发超卖缺陷

> **这是本次排查中新发现的真实业务缺陷**,不是测试问题。
> `select(...).with_for_update()` 在 SQLite 上会被**静默忽略**(SQLite 不支持 `SELECT ... FOR UPDATE`),
> 所以「先读库存再写库存」之间存在竞态:5 个并发请求抢 1 件库存,会有 2 个同时成功 → **超卖**。

**文件**:`app/routers/quotations.py`

**15.1 导入行加 `update`**:

```python
from sqlmodel import Session, select, update
```

**15.2 找到 `generate_and_save_quotation` 里这段**:

```python
        part = session.exec(
            select(AutoPart)
            .where(AutoPart.oem == item.oem)
            .with_for_update()
        ).first()

        if not part:
            raise HTTPException(status_code=404, detail=f"商品 {item.oem} 不存在或已被删除！")

        old_stock = part.stock
        if part.stock < item.quantity:
            raise HTTPException(status_code=400, detail=f"商品 {part.name} 库存不足，无法成交出库！")
        part.stock -= item.quantity
        session.add(part)
```

**替换为**:

```python
        part = session.exec(select(AutoPart).where(AutoPart.oem == item.oem)).first()
        if not part:
            raise HTTPException(status_code=404, detail=f"商品 {item.oem} 不存在或已被删除！")

        old_stock = part.stock
        new_stock = old_stock - item.quantity

        # SQLite 不支持 SELECT ... FOR UPDATE（with_for_update 会被静默忽略），
        # 因此"先读后写"存在超卖竞态。改为原子条件更新 + 校验影响行数。
        result = session.exec(
            update(AutoPart)
            .where(AutoPart.oem == item.oem, AutoPart.stock >= item.quantity)
            .values(stock=AutoPart.stock - item.quantity)
        )
        if result.rowcount == 0:
            session.rollback()
            raise HTTPException(status_code=400, detail=f"商品 {part.name} 库存不足，无法成交出库！")
```

**15.3 紧接着的日志行**,把 `{part.stock}` 改成 `{new_stock}`(因为 `part` 对象已被 UPDATE 覆盖,不再是旧值):

```python
                details=f"开单销售出库: {part.name} (OEM: {item.oem}), 原库存: {old_stock} -> 新库存: {new_stock}",
```

> `app/routers/pos.py` 的 `create_pos_order` 有同样的 `with_for_update()` 写法,建议照此一并改掉。

**验证**:

```bash
for i in $(seq 1 10); do .venv/bin/python -m pytest test_erp.py::test_concurrent_flash_sale_race_condition -q 2>&1 | tail -1; done
# 期望:10 次全部 1 passed（改前实测会间歇性 assert 2 == 1）
```

---

### 步骤 15b (执行中新发现) `log_action` 会让开单"部分生效"

> 这是执行步骤 15 时**新发现的第二个数据一致性缺陷**,初版手册没有覆盖。

**症状**:一单两件,第二件库存不足返回 400,但**第一件的库存已经被扣掉了**。

**根因**:`app/services/audit.py` 的 `log_action()` 内部会 `session.commit()`,
而 `generate_and_save_quotation` 在**循环内**调用它。于是第一件扣完库存后立刻被提交,
第二件失败时的 `session.rollback()` 已经回滚不掉第一件了。

同理,挂账信用额度校验在循环之后,它抛 400 时库存也已经被提交。

**修法** —— `app/routers/quotations.py` 的 `generate_and_save_quotation`:

① 循环内**不要**调用 `log_action`,改为收集明细:

```python
    # 库存变动先只做扣减、不写审计日志：log_action 内部会 session.commit()，
    # 若在循环里调用，会把前面几件的扣减提前提交，导致后续某件校验失败时无法整体回滚。
    stock_logs: list[tuple[str, str, int, int]] = []

    for item in payload.items:
        ...（校验 + 原子扣减，保持步骤 15 的写法）...
        stock_logs.append((part.name, item.oem, old_stock, new_stock))
        session.add(tx)          # 只加流水，不写审计
```

② 信用额度拒绝时补上 `session.rollback()`:

```python
        if projected_debt > client_obj.credit_limit:
            # 必须回滚：此时本单的库存扣减还未提交，不回滚就会变成"拒单但扣了库存"
            session.rollback()
            raise HTTPException(status_code=400, detail=...)
```

③ 所有校验通过后,再统一落审计日志:

```python
    # 所有校验都通过了，此时才落审计日志（log_action 会提交，因此附带完成本单的库存落库）
    for part_name, item_oem, old_stock, new_stock in stock_logs:
        log_action(session=session, username=actor.username, role=actor.role,
                   action="UPDATE_STOCK",
                   details=f"开单销售出库: {part_name} (OEM: {item_oem}), 原库存: {old_stock} -> 新库存: {new_stock}")
```

**验证**(用副本库,别在生产库上试):

```bash
# 造两个测试件: QT-1 库存 6、QT-3 库存 2
# 提交一单: QT-1 × 1 + QT-3 × 99
curl -s -X POST http://127.0.0.1:8000/api/quotations/generate \
  -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d '{"client_name":"T","lang":"zh","payment_method":"Cash_USD","items":[
       {"oem":"QT-1","name":"a","brand":"T","quantity":1,"price":5},
       {"oem":"QT-3","name":"b","brand":"T","quantity":99,"price":5}]}'
# 期望:400,且 QT-1 库存仍为 6（修复前会变成 5）
```

> ⚠️ **通用规则**:`log_action()` 会提交事务,**永远不要在多步写操作的循环中间调用它**。
> 目前 `pos.py` 没有该问题(它在循环外调用),但后续新增代码要留意。

---

### 步骤 16 (D2 附带) 让 TestClient 真正触发 lifespan

**问题**:`test_erp.py` 里 `client = TestClient(app)` 没有用 `with`,而 Starlette 只在
`with TestClient(app)` 上下文里才触发 startup/shutdown。所以测试期间 `bootstrap()`
从不执行(靠 `setup_database` fixture 手工建表才没崩)。

> ⚠️ **初版手册的写法有隐患**:直接 `with TestClient(app)` 会让 `bootstrap()` 对着
> **真实的生产引擎**跑一遍——建表之外,如果 `autopart` 恰好为空,还会把 4 条演示配件
> **播种进生产库**。必须先把引擎换成测试库。

**改法 ①** —— `app/main.py`:`bootstrap()` 改为动态取引擎(否则测试替换不掉它)。
把导入行 `from app.database import engine, init_db` 改成:

```python
from app import database
from app.database import init_db
```

并把 `bootstrap()` 里的 `with Session(engine) as session:` 改成:

```python
    with Session(database.engine) as session:
```

(`init_db()` 内部本来就是在调用时读 `app.database.engine`,无需改动。)

**改法 ②** —— `test_erp.py`:加会话级 fixture,并把引擎临时指向测试库:

```python
from app import database          # 加到文件顶部导入区


@pytest.fixture(scope="session", autouse=True)
def run_app_lifespan():
    """让应用的 lifespan 真正跑一次。

    ⚠️ 关键：把 app.database.engine 临时指向测试库，否则 bootstrap() 会去
    建表并可能把 4 条演示配件播种到**真实的生产数据库**里。
    """
    original_engine = database.engine
    database.engine = test_engine
    try:
        with TestClient(app):
            yield
    finally:
        database.engine = original_engine
```

**改法 ③** —— 同一个文件的 `setup_database` fixture:在 `create_all` **之前**先
`drop_all` 一次,清掉 lifespan 播种的数据,保证每个用例从空库开始:

```python
@pytest.fixture(autouse=True)
def setup_database():
    # 先 drop 一次：清掉 run_app_lifespan 里 bootstrap() 播种的演示数据
    SQLModel.metadata.drop_all(test_engine)
    SQLModel.metadata.create_all(test_engine)
    yield
    SQLModel.metadata.drop_all(test_engine)
```

**验证**:

```bash
# 1) bootstrap 确实执行了(应看到数据库路径输出)
.venv/bin/python -m pytest test_erp.py::test_root -q -s 2>&1 | grep "数据库绝对路径"

# 2) 测试全程不碰生产库:跑测试前后比对表数与行数指纹
cat > /tmp/fp.py <<'EOF'
import hashlib, sqlite3
c = sqlite3.connect("tostiyk_erp.db")
sig = ["%s=%s" % (t, c.execute('select count(*) from "%s"' % t).fetchone()[0])
       for (t,) in sorted(c.execute("select name from sqlite_master where type='table'"))]
print(hashlib.sha256("|".join(sig).encode()).hexdigest()[:16])
EOF
.venv/bin/python /tmp/fp.py    # 跑测试
.venv/bin/python -m pytest test_erp.py -q
.venv/bin/python /tmp/fp.py    # 应输出与上面完全相同的指纹
```

---

## 阶段 5 · 巨型组件拆分(方法论,无法一步到位)

### 步骤 17 (C4) 拆 `QuotationDeskView.vue`(1161 行)与 `App.vue`(936 行)

这两个文件不适合"贴一段代码就完事",按下面的套路分 3 轮做:

**第 1 轮 · 抽状态到 composable**(不改任何 UI,风险最低)

在 `frontend/src/composables/` 下新建文件,把 `ref`/`computed`/数据请求函数搬进去:

```
composables/
├── usePosOrders.js      # 订单加载 / 开单 / 退货(fetchCompletedOrders、confirmAndPrint、executeReturnOrder)
├── useParts.js          # 配件增删查、图片解析(parseImages、库存操作)
├── useClients.js        # 客户档案、还款
├── useAuth.js           # 登录态、token、当前用户(替代散落的 localStorage 读写)
└── useI18n.js           # 已有的翻译,保持不变
```

composable 的固定写法:

```javascript
// composables/usePosOrders.js
import { ref } from 'vue'
import { apiFetch } from '../utils/api'

export function usePosOrders() {
  const orders = ref([])

  const loadOrders = async () => {
    const res = await apiFetch('/api/pos/orders')
    if (!res.ok) return
    orders.value = await res.json()
  }

  return { orders, loadOrders }
}
```

组件里改成:

```javascript
import { usePosOrders } from '../composables/usePosOrders'
const { orders, loadOrders } = usePosOrders()
```

**第 2 轮 · 抽子组件**

`QuotationDeskView.vue` 里的「预览弹窗」「历史订单弹窗」「退货确认弹窗」各自独立成
`components/pos/PosPreviewModal.vue`、`PosHistoryModal.vue`、`PosReturnModal.vue`,
通过 `props` 传入数据、`emit` 回传事件。

**第 3 轮 · 抽纯展示小组件**

`App.vue` 顶部的 `<img>` 画廊、各处表格行,拆成无状态展示组件。

**每轮做完都要**:

```bash
cd frontend && npm run build     # 必须通过
npm run dev                      # 手工点一遍:登录 → 开单 → 报价单 PDF → 退货
```

---

## 附录 · 全量验证清单

每完成一个阶段,跑这套:

```bash
cd /Users/elias/tostiyk-erp

# 1. 测试套件
.venv/bin/python -m pytest test_erp.py -q
# 期望:48 passed

# 2. API 契约没被破坏
#    ⚠️ 口径:len(openapi()['paths']) 是「唯一路径数」= 36;
#       「路径+方法组合数」= 43。两者别搞混。
.venv/bin/python -c "from app.main import app; print("唯一路径 =", len(app.openapi()['paths']), "| 路径+方法组合 =", sum(len(v) for v in app.openapi()['paths'].values()))"

# 3. 鉴权生效
.venv/bin/uvicorn app.main:app --port 8000 &
sleep 4
curl -s -o /dev/null -w "伪造头 -> %{http_code} (期望 401)\n" http://127.0.0.1:8000/api/staff -H 'X-Role: super_admin'
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/api/auth/login -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"tostiyk2026"}' | .venv/bin/python -c "import sys,json;print(json.load(sys.stdin)['access_token'])")
curl -s -o /dev/null -w "带令牌 -> %{http_code} (期望 200)\n" http://127.0.0.1:8000/api/staff -H "Authorization: Bearer $TOKEN"
kill %1

# 4. 前端构建
cd frontend && npm run build
```

---

## 各步骤实测结果对照

| 步骤 | 内容 | 实测结果 |
|---|---|---|
| 1 | 修 `test_root` | 48 passed |
| 5 | scrypt + JWT | 哈希/令牌/篡改/过期 全部通过 |
| 6–9 | JWT 鉴权迁移 | 47 passed + 伪造头 401 + 密码自动升级为 scrypt |
| 11–13 | 前端 | 构建通过,包体 1346 kB → 1295 kB |
| 14 | 文件型测试库 | 并发崩溃消失(8/12 → 3/10 失败) |
| 15 | 原子扣减 | 抢单用例 10/10 通过,完整套件连续 3 轮稳定 47 passed |
| 16 | lifespan | 未单独验证,属可选加固 |
