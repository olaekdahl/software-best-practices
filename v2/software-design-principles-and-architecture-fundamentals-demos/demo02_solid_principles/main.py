"""
Demo 02 - SOLID Principles Applied
===================================
Refactored version of demo01 applying SOLID, DRY, KISS, and YAGNI.

Instructor talking points:
- SRP: Each class has one reason to change
- OCP: New discounts/tax strategies via new classes, not conditionals
- LSP: All shapes/strategies are interchangeable
- ISP: Small, focused Protocol interfaces
- DIP: Dependencies injected, not hard-coded
- DRY: Shared validation in one place
- KISS: Simple dict lookup instead of class hierarchy for trivial cases
- YAGNI: Only features that are needed

Run: python main.py
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Protocol

# ---------------------------------------------------------------------------
# DRY: Centralized validation
# ---------------------------------------------------------------------------
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def is_valid_email(email: str) -> bool:
    """Single source of truth for email validation."""
    return bool(EMAIL_RE.match(email))


# ---------------------------------------------------------------------------
# SRP: Order is just data
# ---------------------------------------------------------------------------
@dataclass
class Order:
    customer: str
    email: str
    items: list[tuple[str, float]]
    state: str
    subtotal: float = 0.0
    tax: float = 0.0
    total: float = 0.0
    status: str = "pending"


# ---------------------------------------------------------------------------
# OCP + ISP: Small protocol interfaces for extension
# ---------------------------------------------------------------------------
class TaxStrategy(Protocol):
    """Calculate tax for a given amount."""
    def compute(self, amount: float) -> float: ...


class PaymentGateway(Protocol):
    """Process a payment."""
    def charge(self, amount: float, description: str) -> bool: ...


class Notifier(Protocol):
    """Send a notification."""
    def send(self, recipient: str, message: str) -> None: ...


class Logger(Protocol):
    """Log a message."""
    def info(self, msg: str) -> None: ...


# ---------------------------------------------------------------------------
# OCP: Add new tax strategies without modifying existing code
# ---------------------------------------------------------------------------
class CaTax:
    def compute(self, amount: float) -> float:
        return amount * 0.0725


class NyTax:
    def compute(self, amount: float) -> float:
        return amount * 0.08


class TxTax:
    def compute(self, amount: float) -> float:
        return amount * 0.0625


class ZeroTax:
    def compute(self, amount: float) -> float:
        return 0.0


# KISS: Simple dict lookup for strategy selection
TAX_STRATEGIES: dict[str, TaxStrategy] = {
    "CA": CaTax(),
    "NY": NyTax(),
    "TX": TxTax(),
}


# ---------------------------------------------------------------------------
# OCP: Add new payment gateways without modifying existing code
# ---------------------------------------------------------------------------
class CreditCardGateway:
    def charge(self, amount: float, description: str) -> bool:
        print(f"  [CreditCard] Charged ${amount:.2f} for {description}")
        return True


class PayPalGateway:
    def charge(self, amount: float, description: str) -> bool:
        print(f"  [PayPal] Charged ${amount:.2f} for {description}")
        return True


# ---------------------------------------------------------------------------
# DIP: Concrete implementations for notification and logging
# ---------------------------------------------------------------------------
class EmailNotifier:
    def send(self, recipient: str, message: str) -> None:
        print(f"  [Email] To {recipient}: {message}")


class ConsoleLogger:
    def info(self, msg: str) -> None:
        print(f"  [LOG] {msg}")


# ---------------------------------------------------------------------------
# SRP: OrderService only orchestrates order creation
# DIP: All dependencies injected through constructor
# ---------------------------------------------------------------------------
class OrderService:
    def __init__(
        self,
        payment: PaymentGateway,
        notifier: Notifier,
        logger: Logger,
    ):
        self._payment = payment
        self._notifier = notifier
        self._log = logger
        self._orders: list[Order] = []

    def create_order(
        self,
        customer: str,
        email: str,
        items: list[tuple[str, float]],
        state: str,
    ) -> Order | None:
        # DRY: Reuse centralized validation
        if not is_valid_email(email):
            self._log.info(f"Invalid email: {email}")
            return None

        subtotal = sum(price for _, price in items)
        # OCP: Look up strategy; default to ZeroTax
        tax_strategy = TAX_STRATEGIES.get(state, ZeroTax())
        tax = tax_strategy.compute(subtotal)
        total = subtotal + tax

        # DIP: Uses injected payment gateway
        if not self._payment.charge(total, f"Order for {customer}"):
            return None

        order = Order(
            customer=customer,
            email=email,
            items=items,
            state=state,
            subtotal=subtotal,
            tax=tax,
            total=total,
            status="completed",
        )
        self._orders.append(order)

        # DIP: Uses injected notifier
        self._notifier.send(email, f"Your order total is ${total:.2f}")
        self._log.info(f"Order created for {customer}, total=${total:.2f}")
        return order

    @property
    def orders(self) -> list[Order]:
        return list(self._orders)


# ---------------------------------------------------------------------------
# SRP: Separate report generation
# ---------------------------------------------------------------------------
class ReportGenerator:
    def sales_summary(self, orders: list[Order]) -> None:
        print("\n=== Sales Report ===")
        grand_total = 0.0
        for order in orders:
            print(f"  {order.customer}: ${order.total:.2f}")
            grand_total += order.total
        print(f"  Grand Total: ${grand_total:.2f}")
        print("===================")


# ---------------------------------------------------------------------------
# SRP: Newsletter is its own concern
# ---------------------------------------------------------------------------
class NewsletterService:
    def __init__(self, logger: Logger):
        self._log = logger

    def subscribe(self, email: str) -> bool:
        # DRY: Reuse centralized validation
        if not is_valid_email(email):
            self._log.info(f"Invalid email for newsletter: {email}")
            return False
        print(f"  Subscribed {email} to newsletter")
        return True


# ---------------------------------------------------------------------------
# Main: Compose everything
# ---------------------------------------------------------------------------
def main():
    print("=== Demo: SOLID Principles Applied ===\n")

    # DIP: Wire dependencies at composition root
    logger = ConsoleLogger()
    payment = CreditCardGateway()
    notifier = EmailNotifier()

    order_service = OrderService(payment, notifier, logger)
    newsletter = NewsletterService(logger)
    reports = ReportGenerator()

    # Create orders
    order_service.create_order(
        "Alice", "alice@example.com",
        [("Widget", 29.99), ("Gadget", 49.99)], "CA"
    )
    print()

    order_service.create_order(
        "Bob", "bob@example.com",
        [("Widget", 29.99)], "NY"
    )
    print()

    # Newsletter
    newsletter.subscribe("charlie@example.com")
    print()

    # Report
    reports.sales_summary(order_service.orders)

    print("\n--- Improvements over demo01 ---")
    print("1. SRP: Order, OrderService, ReportGenerator, NewsletterService separated")
    print("2. OCP: New tax/payment via new class, no existing code changed")
    print("3. ISP: Small Protocol interfaces (TaxStrategy, PaymentGateway, etc.)")
    print("4. DIP: Dependencies injected at composition root")
    print("5. DRY: Email validation in one place (is_valid_email)")
    print("6. KISS: Dict lookup for strategies instead of class hierarchy")
    print("7. YAGNI: No CSV/XML export - not needed yet")


if __name__ == "__main__":
    main()
