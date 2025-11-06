"""Secure configuration patterns."""

from __future__ import annotations

import os

from functools import lru_cache

class ConfigError(RuntimeError):
    pass

@lru_cache(maxsize=1)
def get_api_key() -> str:
    key = os.getenv("APP_API_KEY")
    if not key:
        raise ConfigError("APP_API_KEY not set")
    if len(key) < 16:
        raise ConfigError("APP_API_KEY too short")
    return key

def safe_error(msg: str = "Unexpected error") -> str:
    # Generic message; specifics go to logs
    return msg
