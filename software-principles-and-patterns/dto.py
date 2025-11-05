# Translate at edges
# BAD
# api/controller.py
def create_order(request_json):
    # Raw dict goes straight into domain
    return domain.create_order(request_json)

# domain/usecase.py
def create_order(payload):
    # Domain now depends on HTTP field names & types 
    if "custId" not in payload or "items" not in payload:
        raise ValueError("bad input")
    # ... business logic mixed with validation ...

# GOOD
# api/dtos.py
from dataclasses import dataclass
from typing import List

@dataclass(frozen=True)
class NewOrderItemDTO:
    sku: str
    qty: int

@dataclass(frozen=True)
class NewOrderDTO:
    customer_id: int
    items: List[NewOrderItemDTO]

def parse_new_order(json_: dict) -> NewOrderDTO:
    # minimal validation (do more as needed)
    if not isinstance(json_.get("custId"), int): raise ValueError("custId must be int")
    items = json_.get("items") or []
    if not items: raise ValueError("items required")
    dto_items = []
    for it in items:
        if not isinstance(it.get("sku"), str): raise ValueError("sku required")
        if not isinstance(it.get("qty"), int) or it["qty"] <= 0:
            raise ValueError("qty must be positive int")
        dto_items.append(NewOrderItemDTO(it["sku"], it["qty"]))
    return NewOrderDTO(json_["custId"], dto_items)

# api/controller.py
from api.dtos import parse_new_order
from domain.usecase import create_order

def create_order_http(request_json):
    dto = parse_new_order(request_json)     # translate & validate at the edge
    order_id = create_order(dto)            # domain sees a clean DTO
    return {"orderId": order_id}, 201

# domain/usecase.py
def create_order(dto) -> int:
    # pure business logic; no HTTP assumptions
    total_qty = sum(i.qty for i in dto.items)
    if total_qty > 100: raise ValueError("bulk limit exceeded")
    # persist via port, publish event via port, etc.
    return 1234
