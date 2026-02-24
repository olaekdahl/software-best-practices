"""
Demo 01 - Basic pytest Testing
================================
Simplest possible tests to introduce pytest conventions.

Instructor talking points:
- Test functions start with test_
- Use plain assert statements
- pytest auto-discovers test files and functions
- Rich failure output shows actual vs expected

Run: pytest -v test_calculator.py
"""


# ----- Source code -----
def add(a: int, b: int) -> int:
    return a + b


def subtract(a: int, b: int) -> int:
    return a - b


def multiply(a: int, b: int) -> int:
    return a * b


def divide(a: float, b: float) -> float:
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b


# ----- Tests -----
def test_add_positive_numbers():
    assert add(2, 3) == 5


def test_add_negative_numbers():
    assert add(-1, -1) == -2


def test_add_zero():
    assert add(0, 5) == 5


def test_subtract():
    assert subtract(10, 4) == 6


def test_multiply():
    assert multiply(3, 4) == 12


def test_divide():
    assert divide(10, 2) == 5.0


def test_divide_by_zero_raises():
    """Test that dividing by zero raises ValueError."""
    import pytest
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        divide(10, 0)


def test_add_returns_int():
    """Test return type."""
    result = add(1, 2)
    assert isinstance(result, int)
