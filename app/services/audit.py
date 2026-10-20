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
        # 不 rollback 会让 Session 停在 needs-rollback 状态，调用方随后读取
        # 已过期对象（如 order.id / order.order_no）就会抛 PendingRollbackError，
        # 把已经成功提交的业务变成 500，客户端重试后重复扣库存。
        session.rollback()
        print(f"写入操作日志异常: {e}")
