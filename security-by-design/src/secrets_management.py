"""
Demo 04 - Secrets Management
===============================
Demonstrates proper secrets handling: env vars, config files, rotation.

Instructor talking points:
- Never hardcode secrets in source code
- Load from environment variables or secret managers
- Support rotation without restart
- Audit and log access (not the secret values)
- Fail fast if required secrets are missing

Run: python main.py
     SECRET_DB_PASSWORD=mypass123 API_KEY=sk-test-abc python main.py
"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from typing import Protocol


# ============================================================================
# Secret loading abstraction
# ============================================================================

class SecretProvider(Protocol):
    """Port for secret retrieval."""
    def get_secret(self, key: str) -> str | None: ...


class EnvironmentSecretProvider:
    """Load secrets from environment variables.

    This is the simplest provider. In production, use a vault client.
    """
    def get_secret(self, key: str) -> str | None:
        return os.environ.get(key)


class FileSecretProvider:
    """Load secrets from files (e.g., Kubernetes volume mounts).

    Secrets are mounted as files at /run/secrets/<key>.
    """
    def __init__(self, base_path: str = "/run/secrets"):
        self._base_path = base_path

    def get_secret(self, key: str) -> str | None:
        path = os.path.join(self._base_path, key)
        try:
            with open(path) as f:
                return f.read().strip()
        except FileNotFoundError:
            return None


class InMemorySecretProvider:
    """In-memory secrets for testing (never in production)."""
    def __init__(self, secrets: dict[str, str]):
        self._secrets = secrets

    def get_secret(self, key: str) -> str | None:
        return self._secrets.get(key)


# ============================================================================
# Secret manager with validation, caching, and rotation
# ============================================================================

@dataclass
class SecretMetadata:
    key: str
    loaded_at: float
    ttl_seconds: float
    access_count: int = 0


class SecretManager:
    """Centralized secret management with caching, rotation, and audit."""

    def __init__(
        self,
        provider: SecretProvider,
        default_ttl: float = 300.0,  # 5 minutes default cache TTL
    ):
        self._provider = provider
        self._default_ttl = default_ttl
        self._cache: dict[str, str] = {}
        self._metadata: dict[str, SecretMetadata] = {}
        self._audit_log: list[dict] = []

    def get(self, key: str, required: bool = True) -> str | None:
        """Get a secret, with caching and audit logging.

        Args:
            key: Secret key name
            required: If True, raises if secret is missing
        """
        # Check cache freshness
        if key in self._cache:
            meta = self._metadata[key]
            age = time.time() - meta.loaded_at
            if age < meta.ttl_seconds:
                meta.access_count += 1
                self._log_access(key, "cache_hit")
                return self._cache[key]
            else:
                self._log_access(key, "cache_expired")
                del self._cache[key]
                del self._metadata[key]

        # Load from provider
        value = self._provider.get_secret(key)
        if value is None:
            self._log_access(key, "not_found")
            if required:
                raise EnvironmentError(
                    f"Required secret '{key}' not found. "
                    f"Set it as an environment variable or configure a secret provider."
                )
            return None

        # Cache it
        self._cache[key] = value
        self._metadata[key] = SecretMetadata(
            key=key,
            loaded_at=time.time(),
            ttl_seconds=self._default_ttl,
        )
        self._log_access(key, "loaded")

        # Never log the secret value
        return value

    def rotate(self, key: str) -> str | None:
        """Force refresh a secret from the provider (rotation)."""
        if key in self._cache:
            del self._cache[key]
            del self._metadata[key]
        self._log_access(key, "rotated")
        return self.get(key, required=False)

    def _log_access(self, key: str, action: str) -> None:
        """Audit log secret access (never log the value)."""
        entry = {
            "timestamp": time.time(),
            "key": key,
            "action": action,
        }
        self._audit_log.append(entry)
        print(f"  [SecretAudit] {action}: {key}")

    def get_audit_log(self) -> list[dict]:
        return list(self._audit_log)

    def get_stats(self) -> dict:
        """Return cache statistics."""
        return {
            "cached_keys": list(self._cache.keys()),
            "total_accesses": sum(
                m.access_count for m in self._metadata.values()
            ),
            "audit_entries": len(self._audit_log),
        }


# ============================================================================
# Application configuration using secrets
# ============================================================================

@dataclass
class AppConfig:
    """Application configuration loaded from secrets."""
    db_host: str
    db_port: int
    db_password: str
    api_key: str
    jwt_secret: str
    debug: bool = False

    @classmethod
    def from_secrets(cls, sm: SecretManager) -> AppConfig:
        """Load configuration from secret manager.

        Validates all required secrets are present at startup.
        """
        return cls(
            db_host=sm.get("DB_HOST", required=False) or "localhost",
            db_port=int(sm.get("DB_PORT", required=False) or "5432"),
            db_password=sm.get("SECRET_DB_PASSWORD", required=True),
            api_key=sm.get("API_KEY", required=True),
            jwt_secret=sm.get("JWT_SECRET", required=True),
            debug=sm.get("DEBUG", required=False) == "true",
        )


# ============================================================================
# Main demo
# ============================================================================

def main():
    print("=== Demo: Secrets Management ===\n")

    # --- Using environment provider ---
    print("--- Environment Secret Provider ---")
    env_provider = EnvironmentSecretProvider()
    sm = SecretManager(env_provider, default_ttl=60.0)

    # Check if secrets are set
    db_pass = sm.get("SECRET_DB_PASSWORD", required=False)
    if db_pass:
        print(f"  DB password loaded (length: {len(db_pass)})")
    else:
        print("  DB password not set in environment")
        print("  Try: SECRET_DB_PASSWORD=mypass123 API_KEY=sk-test JWT_SECRET=jwt-demo python main.py")

    print()

    # --- Using in-memory provider (for demo) ---
    print("--- In-Memory Secret Provider (Demo) ---")
    demo_provider = InMemorySecretProvider({
        "SECRET_DB_PASSWORD": "s3cur3-p@ss!",
        "API_KEY": "sk-live-abc123",
        "JWT_SECRET": "jwt-signing-key-256bit",
        "DB_HOST": "db.internal.example.com",
        "DB_PORT": "5432",
    })
    sm = SecretManager(demo_provider, default_ttl=5.0)  # Short TTL for demo

    # Load config
    config = AppConfig.from_secrets(sm)
    print(f"  DB Host: {config.db_host}")
    print(f"  DB Port: {config.db_port}")
    print(f"  DB Password loaded: {'*' * len(config.db_password)}")
    print(f"  API Key loaded: {config.api_key[:8]}...")
    print()

    # --- Caching behavior ---
    print("--- Secret Caching ---")
    sm.get("API_KEY")  # Should be cache hit
    sm.get("API_KEY")  # Should be cache hit
    print()

    # --- Rotation ---
    print("--- Secret Rotation ---")
    sm.rotate("API_KEY")
    sm.get("API_KEY")  # Reloaded from provider
    print()

    # --- Missing required secret ---
    print("--- Missing Required Secret ---")
    try:
        sm.get("NONEXISTENT_SECRET", required=True)
    except EnvironmentError as e:
        print(f"  Error (expected): {e}")
    print()

    # --- Audit log ---
    print("--- Audit Log ---")
    for entry in sm.get_audit_log()[-5:]:
        print(f"  {entry['action']:15s} -> {entry['key']}")
    print()

    # --- Statistics ---
    print("--- Cache Statistics ---")
    stats = sm.get_stats()
    print(f"  Cached keys: {stats['cached_keys']}")
    print(f"  Total accesses: {stats['total_accesses']}")
    print(f"  Audit entries: {stats['audit_entries']}")

    print("\n--- Security Best Practices ---")
    print("1. Never hardcode secrets in source code")
    print("2. Load from env vars or secret managers (Vault, AWS SM, etc.)")
    print("3. Cache with TTL for performance; rotate on schedule")
    print("4. Audit log all secret access (never log values)")
    print("5. Fail fast if required secrets are missing")
    print("6. Mask secret values in logs and output")
    print("7. Use workload identity for secret retrieval")


if __name__ == "__main__":
    main()
