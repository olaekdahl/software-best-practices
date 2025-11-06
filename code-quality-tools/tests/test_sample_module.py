from __future__ import annotations

import math
import sys
from pathlib import Path

# Make local src importable despite hyphen in folder name
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from sample_module import add, Greeter, risky_divide, complex_branch  # type: ignore


def test_add():
    assert add(2, 3) == 5


def test_greeter():
    g = Greeter(prefix="Hi")
    assert g.greet("Ola") == "Hi Ola"


def test_risky_divide_zero():
    assert risky_divide(4, 0) is None


def test_complex_branch_small():
    assert complex_branch(5) == "small"


def test_complex_branch_large():
    assert complex_branch(25) == "large"
