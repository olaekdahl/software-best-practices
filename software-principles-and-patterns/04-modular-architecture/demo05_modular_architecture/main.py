"""
Demo 05 - Modular Monolith with Clean Architecture
====================================================
A realistic order management system with clear module boundaries,
dependency inversion, and layered architecture.

Instructor talking points:
- Modules: orders, payments, notifications - each with clear boundaries
- Layers: domain (models, ports) -> application (services) -> infrastructure (adapters)
- Depend inward: infrastructure depends on domain, never the reverse
- Composition root wires everything together
- Each module is independently testable

Run: python main.py
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Protocol


# ============================================================================
# DOMAIN LAYER - Models, value objects, and port interfaces
# ============================================================================

class OrderStatus(Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    PAID = "paid"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


@dataclass
class Money:
    """Value object for monetary amounts."""
    amount: float
    currency: str = "USD"

    def __add__(self, other: Money) -> Money:
        if self.currency != other.currency:
            raise ValueError(f"Cannot add {self.currency} and {other.currency}")
        return Money(self.amount + other.amount, self.currency)

    def __mul__(self, factor: float) -> Money:
        return Money(self.amount * factor, self.currency)

    def __str__(self) -> str:
        return f"${self.amount:.2f} {self.currency}"


@dataclass
class OrderLine:
    product: str
    quantity: int
    unit_price: Money

    @property
    def line_total(self) -> Money:
        return self.unit_price * self.quantity


@dataclass
class Order:
    id: str
    customer_id: str
    lines: list[OrderLine] = field(default_factory=list)
    status: OrderStatus = OrderStatus.DRAFT
    created_at: str = ""
    payment_id: str | None = None

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()

    @property
    def subtotal(self) -> Money:
        if not self.lines:
            return Money(0.0)
        total = Money(0.0)
        for line in self.lines:
            total = total + line.line_total
        return total

    def submit(self) -> None:
        if self.status != OrderStatus.DRAFT:
            raise ValueError(f"Cannot submit order in {self.status.value} status")
        if not self.lines:
            raise ValueError("Cannot submit empty order")
        self.status = OrderStatus.SUBMITTED

    def mark_paid(self, payment_id: str) -> None:
        if self.status != OrderStatus.SUBMITTED:
            raise ValueError(f"Cannot pay order in {self.status.value} status")
        self.payment_id = payment_id
        self.status = OrderStatus.PAID

    def ship(self) -> None:
        if self.status != OrderStatus.PAID:
            raise ValueError(f"Cannot ship order in {self.status.value} status")
        self.status = OrderStatus.SHIPPED

    def cancel(self) -> None:
        if self.status in (OrderStatus.SHIPPED, OrderStatus.DELIVERED):
            raise ValueError(f"Cannot cancel order in {self.status.value} status")
        self.status = OrderStatus.CANCELLED


# ---------------------------------------------------------------------------
# Ports (interfaces) - defined in domain, implemented in infrastructure
# ---------------------------------------------------------------------------

class OrderRepository(Protocol):
    """Persistence port for orders."""
    def save(self, order: Order) -> None: ...
    def find_by_id(self, order_id: str) -> Order | None: ...
    def find_by_customer(self, customer_id: str) -> list[Order]: ...


class PaymentService(Protocol):
    """Payment port."""
    def charge(self, amount: Money, customer_id: str, order_id: str) -> str: ...
    def refund(self, payment_id: str) -> bool: ...


class NotificationService(Protocol):
    """Notification port."""
    def notify_order_confirmed(self, order: Order) -> None: ...
    def notify_order_shipped(self, order: Order) -> None: ...


class EventBus(Protocol):
    """Domain event publishing port."""
    def publish(self, event_type: str, payload: dict) -> None: ...


# ============================================================================
# APPLICATION LAYER - Use cases / services
# ============================================================================

class CreateOrderUseCase:
    """Use case: Create a new draft order."""
    def __init__(self, repo: OrderRepository):
        self._repo = repo

    def execute(self, customer_id: str, items: list[dict]) -> Order:
        order = Order(
            id=str(uuid.uuid4())[:8],
            customer_id=customer_id,
        )
        for item in items:
            order.lines.append(OrderLine(
                product=item["product"],
                quantity=item.get("quantity", 1),
                unit_price=Money(item["price"]),
            ))
        self._repo.save(order)
        return order


class SubmitOrderUseCase:
    """Use case: Submit (and pay for) an order."""
    def __init__(
        self,
        repo: OrderRepository,
        payments: PaymentService,
        notifications: NotificationService,
        events: EventBus,
    ):
        self._repo = repo
        self._payments = payments
        self._notifications = notifications
        self._events = events

    def execute(self, order_id: str) -> Order:
        order = self._repo.find_by_id(order_id)
        if not order:
            raise ValueError(f"Order {order_id} not found")

        # Submit
        order.submit()

        # Pay
        payment_id = self._payments.charge(
            order.subtotal, order.customer_id, order.id
        )
        order.mark_paid(payment_id)

        # Persist
        self._repo.save(order)

        # Notify
        self._notifications.notify_order_confirmed(order)

        # Publish event
        self._events.publish("order.paid", {
            "order_id": order.id,
            "customer_id": order.customer_id,
            "total": str(order.subtotal),
        })

        return order


class ShipOrderUseCase:
    """Use case: Ship a paid order."""
    def __init__(
        self,
        repo: OrderRepository,
        notifications: NotificationService,
        events: EventBus,
    ):
        self._repo = repo
        self._notifications = notifications
        self._events = events

    def execute(self, order_id: str) -> Order:
        order = self._repo.find_by_id(order_id)
        if not order:
            raise ValueError(f"Order {order_id} not found")

        order.ship()
        self._repo.save(order)
        self._notifications.notify_order_shipped(order)
        self._events.publish("order.shipped", {"order_id": order.id})
        return order


# ============================================================================
# INFRASTRUCTURE LAYER - Concrete implementations of ports
# ============================================================================

class InMemoryOrderRepository:
    """In-memory implementation of OrderRepository."""
    def __init__(self):
        self._store: dict[str, Order] = {}

    def save(self, order: Order) -> None:
        self._store[order.id] = order

    def find_by_id(self, order_id: str) -> Order | None:
        return self._store.get(order_id)

    def find_by_customer(self, customer_id: str) -> list[Order]:
        return [o for o in self._store.values() if o.customer_id == customer_id]


class ConsolePaymentService:
    """Simulated payment service (prints to console)."""
    def charge(self, amount: Money, customer_id: str, order_id: str) -> str:
        payment_id = f"PAY-{uuid.uuid4().hex[:8]}"
        print(f"    [Payment] Charged {amount} for order {order_id} -> {payment_id}")
        return payment_id

    def refund(self, payment_id: str) -> bool:
        print(f"    [Payment] Refunded {payment_id}")
        return True


class ConsoleNotificationService:
    """Simulated notification service (prints to console)."""
    def notify_order_confirmed(self, order: Order) -> None:
        print(f"    [Notify] Order {order.id} confirmed for customer {order.customer_id}")

    def notify_order_shipped(self, order: Order) -> None:
        print(f"    [Notify] Order {order.id} shipped to customer {order.customer_id}")


class ConsoleEventBus:
    """Simulated event bus (prints to console)."""
    def publish(self, event_type: str, payload: dict) -> None:
        print(f"    [Event] {event_type}: {payload}")


# ============================================================================
# COMPOSITION ROOT - Wire everything together
# ============================================================================

def main():
    print("=== Demo: Modular Monolith with Clean Architecture ===\n")

    # --- Infrastructure ---
    repo = InMemoryOrderRepository()
    payments = ConsolePaymentService()
    notifications = ConsoleNotificationService()
    events = ConsoleEventBus()

    # --- Use cases ---
    create_order = CreateOrderUseCase(repo)
    submit_order = SubmitOrderUseCase(repo, payments, notifications, events)
    ship_order = ShipOrderUseCase(repo, notifications, events)

    # --- Scenario 1: Full order lifecycle ---
    print("--- Scenario 1: Full Order Lifecycle ---")
    order = create_order.execute("CUST-001", [
        {"product": "Laptop", "price": 999.99, "quantity": 1},
        {"product": "Mouse", "price": 29.99, "quantity": 2},
    ])
    print(f"  Created order {order.id} ({order.status.value}), "
          f"subtotal={order.subtotal}")

    print()
    order = submit_order.execute(order.id)
    print(f"  Order {order.id} is now {order.status.value}")

    print()
    order = ship_order.execute(order.id)
    print(f"  Order {order.id} is now {order.status.value}")

    # --- Scenario 2: Multiple orders for same customer ---
    print("\n--- Scenario 2: Customer Order History ---")
    order2 = create_order.execute("CUST-001", [
        {"product": "Keyboard", "price": 79.99},
    ])
    submit_order.execute(order2.id)

    history = repo.find_by_customer("CUST-001")
    print(f"  Customer CUST-001 has {len(history)} orders:")
    for o in history:
        print(f"    {o.id}: {o.status.value} - {o.subtotal}")

    # --- Scenario 3: Invalid state transition ---
    print("\n--- Scenario 3: Invalid State Transition ---")
    try:
        order.ship()  # Already shipped
    except ValueError as e:
        print(f"  Caught expected error: {e}")

    print("\n--- Architecture Benefits ---")
    print("1. Domain layer has zero infrastructure imports")
    print("2. Swap InMemoryRepo for PostgresRepo without touching domain")
    print("3. Each use case is independently testable with mock ports")
    print("4. State machine in Order enforces valid transitions")
    print("5. Events decouple side effects from core logic")


if __name__ == "__main__":
    main()
