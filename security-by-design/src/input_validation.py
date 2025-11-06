from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Final

from pydantic import BaseModel, EmailStr, constr


SAFE_NAME: Final = re.compile(r"^[a-zA-Z0-9 _.-]{1,50}$")


def sanitize_filename(name: str) -> str:
    """Allow-list characters and strip path separators to prevent traversal."""
    # Normalize and reject traversal
    name = name.replace("..", "_").replace("/", "_").replace("\\", "_")
    if not SAFE_NAME.match(name):
        raise ValueError("Invalid filename")
    return name


def validate_search_query(q: str) -> str:
    if len(q) > 64:
        raise ValueError("query too long")
    if not re.match(r"^[a-zA-Z0-9 _.-]+$", q):
        raise ValueError("query contains invalid characters")
    return q


class Signup(BaseModel):
    username: constr(min_length=3, max_length=32, pattern=r"^[a-zA-Z0-9_.-]+$")
    email: EmailStr
    password: constr(min_length=8)


def _demo():
    print("-- filename sanitization --")
    good = sanitize_filename("report-01.txt")
    print("ok:", good)
    for bad in ["../../etc/passwd", "a*bad|name", "", "x" * 200]:
        try:
            sanitize_filename(bad)
        except Exception as e:
            print("rejected:", bad, e)

    print("\n-- search query --")
    for q in ["test", "a b", "DROP TABLE;"]:
        try:
            print("query:", validate_search_query(q))
        except Exception as e:
            print("rejected:", q, e)

    print("\n-- signup model --")
    try:
        u = Signup(username="user_1", email="u@example.com", password="password123")
        print("valid:", u.model_dump())
    except Exception as e:
        print("unexpected:", e)
    try:
        Signup(username="bad name", email="not-an-email", password="short")
    except Exception as e:
        print("rejected invalid signup:", e)


if __name__ == "__main__":
    _demo()
