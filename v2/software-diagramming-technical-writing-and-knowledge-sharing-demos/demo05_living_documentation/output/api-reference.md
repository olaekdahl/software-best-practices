# Order Service API Reference

*Auto-generated from source code. Do not edit manually.*

## `OrderItem`

A single item in an order.

Attributes:
    sku: Stock keeping unit identifier
    name: Human-readable product name
    quantity: Number of units (must be positive)
    unit_price: Price per unit in dollars

### Attributes

| Name | Type | Description |
|------|------|-------------|
| `sku` | `str` | Stock keeping unit identifier |
| `name` | `str` | Human-readable product name |
| `quantity` | `int` | Number of units (must be positive) |
| `unit_price` | `float` | Price per unit in dollars |

### Methods

#### `__init__(self, sku: 'str', name: 'str', quantity: 'int', unit_price: 'float') -> None`

Initialize self.  See help(type(self)) for accurate signature.

#### `total() -> float`

Calculate line item total.
---

## `Order`

Represents a customer order.

An order progresses through a defined state machine from DRAFT
to DELIVERED, with business rules enforced at each transition.

Attributes:
    id: Unique order identifier (UUID format)
    customer_id: Reference to the customer placing the order
    items: Line items in the order
    status: Current order status

### Attributes

| Name | Type | Description |
|------|------|-------------|
| `id` | `str` | Unique order identifier (UUID format) |
| `customer_id` | `str` | Reference to the customer placing the order |
| `items` | `list[OrderItem]` | Line items in the order |
| `status` | `str` | Current order status |

### Methods

#### `__init__(self, id: 'str', customer_id: 'str', items: 'list[OrderItem]' = <factory>, status: 'str' = 'DRAFT') -> None`

Initialize self.  See help(type(self)) for accurate signature.

#### `add_item(self, item: 'OrderItem') -> 'None'`

Add an item to the order.

Args:
    item: The order item to add

Raises:
    ValueError: If order is not in DRAFT status

Transitions: (none - stays in DRAFT)

#### `cancel(self) -> 'None'`

Cancel the order.

Transitions: DRAFT -> CANCELLED, SUBMITTED -> CANCELLED, CONFIRMED -> CANCELLED

Raises:
    ValueError: If order cannot be cancelled from current status

#### `confirm(self) -> 'None'`

Confirm the order after successful payment.

Transitions: SUBMITTED -> CONFIRMED

Raises:
    ValueError: If order is not in SUBMITTED status

#### `deliver(self) -> 'None'`

Mark the order as delivered.

Transitions: SHIPPED -> DELIVERED

Raises:
    ValueError: If order is not in SHIPPED status

#### `ship(self, tracking_number: 'str') -> 'None'`

Mark the order as shipped.

Transitions: CONFIRMED -> SHIPPED

Args:
    tracking_number: Carrier tracking number

Raises:
    ValueError: If order is not in CONFIRMED status

#### `submit(self) -> 'None'`

Submit the order for processing.

Transitions: DRAFT -> SUBMITTED

Raises:
    ValueError: If order has no items or is not in DRAFT status

#### `total() -> float`

Calculate order total across all items.
---

## `OrderRepository`

Port for order persistence.

Implementations must provide thread-safe access to order storage.

### Methods

#### `__init__(self, *args, **kwargs)`


#### `find_by_customer(self, customer_id: 'str') -> 'list[Order]'`

Find all orders for a customer.

Args:
    customer_id: The customer identifier

Returns:
    List of orders, empty if none found

#### `find_by_id(self, order_id: 'str') -> 'Order | None'`

Find an order by ID.

Args:
    order_id: The unique order identifier

Returns:
    The order if found, None otherwise

#### `save(self, order: 'Order') -> 'None'`

Persist an order.

Args:
    order: The order to save (insert or update)
