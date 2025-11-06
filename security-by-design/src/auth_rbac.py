from __future__ import annotations

import secrets
import bcrypt
from typing import Dict, Optional


_USERS: Dict[str, Dict[str, str]] = {}

def _hash_password(pw: str) -> str:
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()


def create_user(username: str, password: str, role: str = "user") -> None:
    _USERS[username] = {
        "password_hash": _hash_password(password),
        "role": role,
    }


def verify_password(username: str, password: str) -> bool:
    user = _USERS.get(username)
    if not user:
        return False
    return bcrypt.checkpw(password.encode(), user["password_hash"].encode())


def issue_token(username: str) -> str:
    # demo token (no signature); real systems use JWT/OAuth
    return secrets.token_hex(16) + f":{username}"


def parse_token(token: str) -> Optional[str]:
    if ":" not in token:
        return None
    _, username = token.split(":", 1)
    return username if username in _USERS else None


def require_role(role: str):
    def decorator(fn):
        def wrapper(user_role: str, *args, **kwargs):
            if user_role != role:
                raise PermissionError("insufficient role")
            return fn(*args, **kwargs)
        return wrapper
    return decorator


@require_role("admin")
def admin_task():
    return "sensitive admin data"


def _demo():
    print("-- create users --")
    create_user("alice", "StrongPass123", role="user")
    create_user("admin", "AdminPass456", role="admin")
    print(_USERS)

    print("\n-- login attempts --")
    print("alice ok:", verify_password("alice", "StrongPass123"))
    print("alice fail:", verify_password("alice", "wrong"))

    token = issue_token("admin")
    print("\nadmin token:", token)
    username = parse_token(token)
    role = _USERS[username]["role"] if username else None
    try:
        print("admin task:", admin_task(role))
    except Exception as e:
        print("unexpected:", e)
    try:
        print("unauthorized user task:", admin_task("user"))
    except Exception as e:
        print("blocked:", e)


if __name__ == "__main__":
    _demo()
