from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, DefaultDict
from collections import defaultdict

@dataclass(frozen=True)
class Event:
    type: str
    data: dict

class EventBus:
    def __init__(self) -> None:
        self._subs: DefaultDict[str, list[Callable[[Event], None]]] = defaultdict(list)

    def subscribe(self, event_type: str, handler: Callable[[Event], None]) -> None:
        self._subs[event_type].append(handler)

    def publish(self, event: Event) -> None:
        for h in list(self._subs.get(event.type, [])):
            h(event)

def main() -> None:
    bus = EventBus()

    def payment(evt: Event) -> None:
        print("Payment: charging card...")
        bus.publish(Event("payment.succeeded", {"order_id": evt.data["order_id"]}))

    def shipping(evt: Event) -> None:
        print("Shipping: creating shipment label...")
        bus.publish(Event("shipment.created", {"order_id": evt.data["order_id"]}))

    def email(evt: Event) -> None:
        print("Email: notifying customer...", evt.type, evt.data)

    bus.subscribe("order.placed", payment)
    bus.subscribe("payment.succeeded", shipping)
    bus.subscribe("payment.succeeded", email)
    bus.subscribe("shipment.created", email)

    print("No central orchestrator. Services react to events.")
    bus.publish(Event("order.placed", {"order_id": "A123"}))

if __name__ == "__main__":
    main()
