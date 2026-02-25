"""
Demo 05 - Full Quality Pipeline
=================================
A realistic project with ruff, mypy, pytest+coverage, and pre-commit.

Instructor talking points:
- pyproject.toml centralizes all tool configuration
- Ruff replaces flake8+isort+pyupgrade in one fast tool
- mypy catches type errors before runtime
- Coverage sets a floor, not a target
- Pre-commit hooks run checks before every commit
- CI workflow enforces all gates

Run:
    pytest --cov --cov-report=term-missing -v
    ruff check .
    mypy src/
"""

from __future__ import annotations


# ============================================================================
# Source module: src/user_service.py
# ============================================================================

from dataclasses import dataclass
from typing import Protocol


class UserStore(Protocol):
    """Port for user persistence."""

    def save(self, user_id: str, data: dict[str, str]) -> None: ...
    def load(self, user_id: str) -> dict[str, str] | None: ...
    def delete(self, user_id: str) -> bool: ...


class Hasher(Protocol):
    """Port for password hashing."""

    def hash(self, password: str) -> str: ...
    def verify(self, password: str, hashed: str) -> bool: ...


@dataclass
class User:
    """Domain model for a user."""

    user_id: str
    email: str
    name: str
    password_hash: str


class UserService:
    """Application service for user management."""

    def __init__(self, store: UserStore, hasher: Hasher) -> None:
        self._store = store
        self._hasher = hasher

    def register(self, user_id: str, email: str, name: str, password: str) -> User:
        if not email or "@" not in email:
            raise ValueError("Invalid email")
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters")

        existing = self._store.load(user_id)
        if existing is not None:
            raise ValueError(f"User {user_id} already exists")

        password_hash = self._hasher.hash(password)
        user = User(user_id=user_id, email=email, name=name, password_hash=password_hash)
        self._store.save(user_id, {
            "email": user.email,
            "name": user.name,
            "password_hash": user.password_hash,
        })
        return user

    def authenticate(self, user_id: str, password: str) -> bool:
        data = self._store.load(user_id)
        if data is None:
            return False
        return self._hasher.verify(password, data["password_hash"])

    def delete_user(self, user_id: str) -> bool:
        return self._store.delete(user_id)


# ============================================================================
# Infrastructure: In-memory implementations
# ============================================================================

class InMemoryUserStore:
    """In-memory user store for testing."""

    def __init__(self) -> None:
        self._data: dict[str, dict[str, str]] = {}

    def save(self, user_id: str, data: dict[str, str]) -> None:
        self._data[user_id] = data

    def load(self, user_id: str) -> dict[str, str] | None:
        return self._data.get(user_id)

    def delete(self, user_id: str) -> bool:
        return self._data.pop(user_id, None) is not None


class FakeHasher:
    """Fake hasher for testing (not secure - demo only)."""

    def hash(self, password: str) -> str:
        return f"hashed_{password}"

    def verify(self, password: str, hashed: str) -> bool:
        return hashed == f"hashed_{password}"
