"""Tests for UserService with full coverage."""

from __future__ import annotations

import pytest

from src.user_service import FakeHasher, InMemoryUserStore, UserService


@pytest.fixture
def service() -> UserService:
    return UserService(store=InMemoryUserStore(), hasher=FakeHasher())


class TestRegister:
    def test_register_success(self, service: UserService) -> None:
        user = service.register("u1", "alice@example.com", "Alice", "secureP@ss1")
        assert user.user_id == "u1"
        assert user.email == "alice@example.com"
        assert user.name == "Alice"

    def test_register_invalid_email_raises(self, service: UserService) -> None:
        with pytest.raises(ValueError, match="Invalid email"):
            service.register("u1", "bad-email", "Alice", "secureP@ss1")

    def test_register_short_password_raises(self, service: UserService) -> None:
        with pytest.raises(ValueError, match="8 characters"):
            service.register("u1", "a@b.com", "Alice", "short")

    def test_register_duplicate_user_raises(self, service: UserService) -> None:
        service.register("u1", "a@b.com", "Alice", "secureP@ss1")
        with pytest.raises(ValueError, match="already exists"):
            service.register("u1", "b@c.com", "Bob", "secureP@ss1")


class TestAuthenticate:
    def test_authenticate_success(self, service: UserService) -> None:
        service.register("u1", "a@b.com", "Alice", "secureP@ss1")
        assert service.authenticate("u1", "secureP@ss1") is True

    def test_authenticate_wrong_password(self, service: UserService) -> None:
        service.register("u1", "a@b.com", "Alice", "secureP@ss1")
        assert service.authenticate("u1", "wrongpass") is False

    def test_authenticate_unknown_user(self, service: UserService) -> None:
        assert service.authenticate("nobody", "password") is False


class TestDelete:
    def test_delete_existing_user(self, service: UserService) -> None:
        service.register("u1", "a@b.com", "Alice", "secureP@ss1")
        assert service.delete_user("u1") is True

    def test_delete_nonexistent_user(self, service: UserService) -> None:
        assert service.delete_user("nobody") is False
