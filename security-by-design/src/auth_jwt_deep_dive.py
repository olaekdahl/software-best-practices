"""
Demo 03 - JWT Authentication with RBAC
=========================================
Demonstrates OAuth2/JWT patterns with role-based access control.

Instructor talking points:
- JWT creation with proper claims (iss, aud, exp, sub)
- Token validation: signature, expiry, issuer, audience
- RBAC enforcement with role-based decorators
- Short-lived tokens with refresh pattern
- Secure key handling

Run: pip install pyjwt cryptography && python main.py
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from functools import wraps
from typing import Any, Callable

import jwt


# ============================================================================
# Configuration
# ============================================================================

# In production, load from environment/vault
JWT_SECRET = "demo-secret-replace-in-production"
JWT_ALGORITHM = "HS256"
JWT_ISSUER = "https://auth.example.com"
JWT_AUDIENCE = "https://api.example.com"
ACCESS_TOKEN_MINUTES = 15
REFRESH_TOKEN_HOURS = 24


# ============================================================================
# Domain models
# ============================================================================

class Role(Enum):
    USER = "user"
    EDITOR = "editor"
    ADMIN = "admin"


# Role hierarchy: admin > editor > user
ROLE_HIERARCHY = {
    Role.USER: 0,
    Role.EDITOR: 1,
    Role.ADMIN: 2,
}


@dataclass
class TokenClaims:
    """Validated JWT claims."""
    sub: str          # Subject (user ID)
    email: str
    role: Role
    iss: str          # Issuer
    aud: str          # Audience
    exp: float        # Expiration
    iat: float        # Issued at
    jti: str | None = None  # JWT ID (for revocation)


# ============================================================================
# Token service
# ============================================================================

class TokenService:
    """Create and validate JWT tokens."""

    def __init__(
        self,
        secret: str,
        algorithm: str = JWT_ALGORITHM,
        issuer: str = JWT_ISSUER,
        audience: str = JWT_AUDIENCE,
    ):
        self._secret = secret
        self._algorithm = algorithm
        self._issuer = issuer
        self._audience = audience
        self._revoked: set[str] = set()  # In production, use Redis/DB

    def create_access_token(
        self,
        user_id: str,
        email: str,
        role: str,
        expires_minutes: int = ACCESS_TOKEN_MINUTES,
    ) -> str:
        """Create a short-lived access token."""
        now = datetime.now(timezone.utc)
        payload = {
            "sub": user_id,
            "email": email,
            "role": role,
            "iss": self._issuer,
            "aud": self._audience,
            "iat": now,
            "exp": now + timedelta(minutes=expires_minutes),
            "jti": f"{user_id}-{int(now.timestamp())}",
            "type": "access",
        }
        return jwt.encode(payload, self._secret, algorithm=self._algorithm)

    def create_refresh_token(
        self,
        user_id: str,
        expires_hours: int = REFRESH_TOKEN_HOURS,
    ) -> str:
        """Create a longer-lived refresh token."""
        now = datetime.now(timezone.utc)
        payload = {
            "sub": user_id,
            "iss": self._issuer,
            "aud": self._audience,
            "iat": now,
            "exp": now + timedelta(hours=expires_hours),
            "jti": f"refresh-{user_id}-{int(now.timestamp())}",
            "type": "refresh",
        }
        return jwt.encode(payload, self._secret, algorithm=self._algorithm)

    def validate_token(self, token: str, expected_type: str = "access") -> TokenClaims:
        """Validate a JWT token and return claims.

        Checks: signature, expiry, issuer, audience, type, revocation.
        """
        try:
            payload = jwt.decode(
                token,
                self._secret,
                algorithms=[self._algorithm],
                issuer=self._issuer,
                audience=self._audience,
                options={
                    "require": ["sub", "iss", "aud", "exp", "iat", "jti"],
                },
            )

            # Check token type
            if payload.get("type") != expected_type:
                raise ValueError(f"Expected {expected_type} token, got {payload.get('type')}")

            # Check revocation
            jti = payload.get("jti", "")
            if jti in self._revoked:
                raise ValueError("Token has been revoked")

            return TokenClaims(
                sub=payload["sub"],
                email=payload.get("email", ""),
                role=Role(payload.get("role", "user")),
                iss=payload["iss"],
                aud=payload["aud"],
                exp=payload["exp"],
                iat=payload["iat"],
                jti=jti,
            )

        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidIssuerError:
            raise ValueError("Invalid token issuer")
        except jwt.InvalidAudienceError:
            raise ValueError("Invalid token audience")
        except jwt.InvalidTokenError as e:
            raise ValueError(f"Invalid token: {e}")

    def revoke_token(self, jti: str) -> None:
        """Revoke a token by its JTI claim."""
        self._revoked.add(jti)


# ============================================================================
# RBAC - Role-Based Access Control
# ============================================================================

class AccessDeniedError(Exception):
    pass


def require_role(minimum_role: Role):
    """Decorator that enforces minimum role requirement."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(claims: TokenClaims, *args: Any, **kwargs: Any) -> Any:
            user_level = ROLE_HIERARCHY.get(claims.role, 0)
            required_level = ROLE_HIERARCHY.get(minimum_role, 0)
            if user_level < required_level:
                raise AccessDeniedError(
                    f"Role {claims.role.value} insufficient. "
                    f"Required: {minimum_role.value}"
                )
            return func(claims, *args, **kwargs)
        return wrapper
    return decorator


# ============================================================================
# Protected resources (simulated API endpoints)
# ============================================================================

@require_role(Role.USER)
def get_profile(claims: TokenClaims) -> dict:
    """Any authenticated user can view their profile."""
    return {"user_id": claims.sub, "email": claims.email, "role": claims.role.value}


@require_role(Role.EDITOR)
def update_content(claims: TokenClaims, content_id: str, data: str) -> dict:
    """Editors and admins can update content."""
    return {"action": "updated", "content_id": content_id, "by": claims.sub}


@require_role(Role.ADMIN)
def delete_user(claims: TokenClaims, target_user_id: str) -> dict:
    """Only admins can delete users."""
    return {"action": "deleted", "target": target_user_id, "by": claims.sub}


# ============================================================================
# Main demo
# ============================================================================

def main():
    print("=== Demo: JWT Authentication with RBAC ===\n")

    token_service = TokenService(JWT_SECRET)

    # --- Create tokens for different roles ---
    print("--- Creating Tokens ---")
    user_token = token_service.create_access_token("user-001", "alice@example.com", "user")
    editor_token = token_service.create_access_token("editor-001", "bob@example.com", "editor")
    admin_token = token_service.create_access_token("admin-001", "carol@example.com", "admin")

    print(f"  User token:   {user_token[:50]}...")
    print(f"  Editor token: {editor_token[:50]}...")
    print(f"  Admin token:  {admin_token[:50]}...")
    print()

    # --- Validate tokens ---
    print("--- Validating Tokens ---")
    user_claims = token_service.validate_token(user_token)
    print(f"  User claims: sub={user_claims.sub}, role={user_claims.role.value}")

    admin_claims = token_service.validate_token(admin_token)
    print(f"  Admin claims: sub={admin_claims.sub}, role={admin_claims.role.value}")
    print()

    # --- RBAC enforcement ---
    print("--- RBAC: User accessing profile (allowed) ---")
    result = get_profile(user_claims)
    print(f"  Result: {result}")
    print()

    print("--- RBAC: User trying to update content (denied) ---")
    try:
        update_content(user_claims, "doc-1", "new text")
    except AccessDeniedError as e:
        print(f"  Access denied: {e}")
    print()

    print("--- RBAC: Editor updating content (allowed) ---")
    editor_claims = token_service.validate_token(editor_token)
    result = update_content(editor_claims, "doc-1", "new text")
    print(f"  Result: {result}")
    print()

    print("--- RBAC: Editor trying to delete user (denied) ---")
    try:
        delete_user(editor_claims, "victim-001")
    except AccessDeniedError as e:
        print(f"  Access denied: {e}")
    print()

    print("--- RBAC: Admin deleting user (allowed) ---")
    result = delete_user(admin_claims, "banned-001")
    print(f"  Result: {result}")
    print()

    # --- Token revocation ---
    print("--- Token Revocation ---")
    token_service.revoke_token(user_claims.jti)
    try:
        token_service.validate_token(user_token)
    except ValueError as e:
        print(f"  Revoked token rejected: {e}")
    print()

    # --- Expired token ---
    print("--- Expired Token ---")
    expired_token = token_service.create_access_token(
        "user-002", "dave@example.com", "user", expires_minutes=-1
    )
    try:
        token_service.validate_token(expired_token)
    except ValueError as e:
        print(f"  Expired token rejected: {e}")
    print()

    # --- Refresh token flow ---
    print("--- Refresh Token Flow ---")
    refresh_token = token_service.create_refresh_token("user-001")
    refresh_claims = token_service.validate_token(refresh_token, expected_type="refresh")
    print(f"  Refresh token valid for: {refresh_claims.sub}")
    # In real code: issue new access token using refresh token claims
    new_access = token_service.create_access_token(
        refresh_claims.sub, "alice@example.com", "user"
    )
    print(f"  New access token issued: {new_access[:40]}...")

    print("\n--- Security Features ---")
    print("1. JWT with proper claims (sub, iss, aud, exp, iat, jti)")
    print("2. Token validation checks signature, expiry, issuer, audience")
    print("3. RBAC with role hierarchy enforcement")
    print("4. Token revocation via JTI tracking")
    print("5. Short-lived access tokens with refresh token pattern")
    print("6. Role decorators for clean access control")


if __name__ == "__main__":
    main()
