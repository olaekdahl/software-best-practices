"""
Order Domain - Source of Truth for Living Documentation
========================================================
This module contains the order domain model. Documentation is generated
directly from the docstrings and type hints in this file.

The key principle: these docstrings serve double duty:
1. IDE tooltips and autocomplete help for developers
2. Auto-generated markdown API reference for the docs site
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


class OrderStatus:
    """Order lifecycle status.

    States flow: DRAFT -> SUBMITTED -> CONFIRMED -> SHIPPED -> DELIVERED
    Cancellation: DRAFT -> CANCELLED, SUBMITTED -> CANCELLED, CONFIRMED -> CANCELLED
    Returns: SHIPPED -> RETURNED -> CANCELLED
    """
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    CONFIRMED = "CONFIRMED"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"
    RETURNED = "RETURNED"


VALID_TRANSITIONS: dict[str, list[str]] = {
    OrderStatus.DRAFT: [OrderStatus.SUBMITTED, OrderStatus.CANCELLED],
    OrderStatus.SUBMITTED: [OrderStatus.CONFIRMED, OrderStatus.CANCELLED],
    OrderStatus.CONFIRMED: [OrderStatus.SHIPPED, OrderStatus.CANCELLED],
    OrderStatus.SHIPPED: [OrderStatus.DELIVERED, OrderStatus.RETURNED],
    OrderStatus.DELIVERED: [],
    OrderStatus.RETURNED: [OrderStatus.CANCELLED],
    OrderStatus.CANCELLED: [],
}


@dataclass
class OrderItem:
    """A single item in an order.

    Attributes:
        sku: Stock keeping unit identifier
        name: Human-readable product name
        quantity: Number of units (must be positive)
        unit_price: Price per unit in dollars
    """
    sku: str
    name: str
    quantity: int
    unit_price: float

    def __post_init__(self) -> None:
        if self.quantity < 1:
            raise ValueError(f"Quantity must be positive, got {self.quantity}")
        if self.unit_price < 0:
            raise ValueError(f"Unit price must be non-negative, got {self.unit_price}")

    @property
    def total(self) -> float:
        """Calculate line item total."""
        return self.quantity * self.unit_price


@dataclass
class Order:
    """Represents a customer order.

    An order progresses through a defined state machine from DRAFT
    to DELIVERED, with business rules enforced at each transition.

    Attributes:
        id: Unique order identifier (UUID format)
        customer_id: Reference to the customer placing the order
        items: Line items in the order
        status: Current order status
    """
    id: str
    customer_id: str
    items: list[OrderItem] = field(default_factory=list)
    status: str = OrderStatus.DRAFT

    def add_item(self, item: OrderItem) -> None:
        """Add an item to the order.

        Args:
            item: The order item to add

        Raises:
            ValueError: If order is not in DRAFT status

        Transitions: (none - stays in DRAFT)
        """
        if self.status != OrderStatus.DRAFT:
            raise ValueError(f"Cannot add items to {self.status} order")
        self.items.append(item)

    def submit(self) -> None:
        """Submit the order for processing.

        Transitions: DRAFT -> SUBMITTED

        Raises:
            ValueError: If order has no items or is not in DRAFT status
        """
        if self.status != OrderStatus.DRAFT:
            raise ValueError(f"Cannot submit {self.status} order")
        if not self.items:
            raise ValueError("Cannot submit empty order")
        self.status = OrderStatus.SUBMITTED

    def confirm(self) -> None:
        """Confirm the order after successful payment.

        Transitions: SUBMITTED -> CONFIRMED

        Raises:
            ValueError: If order is not in SUBMITTED status
        """
        if self.status != OrderStatus.SUBMITTED:
            raise ValueError(f"Cannot confirm {self.status} order")
        self.status = OrderStatus.CONFIRMED

    def ship(self, tracking_number: str) -> None:
        """Mark the order as shipped.

        Transitions: CONFIRMED -> SHIPPED

        Args:
            tracking_number: Carrier tracking number

        Raises:
            ValueError: If order is not in CONFIRMED status
        """
        if self.status != OrderStatus.CONFIRMED:
            raise ValueError(f"Cannot ship {self.status} order")
        self.status = OrderStatus.SHIPPED

    def deliver(self) -> None:
        """Mark the order as delivered.

        Transitions: SHIPPED -> DELIVERED

        Raises:
            ValueError: If order is not in SHIPPED status
        """
        if self.status != OrderStatus.SHIPPED:
            raise ValueError(f"Cannot deliver {self.status} order")
        self.status = OrderStatus.DELIVERED

    def cancel(self) -> None:
        """Cancel the order.

        Transitions: DRAFT -> CANCELLED, SUBMITTED -> CANCELLED, CONFIRMED -> CANCELLED

        Raises:
            ValueError: If order cannot be cancelled from current status
        """
        cancellable = {OrderStatus.DRAFT, OrderStatus.SUBMITTED, OrderStatus.CONFIRMED}
        if self.status not in cancellable:
            raise ValueError(f"Cannot cancel {self.status} order")
        self.status = OrderStatus.CANCELLED

    @property
    def total(self) -> float:
        """Calculate order total across all items."""
        return sum(item.total for item in self.items)


class OrderRepository(Protocol):
    """Port for order persistence.

    Implementations must provide thread-safe access to order storage.
    """

    def save(self, order: Order) -> None:
        """Persist an order.

        Args:
            order: The order to save (insert or update)
        """
        ...

    def find_by_id(self, order_id: str) -> Order | None:
        """Find an order by ID.

        Args:
            order_id: The unique order identifier

        Returns:
            The order if found, None otherwise
        """
        ...

    def find_by_customer(self, customer_id: str) -> list[Order]:
        """Find all orders for a customer.

        Args:
            customer_id: The customer identifier

        Returns:
            List of orders, empty if none found
        """
        ...
