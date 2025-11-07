from __future__ import annotations

"""Acceptance-style test (Given-When-Then) for a simple shopping total.

Scenario: As a shopper, I want to see my total with tax so that I know what I pay.
Given a unit price and quantity
When I calculate the total with a tax rate
Then I see the correct amount rounded to 2 decimals
"""

from importlib.util import spec_from_file_location, module_from_spec
from pathlib import Path

SRC = Path(__file__).resolve().parents[2] / "src" / "calculator.py"
spec = spec_from_file_location("calculator", SRC)
assert spec and spec.loader
mod = module_from_spec(spec)
spec.loader.exec_module(mod)  # type: ignore[attr-defined]
add = mod.add
multiply = mod.multiply


def compute_total(price: float, qty: int, tax_rate: float) -> float:
    subtotal = multiply(price, qty)
    tax = subtotal * tax_rate
    return round(add(subtotal, tax), 2)


def test_shopper_total_acceptance():
    # Given
    price = 19.99
    qty = 3
    tax_rate = 0.0825

    # When
    total = compute_total(price, qty, tax_rate)

    # Then
    assert total == 64.92  # 19.99*3=59.97, tax≈4.9475 → total≈64.9175 → round(2)=64.92
