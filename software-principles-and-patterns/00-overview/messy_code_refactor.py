# Refactored: SRP + DIP + remove duplication
# Talking points:
# - Separate classes own validation, pricing, orchestration (SRP).
# - Ports (Protocols) decouple side effects so you can inject fakes (DIP).
# - One Pricer eliminates rule duplication (DRY).
# - Easier to test: replace Payment/Email with test doubles.
#
# Improvements to call out:
# - SRP: Validation, pricing, payment, and email are separate components.
# - DIP: Side-effects are abstracted via Protocols (ports), so the orchestrator
#   depends on abstractions. You can inject different adapters in tests/prod.
# - DRY: A single Pricer owns the price calculation. If the rule changes, you
#   change it in one place.
from dataclasses import dataclass
from typing import List, Protocol
import re


@dataclass
class LineItem:
    sku: str
    price: float
    qty: int


@dataclass
class Order:
    email: str
    card_last4: str
    items: List[LineItem]


class EmailValidator:
    _re = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

    def validate(self, email: str) -> None:
        # Single responsibility: validation only
        if not email:
            raise ValueError("email required")
        if not self._re.match(email):
            raise ValueError("invalid email")


class Pricer:
    def total(self, items: List[LineItem], tax_rate: float = 0.07) -> float:
        # Centralize pricing so it isn't duplicated
        subtotal = sum(i.price * i.qty for i in items)
        return round(subtotal * (1 + tax_rate), 2)


class PaymentPort(Protocol):
    def charge(self, card_last4: str, amount: float) -> None: ...


class EmailPort(Protocol):
    def send(self, to: str, body: str) -> None: ...


class ConsolePayment:
    def charge(self, card_last4: str, amount: float) -> None:
        # Concrete adapter for demo/testing; swap with real gateway in prod
        print(f"[PAYMENT] Charging card {card_last4} amount ${amount:.2f}")


class ConsoleEmail:
    def send(self, to: str, body: str) -> None:
        # Concrete adapter for demo/testing; swap with real SMTP/ESP in prod
        print(f"[EMAIL] To: {to} — {body}")


class OrderProcessor:
    def __init__(self, validator: EmailValidator, pricer: Pricer, pay: PaymentPort, mail: EmailPort):
        self.validator = validator
        self.pricer = pricer
        self.pay = pay
        self.mail = mail

    def process(self, order: Order) -> None:
        # Orchestration only; no business rules embedded here
        self.validator.validate(order.email)
        total = self.pricer.total(order.items)
        self.pay.charge(order.card_last4, total)
        self.mail.send(order.email, f"Thanks! We charged ${total:.2f}")


if __name__ == "__main__":
    order = Order(
        email="user@example.com",
        card_last4="1111",
        items=[LineItem("A", 10.0, 2), LineItem("B", 5.0, 3)],
    )
    processor = OrderProcessor(EmailValidator(), Pricer(), ConsolePayment(), ConsoleEmail())
    processor.process(order)
