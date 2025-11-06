from __future__ import annotations

import math
import pytest

from importlib.util import spec_from_file_location, module_from_spec
from pathlib import Path

SRC = Path(__file__).resolve().parents[2] / "src" / "calculator.py"
spec = spec_from_file_location("calculator", SRC)
assert spec and spec.loader
mod = module_from_spec(spec)
spec.loader.exec_module(mod)  # type: ignore[attr-defined]
add = mod.add
subtract = mod.subtract
multiply = mod.multiply
divide = mod.divide


def test_add():
    assert add(2, 3) == 5
    assert add(-1, 1) == 0


def test_subtract():
    assert subtract(5, 3) == 2
    assert subtract(0, 5) == -5


def test_multiply():
    assert multiply(4, 2.5) == 10
    assert multiply(-2, 3) == -6


def test_divide():
    assert divide(10, 2) == 5
    assert math.isclose(divide(1, 3), 0.3333333333, rel_tol=1e-9)


def test_divide_by_zero():
    with pytest.raises(ValueError):
        divide(1, 0)
