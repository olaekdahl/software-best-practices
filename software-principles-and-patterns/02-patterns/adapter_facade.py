# Adapter / Facade demo
# Talking points:
# - Adapter shields your app from legacy API signatures and changes.
# - Facade provides a single, simple entry point over multiple subsystems.
# - Keep adapters thin; don’t let the facade become a god-object.
#
# Intent
# - Adapter: wrap an incompatible API to match your application's expected interface.
# - Facade: provide a simple entry point over a set of subsystems to reduce coupling.
#
# When to use
# - Adapter: third-party or legacy API signatures don't match your ports; you want
#   to isolate vendor churn and keep the rest of your code stable.
# - Facade: client code shouldn't orchestrate multiple subsystems; expose one
#   cohesive method that coordinates them.
#
# Trade-offs
# - Keep adapters thin; avoid leaking third-party types outside.
# - Facade shouldn't become a god-object; it just sequences collaborators.
# - For resilience, consider retries/transactions around the façade orchestration.
from dataclasses import dataclass
from typing import Protocol


# --- Adapter ---
class EmailClient(Protocol):
    def send(self, to: str, subject: str, body: str) -> None: ...


class LegacyEmailService:
    # third-party we don't control
    def send_mail(self, recipient: str, message: str) -> None:
        print(f"[LEGACY] to={recipient} msg={message}")


class LegacyEmailAdapter:
    def __init__(self, legacy: LegacyEmailService) -> None:
        self.legacy = legacy

    def send(self, to: str, subject: str, body: str) -> None:
        # Map your app's interface to the legacy call shape/semantics
        self.legacy.send_mail(to, f"{subject}: {body}")


# --- Facade ---
@dataclass
class Order:
    id: str
    amount: float


class Inventory:
    def reserve(self, order_id: str) -> None:
        print(f"[Inventory] reserved for {order_id}")


class Billing:
    def charge(self, amount: float) -> None:
        print(f"[Billing] charged ${amount:.2f}")


class Shipping:
    def ship(self, order_id: str) -> None:
        print(f"[Shipping] shipped {order_id}")


class OrderFacade:
    def __init__(self, inv: Inventory, bill: Billing, ship: Shipping, mail: EmailClient) -> None:
        self.inv, self.bill, self.ship, self.mail = inv, bill, ship, mail

    def place(self, order: Order) -> None:
        # Simple orchestration; errors/compensation can be added as needed
        self.inv.reserve(order.id)
        self.bill.charge(order.amount)
        self.ship.ship(order.id)
        self.mail.send("user@example.com", "Order placed", f"Order {order.id} confirmed")


if __name__ == "__main__":
    adapter = LegacyEmailAdapter(LegacyEmailService())
    facade = OrderFacade(Inventory(), Billing(), Shipping(), adapter)
    facade.place(Order(id="O-1", amount=42.50))
