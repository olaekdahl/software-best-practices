"""Sample module with mixed quality for tooling demos."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

UNUSED_CONSTANT = 42  # Should be flagged by pylint (unused)


def add(a: int, b: int) -> int:
    return a + b


def risky_divide(a: float, b: float) -> float | None:
    """Divide with intentionally broad exception (lint will complain)."""
    try:
        return a / b
    except Exception:  # noqa: BLE001 - intentionally broad for demo
        return None


@dataclass
class Greeter:
    prefix: str = "Hello"

    def greet(self, name: str) -> str:
        return f"{self.prefix} {name}"


def complex_branch(x: int) -> str:
    """Function with uncovered branches to show coverage gaps."""
    if x < 0:
        return "negative"
    if x == 0:
        return "zero"
    if 0 < x < 10:
        return "small"
    return "large"


def insecure_eval(expr: str) -> Any:  # Bandit should flag use of eval
    return eval(expr)  # noqa: S307 - intentionally unsafe for demo
