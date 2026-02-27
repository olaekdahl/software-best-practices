from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Callable, DefaultDict

@dataclass(frozen=True)
class Message:
    topic: str
    body: dict

class Broker:
    def __init__(self) -> None:
        self._subs: DefaultDict[str, list[Callable[[Message], None]]] = defaultdict(list)

    def subscribe(self, topic: str, handler: Callable[[Message], None]) -> None:
        self._subs[topic].append(handler)

    def publish(self, msg: Message) -> None:
        for h in list(self._subs.get(msg.topic, [])):
            h(msg)

def main() -> None:
    b = Broker()

    b.subscribe("orders", lambda m: print("billing got:", m.body))
    b.subscribe("orders", lambda m: print("analytics got:", m.body))
    b.subscribe("users", lambda m: print("crm got:", m.body))

    b.publish(Message("orders", {"order_id": "O-1"}))
    b.publish(Message("users", {"user_id": "U-9"}))

if __name__ == "__main__":
    main()
