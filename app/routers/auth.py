"""登录、管理员重置、员工账号管理。"""

import hmac

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session, select

from app.config import (
    DEFAULT_ADMIN_PASSWORD,
    DEFAULT_ADMIN_USERNAME,
    MASTER_SECURITY_PIN,
    TRUST_PROXY,
    WEAK_DEFAULTS,
)
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
from app.services.ratelimit import login_limiter, reset_pin_limiter

router = APIRouter(tags=["鉴权与员工"])


def _client_ip(request: Request) -> str:
    """取客户端 IP。

    只有显式开启 TK_TRUST_PROXY 时才信任 X-Forwarded-For —— 否则直连暴露的场景下
    攻击者可以随意伪造该头，把限流 key 换掉从而绕过限制。
    """
    if TRUST_PROXY:
        forwarded = request.headers.get("x-forwarded-for", "")
        if forwarded:
            return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _reject_if_locked(limiter, key: str) -> None:
    wait = limiter.retry_after(key)
    if wait > 0:
        raise HTTPException(
            status_code=429,
            detail=f"尝试过于频繁，请在 {wait} 秒后重试。",
            headers={"Retry-After": str(wait)},
        )


@router.post("/api/auth/login")
def login_user(
    payload: LoginPayload,
    request: Request,
    session: Session = Depends(get_session),
):
    # 按 (客户端 IP + 账号) 限流，防止暴力破解
    rate_key = f"{_client_ip(request)}|{payload.username.strip().lower()}"
    _reject_if_locked(login_limiter, rate_key)

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

        login_limiter.reset(rate_key)
        _warn_if_weak_password(user)
        return {
            "status": "success",
            "username": user.username,
            "role": user.role,
            "access_token": create_access_token(user.username, user.role),
            "token_type": "bearer",
        }

    remaining = login_limiter.record_failure(rate_key)
    detail = "账号或密码错误 (Invalid credentials)"
    if remaining <= 2:
        detail += f"（连续失败 {login_limiter.max_attempts - remaining} 次，"
        detail += f"达到 {login_limiter.max_attempts} 次将锁定 {login_limiter.lockout_seconds // 60} 分钟）"
    raise HTTPException(status_code=401, detail=detail)


def _warn_if_weak_password(user) -> None:
    """登录成功时，如果该账号还在用出厂默认密码就提示改掉。"""
    weak = WEAK_DEFAULTS["TK_ADMIN_PASSWORD"]
    if user.username == DEFAULT_ADMIN_USERNAME and verify_password(weak, user.password_hash):
        print(
            f"⚠️ 安全告警：管理员 {user.username!r} 仍在使用出厂默认密码，"
            "请执行 .venv/bin/python scripts/set_admin_password.py 修改。"
        )


@router.post("/api/auth/reset-admin")
def reset_admin_password(
    payload: ResetPasswordPayload,
    request: Request,
    session: Session = Depends(get_session),
):
    # 该接口只有 PIN、没有账号维度，按 IP 限流
    rate_key = f"reset|{_client_ip(request)}"
    _reject_if_locked(reset_pin_limiter, rate_key)

    # 用 compare_digest 避免通过响应时间差逐字节猜 PIN
    if not hmac.compare_digest(payload.security_pin, MASTER_SECURITY_PIN):
        reset_pin_limiter.record_failure(rate_key)
        raise HTTPException(status_code=403, detail="安全密钥错误，拒绝重置！")

    reset_pin_limiter.reset(rate_key)

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
