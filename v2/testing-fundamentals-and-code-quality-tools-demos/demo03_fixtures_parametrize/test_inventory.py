"""
Demo 03 - Fixtures, Parametrization, and Markers
==================================================
Demonstrates pytest's power features for organized, maintainable tests.

Instructor talking points:
- Fixtures provide setup/teardown with dependency injection
- Parametrize avoids duplicated test code
- Markers categorize tests (unit, integration, slow)
- conftest.py shares fixtures across files

Run:
    pytest -v test_inventory.py
    pytest -v -m unit test_inventory.py
    pytest -v -m "not slow" test_inventory.py
"""

from __future__ import annotations

import json
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

import pytest


# ============================================================================
# Production code: Inventory system
# ============================================================================

@dataclass
class Product:
    sku: str
    name: str
    price: float
    quantity: int = 0


class InsufficientStockError(Exception):
    pass


class ProductNotFoundError(Exception):
    pass


class Inventory:
    """Simple inventory management system."""

    def __init__(self):
        self._products: dict[str, Product] = {}

    def add_product(self, product: Product) -> None:
        self._products[product.sku] = product

    def get_product(self, sku: str) -> Product:
        if sku not in self._products:
            raise ProductNotFoundError(f"Product {sku} not found")
        return self._products[sku]

    def restock(self, sku: str, quantity: int) -> int:
        product = self.get_product(sku)
        if quantity < 0:
            raise ValueError("Restock quantity must be positive")
        product.quantity += quantity
        return product.quantity

    def sell(self, sku: str, quantity: int) -> float:
        product = self.get_product(sku)
        if quantity > product.quantity:
            raise InsufficientStockError(
                f"Requested {quantity}, only {product.quantity} available"
            )
        product.quantity -= quantity
        return product.price * quantity

    def total_value(self) -> float:
        return sum(p.price * p.quantity for p in self._products.values())

    def low_stock(self, threshold: int = 5) -> list[Product]:
        return [p for p in self._products.values() if p.quantity < threshold]

    def export_json(self, path: Path) -> None:
        data = {
            sku: {
                "name": p.name,
                "price": p.price,
                "quantity": p.quantity,
            }
            for sku, p in self._products.items()
        }
        path.write_text(json.dumps(data, indent=2))

    def import_json(self, path: Path) -> int:
        data = json.loads(path.read_text())
        count = 0
        for sku, info in data.items():
            self.add_product(Product(
                sku=sku, name=info["name"],
                price=info["price"], quantity=info["quantity"],
            ))
            count += 1
        return count


# ============================================================================
# FIXTURES - Setup reusable test state
# ============================================================================

@pytest.fixture
def empty_inventory() -> Inventory:
    """Fresh empty inventory for each test."""
    return Inventory()


@pytest.fixture
def sample_products() -> list[Product]:
    """Standard set of test products."""
    return [
        Product("LAPTOP-001", "Developer Laptop", 1299.99, 10),
        Product("MOUSE-001", "Wireless Mouse", 29.99, 50),
        Product("KBD-001", "Mechanical Keyboard", 89.99, 25),
        Product("MON-001", "4K Monitor", 449.99, 3),
    ]


@pytest.fixture
def stocked_inventory(empty_inventory, sample_products) -> Inventory:
    """Inventory pre-loaded with sample products (fixture composability)."""
    for product in sample_products:
        empty_inventory.add_product(product)
    return empty_inventory


@pytest.fixture
def tmp_json_file(tmp_path) -> Path:
    """Temporary JSON file path (uses pytest built-in tmp_path)."""
    return tmp_path / "inventory.json"


# ============================================================================
# UNIT TESTS (marked with @pytest.mark.unit)
# ============================================================================

@pytest.mark.unit
class TestInventoryUnit:
    """Unit tests for core inventory operations."""

    def test_add_and_get_product(self, empty_inventory):
        product = Product("TEST-001", "Test Item", 9.99, 5)
        empty_inventory.add_product(product)
        result = empty_inventory.get_product("TEST-001")
        assert result.name == "Test Item"
        assert result.price == 9.99

    def test_get_nonexistent_product_raises(self, empty_inventory):
        with pytest.raises(ProductNotFoundError, match="FAKE-001"):
            empty_inventory.get_product("FAKE-001")

    def test_restock_increases_quantity(self, stocked_inventory):
        new_qty = stocked_inventory.restock("MOUSE-001", 10)
        assert new_qty == 60  # was 50

    def test_restock_negative_raises(self, stocked_inventory):
        with pytest.raises(ValueError, match="positive"):
            stocked_inventory.restock("MOUSE-001", -5)

    def test_sell_reduces_quantity_returns_total(self, stocked_inventory):
        total = stocked_inventory.sell("MOUSE-001", 3)
        assert total == pytest.approx(89.97)
        assert stocked_inventory.get_product("MOUSE-001").quantity == 47

    def test_sell_insufficient_stock_raises(self, stocked_inventory):
        with pytest.raises(InsufficientStockError, match="only 10 available"):
            stocked_inventory.sell("LAPTOP-001", 20)


# ============================================================================
# PARAMETRIZED TESTS - Multiple inputs, one test function
# ============================================================================

@pytest.mark.unit
class TestSellParametrized:
    """Parametrized tests covering multiple sell scenarios."""

    @pytest.mark.parametrize("sku,qty,expected_total", [
        ("LAPTOP-001", 1, 1299.99),
        ("MOUSE-001", 5, 149.95),
        ("KBD-001", 2, 179.98),
        ("MON-001", 1, 449.99),
    ], ids=["one-laptop", "five-mice", "two-keyboards", "one-monitor"])
    def test_sell_calculates_correct_total(
        self, stocked_inventory, sku, qty, expected_total
    ):
        total = stocked_inventory.sell(sku, qty)
        assert total == pytest.approx(expected_total)


@pytest.mark.unit
class TestLowStock:
    """Parametrized low-stock threshold tests."""

    @pytest.mark.parametrize("threshold,expected_count", [
        (5, 1),    # Only MON-001 has qty 3 (below 5)
        (10, 1),   # MON-001 still
        (30, 3),   # MON-001 (3), LAPTOP-001 (10), KBD-001 (25)
        (100, 4),  # All below 100
    ], ids=["threshold-5", "threshold-10", "threshold-30", "threshold-100"])
    def test_low_stock_threshold(
        self, stocked_inventory, threshold, expected_count
    ):
        low = stocked_inventory.low_stock(threshold)
        assert len(low) == expected_count


# ============================================================================
# INTEGRATION TESTS (marked with @pytest.mark.integration)
# ============================================================================

@pytest.mark.integration
class TestInventoryPersistence:
    """Integration tests for JSON import/export."""

    def test_export_creates_valid_json(self, stocked_inventory, tmp_json_file):
        stocked_inventory.export_json(tmp_json_file)
        data = json.loads(tmp_json_file.read_text())
        assert "LAPTOP-001" in data
        assert data["LAPTOP-001"]["price"] == 1299.99

    def test_import_loads_products(self, empty_inventory, stocked_inventory, tmp_json_file):
        stocked_inventory.export_json(tmp_json_file)
        count = empty_inventory.import_json(tmp_json_file)
        assert count == 4
        assert empty_inventory.get_product("LAPTOP-001").name == "Developer Laptop"

    def test_roundtrip_preserves_data(self, stocked_inventory, tmp_json_file):
        """Export then import should preserve all data."""
        original_value = stocked_inventory.total_value()
        stocked_inventory.export_json(tmp_json_file)

        new_inv = Inventory()
        new_inv.import_json(tmp_json_file)
        assert new_inv.total_value() == pytest.approx(original_value)


# ============================================================================
# SLOW TEST (demonstrates marker filtering)
# ============================================================================

@pytest.mark.slow
def test_large_inventory_performance(empty_inventory):
    """Slow test - demonstrates skipping with markers.

    Run with: pytest -m "not slow" to skip.
    """
    for i in range(10_000):
        empty_inventory.add_product(Product(f"ITEM-{i:06d}", f"Item {i}", 1.00, 1))
    assert empty_inventory.total_value() == pytest.approx(10_000.00)
