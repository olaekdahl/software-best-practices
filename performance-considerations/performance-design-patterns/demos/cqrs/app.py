from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class CreateOrder:
    order_id: str
    total: float

@dataclass(frozen=True)
class GetOrderSummary:
    order_id: str

# Write model (optimized for writes)
ORDERS_WRITE: dict[str, dict] = {}

# Read model (optimized for reads; denormalized)
ORDERS_READ: dict[str, dict] = {}

def handle_create(cmd: CreateOrder) -> None:
    ORDERS_WRITE[cmd.order_id] = {"order_id": cmd.order_id, "total": cmd.total}
    # Projection update (in real systems often async)
    ORDERS_READ[cmd.order_id] = {"order_id": cmd.order_id, "total": cmd.total, "status": "CREATED"}

def handle_get(q: GetOrderSummary) -> dict:
    return ORDERS_READ[q.order_id]

def main() -> None:
    handle_create(CreateOrder("O-100", 42.50))
    handle_create(CreateOrder("O-101", 13.37))

    print("Read model is separate and optimized for queries:")
    print(handle_get(GetOrderSummary("O-100")))

if __name__ == "__main__":
    main()
