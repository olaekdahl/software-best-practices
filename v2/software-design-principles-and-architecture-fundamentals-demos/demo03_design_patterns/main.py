"""
Demo 03 - Design Patterns: Strategy, Adapter, Observer
=======================================================
Demonstrates three key patterns in a realistic order processing system.

Instructor talking points:
- Strategy: Swap shipping cost algorithms at runtime
- Adapter: Wrap third-party payment SDK behind a clean port
- Observer: Decouple side effects (email, audit log) from order logic

Run: python main.py
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


# ===== STRATEGY PATTERN =====
# Encapsulate shipping cost algorithms behind a common interface.
# Adding a new shipping method requires NO changes to OrderProcessor.

class ShippingStrategy(Protocol):
    """Calculate shipping cost for a given order weight."""
    def cost(self, weight_kg: float) -> float: ...


class StandardShipping:
    """Flat rate + per-kg charge."""
    def cost(self, weight_kg: float) -> float:
        return 5.00 + weight_kg * 0.50


class ExpressShipping:
    """Premium rate for next-day delivery."""
    def cost(self, weight_kg: float) -> float:
        return 15.00 + weight_kg * 1.00


class FreeShipping:
    """Promotional free shipping."""
    def cost(self, weight_kg: float) -> float:
        return 0.0


# ===== ADAPTER PATTERN =====
# Third-party payment SDK has an incompatible interface.
# The adapter translates between our domain port and the vendor API.

class StripeSDK:
    """Simulated third-party Stripe SDK with vendor-specific interface."""
    def create_charge(self, amount_cents: int, currency: str, token: str) -> dict:
        # In reality this would call Stripe's API
        return {
            "id": f"ch_{token[:8]}",
            "amount": amount_cents,
            "currency": currency,
            "status": "succeeded",
        }


class PaymentPort(Protocol):
    """Our domain's payment interface - clean and vendor-agnostic."""
    def pay(self, amount: float, reference: str) -> bool: ...


class StripeAdapter:
    """Translates our PaymentPort to Stripe's SDK interface."""
    def __init__(self, sdk: StripeSDK, currency: str = "usd"):
        self._sdk = sdk
        self._currency = currency

    def pay(self, amount: float, reference: str) -> bool:
        result = self._sdk.create_charge(
            amount_cents=int(amount * 100),
            currency=self._currency,
            token=reference,
        )
        success = result["status"] == "succeeded"
        print(f"  [Stripe] Charge {result['id']}: ${amount:.2f} -> {result['status']}")
        return success


# ===== OBSERVER PATTERN =====
# Decouple side effects from core order logic.
# Adding a new observer (e.g., analytics) requires no changes to OrderProcessor.

class OrderEvent:
    """Immutable event published when an order is completed."""
    def __init__(self, order_id: str, customer: str, total: float):
        self.order_id = order_id
        self.customer = customer
        self.total = total


class OrderObserver(Protocol):
    """Observers react to order events without coupling to order logic."""
    def on_order_completed(self, event: OrderEvent) -> None: ...


class EmailObserver:
    """Sends confirmation email when order is completed."""
    def on_order_completed(self, event: OrderEvent) -> None:
        print(f"  [Email] Sending confirmation to {event.customer} "
              f"for order {event.order_id} (${event.total:.2f})")


class AuditLogObserver:
    """Records order in audit log for compliance."""
    def on_order_completed(self, event: OrderEvent) -> None:
        print(f"  [Audit] Order {event.order_id} completed: "
              f"customer={event.customer}, total=${event.total:.2f}")


class AnalyticsObserver:
    """Tracks order metrics for business intelligence."""
    def on_order_completed(self, event: OrderEvent) -> None:
        print(f"  [Analytics] Tracked order {event.order_id}: ${event.total:.2f}")


# ===== ORDER PROCESSOR =====
# Combines all patterns: strategy for shipping, adapter for payment, observer for events.

@dataclass
class OrderItem:
    name: str
    price: float
    weight_kg: float


class OrderProcessor:
    def __init__(
        self,
        shipping: ShippingStrategy,
        payment: PaymentPort,
    ):
        self._shipping = shipping
        self._payment = payment
        self._observers: list[OrderObserver] = []
        self._order_counter = 0

    def add_observer(self, observer: OrderObserver) -> None:
        self._observers.append(observer)

    def _notify(self, event: OrderEvent) -> None:
        for observer in self._observers:
            observer.on_order_completed(event)

    def process(self, customer: str, items: list[OrderItem], token: str) -> dict | None:
        self._order_counter += 1
        order_id = f"ORD-{self._order_counter:04d}"

        subtotal = sum(item.price for item in items)
        total_weight = sum(item.weight_kg for item in items)

        # STRATEGY: Shipping cost calculated by injected strategy
        shipping_cost = self._shipping.cost(total_weight)
        total = subtotal + shipping_cost

        print(f"  Order {order_id}: subtotal=${subtotal:.2f}, "
              f"shipping=${shipping_cost:.2f}, total=${total:.2f}")

        # ADAPTER: Payment processed through adapted vendor SDK
        if not self._payment.pay(total, token):
            print(f"  Payment failed for {order_id}")
            return None

        # OBSERVER: Notify all observers without coupling
        event = OrderEvent(order_id, customer, total)
        self._notify(event)

        return {"order_id": order_id, "total": total, "status": "completed"}


def main():
    print("=== Demo: Design Patterns (Strategy, Adapter, Observer) ===\n")

    # --- Compose the system ---

    # ADAPTER: Wrap Stripe SDK
    stripe_sdk = StripeSDK()
    payment = StripeAdapter(stripe_sdk)

    # STRATEGY: Choose shipping method
    shipping = StandardShipping()

    # Create processor and add OBSERVERS
    processor = OrderProcessor(shipping, payment)
    processor.add_observer(EmailObserver())
    processor.add_observer(AuditLogObserver())
    processor.add_observer(AnalyticsObserver())

    # --- Process orders ---
    print("--- Order 1: Standard Shipping ---")
    items = [
        OrderItem("Laptop", 999.99, 2.5),
        OrderItem("Mouse", 29.99, 0.2),
    ]
    processor.process("Alice", items, "tok_alice_visa")
    print()

    # STRATEGY: Swap shipping at runtime
    print("--- Order 2: Express Shipping ---")
    processor._shipping = ExpressShipping()
    items = [OrderItem("Monitor", 449.99, 5.0)]
    processor.process("Bob", items, "tok_bob_mc")
    print()

    # STRATEGY: Free shipping promotion
    print("--- Order 3: Free Shipping Promo ---")
    processor._shipping = FreeShipping()
    items = [OrderItem("Keyboard", 79.99, 0.8)]
    processor.process("Charlie", items, "tok_charlie_amex")

    print("\n--- Pattern Benefits ---")
    print("STRATEGY: New shipping methods = new class, no changes to OrderProcessor")
    print("ADAPTER:  Switch from Stripe to Square = new adapter, domain unchanged")
    print("OBSERVER: Add SMS notifications = new observer, no changes to OrderProcessor")


if __name__ == "__main__":
    main()
