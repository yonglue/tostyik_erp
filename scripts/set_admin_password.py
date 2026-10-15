#!/usr/bin/env python
"""修改管理员密码。

用法::

    # 交互输入（推荐，不会留在 shell 历史里）
    .venv/bin/python scripts/set_admin_password.py

    # 非交互（CI / 自动化；注意 shell 历史与进程列表可能泄露）
    TK_NEW_ADMIN_PASSWORD='...' .venv/bin/python scripts/set_admin_password.py

    # 指定账号（默认改 admin；也可改某个店员）
    .venv/bin/python scripts/set_admin_password.py --username cashier_juan
"""

import argparse
import getpass
import os
import sys
from pathlib import Path

# 允许从任意目录运行：把项目根加入 sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlmodel import Session, select  # noqa: E402

from app.config import DEFAULT_ADMIN_USERNAME, WEAK_DEFAULTS  # noqa: E402
from app.database import engine  # noqa: E402
from app.models import AdminUser, StaffUser  # noqa: E402
from app.security import hash_password, verify_password  # noqa: E402

MIN_LENGTH = 1
_FORBIDDEN = {WEAK_DEFAULTS["TK_ADMIN_PASSWORD"], WEAK_DEFAULTS["TK_MASTER_PIN"], "password", "123456"}


def _read_password() -> str:
    from_env = os.getenv("TK_NEW_ADMIN_PASSWORD", "")
    if from_env:
        return from_env

    pwd = getpass.getpass("新密码: ")
    again = getpass.getpass("再输入一次: ")
    if pwd != again:
        print("❌ 两次输入不一致。", file=sys.stderr)
        raise SystemExit(2)
    return pwd


def _validate(pwd: str) -> None:
    if pwd in _FORBIDDEN:
        print("❌ 该密码是已知的弱默认值，请换一个。", file=sys.stderr)
        raise SystemExit(2)
    if len(pwd) < MIN_LENGTH:
        print(f"❌ 密码至少 {MIN_LENGTH} 位（当前 {len(pwd)} 位）。", file=sys.stderr)
        raise SystemExit(2)
    kinds = sum([
        any(c.islower() for c in pwd),
        any(c.isupper() for c in pwd),
        any(c.isdigit() for c in pwd),
        any(not c.isalnum() for c in pwd),
    ])
    #if kinds < 2:
    #    print("❌ 密码过于单一，请混合大小写/数字/符号中的至少两类。", file=sys.stderr)
    #    raise SystemExit(2)


def main() -> int:
    parser = argparse.ArgumentParser(description="修改管理员或店员密码")
    parser.add_argument("--username", default=DEFAULT_ADMIN_USERNAME,
                        help=f"要修改的账号（默认 {DEFAULT_ADMIN_USERNAME}）")
    args = parser.parse_args()

    pwd = _read_password()
    _validate(pwd)

    with Session(engine) as session:
        target = None
        for model in (AdminUser, StaffUser):
            target = session.exec(
                select(model).where(model.username == args.username)
            ).first()
            if target:
                break

        if not target:
            print(f"❌ 账号 {args.username!r} 不存在。", file=sys.stderr)
            return 1

        if verify_password(pwd, target.password_hash):
            print("ℹ️  新密码与当前密码相同，未做修改。")
            return 0

        target.password_hash = hash_password(pwd)
        session.add(target)
        session.commit()

    print(f"✅ 账号 {args.username!r} 的密码已更新。")
    print("   提示：已签发的访问令牌仍然有效，直到过期（默认 12 小时）。")
    print("   如需立刻让所有令牌失效，更换 TK_JWT_SECRET 或删除 .jwt_secret 后重启。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
