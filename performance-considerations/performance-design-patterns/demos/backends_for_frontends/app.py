from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class Product:
    id: int
    name: str
    description: str
    price: float
    inventory: int

# Shared domain store
DB = {
    1: Product(1, "Trail Shoes", "Durable shoes for long runs.", 129.99, 42),
    2: Product(2, "Water Bottle", "Insulated 24oz bottle.", 24.99, 300),
}

class WebBFF:
    """Optimized for web: richer fields, fewer round-trips."""
    def get_product_card(self, product_id: int) -> dict:
        p = DB[product_id]
        return {"id": p.id, "name": p.name, "price": p.price, "description": p.description}

class MobileBFF:
    """Optimized for mobile: smaller payload, faster render."""
    def get_product_card(self, product_id: int) -> dict:
        p = DB[product_id]
        return {"id": p.id, "name": p.name, "price": p.price}

def main() -> None:
    web = WebBFF()
    mobile = MobileBFF()

    print("Web response (richer payload):", web.get_product_card(1))
    print("Mobile response (lean payload):", mobile.get_product_card(1))
    print("Same domain model, different client-optimized backends.")

if __name__ == "__main__":
    main()
