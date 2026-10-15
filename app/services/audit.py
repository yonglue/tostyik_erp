"""操作审计日志。"""

from sqlmodel import Session

from app.models import AuditLog


def log_action(session: Session, username: str, role: str, action: str, details: str) -> None:
    """写入一条审计日志。

    审计失败绝不影响主业务，因此异常只打印不抛出（与原实现一致）。
    """
    try:
        log = AuditLog(username=username, role=role, action=action, details=details)
        session.add(log)
        session.commit()
    except Exception as e:  # noqa: BLE001 - 有意吞掉，避免审计故障中断业务
        print(f"写入操作日志异常: {e}")
