# SRP + OCP (bad): monolithic and closed to extension
# Talking points:
# - Adding a discount means editing this class (OCP violation).
# - Business rules mixed with orchestration (SRP violation).
# - Harder to test rules in isolation.
#
# Problems:
# - SRP: One class computes totals, interprets discount codes, and orchestrates everything.
# - OCP: Adding a new discount requires modifying apply_discount (risking regressions).
from dataclasses import dataclass
from typing import List


@dataclass
class LineItem:
    sku: str
    price: float
    qty: int


@dataclass
class Order:
    items: List[LineItem]


class OrderProcessor:
    def total(self, items: List[LineItem]) -> float:
        # Not terrible, but tied to OrderProcessor; harder to reuse/test in isolation
        return sum(i.price * i.qty for i in items)

    def apply_discount(self, code: str, total: float) -> float:
        # OCP violation: every new code requires modifying this method.
        # Also bakes policy into the class, preventing runtime composition.
        if not code:
            return total
        if code == "WELCOME10":
            return round(total * 0.90, 2)
        elif code == "VIP":
            return round(total * 0.80, 2)
        elif code == "BLACKFRIDAY":
            return round(total * 0.70, 2)
        else:
            return total

    def process(self, order: Order, discount_code: str | None = None) -> float:
        # Orchestrates and contains business rules → many reasons to change
        t = self.total(order.items)
        t = self.apply_discount(discount_code or "", t)
        print(f"[BAD] total after discount '{discount_code}': {t}")
        return t


if __name__ == "__main__":
    order = Order(items=[LineItem("A", 10.0, 2), LineItem("B", 5.0, 3)])
    OrderProcessor().process(order, "VIP")
