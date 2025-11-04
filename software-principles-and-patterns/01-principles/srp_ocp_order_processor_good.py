# SRP + OCP (good): small responsibilities and open for extension via strategies
# Talking points:
# - Discounts are strategies you can add without modifying consumers (OCP).
# - Registry composes policy at runtime; Totaller keeps summation separate (SRP).
# - OrderProcessor orchestrates only; collaborators own rules.
#
# Design:
# - Totaller owns summation logic (SRP).
# - Discount is a Strategy; new discounts are added without changing OrderProcessor (OCP).
# - DiscountRegistry composes policy at runtime.
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Protocol, Dict, Type


@dataclass
class LineItem:
    sku: str
    price: float
    qty: int


@dataclass
class Order:
    items: List[LineItem]


class Discount(Protocol):
    def apply(self, total: float) -> float: ...


class NoDiscount:
    def apply(self, total: float) -> float:
        return total


class PercentOff:
    def __init__(self, pct: float) -> None:
        self.pct = pct

    def apply(self, total: float) -> float:
        return round(total * (1 - self.pct), 2)


class DiscountRegistry:
    def __init__(self) -> None:
        self._map: Dict[str, Discount] = {
            "": NoDiscount(),
            "WELCOME10": PercentOff(0.10),
            "VIP": PercentOff(0.20),
        }

    def get(self, code: str | None) -> Discount:
        return self._map.get(code or "", NoDiscount())

    def register(self, code: str, discount: Discount) -> None:
        # Open for extension: add new behaviors without modifying consumers
        self._map[code] = discount


class Totaller:
    def total(self, items: List[LineItem]) -> float:
        return sum(i.price * i.qty for i in items)


class OrderProcessor:
    def __init__(self, totaller: Totaller, discounts: DiscountRegistry):
        self.totaller = totaller
        self.discounts = discounts

    def process(self, order: Order, discount_code: str | None = None) -> float:
        # Orchestration only: delegate rules to collaborators
        t = self.totaller.total(order.items)
        t = self.discounts.get(discount_code).apply(t)
        print(f"[GOOD] total after discount '{discount_code}': {t}")
        return t


if __name__ == "__main__":
    order = Order(items=[LineItem("A", 10.0, 2), LineItem("B", 5.0, 3)])
    reg = DiscountRegistry()
    # OCP-friendly: add new code without modifying OrderProcessor
    reg.register("BLACKFRIDAY", PercentOff(0.30))
    OrderProcessor(Totaller(), reg).process(order, "BLACKFRIDAY")
