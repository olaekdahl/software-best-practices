from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class Event:
    type: str
    data: dict

EVENT_LOG: list[Event] = []

def append(evt: Event) -> None:
    EVENT_LOG.append(evt)

def rebuild_state() -> dict:
    balance = 0
    for evt in EVENT_LOG:
        if evt.type == "deposit":
            balance += evt.data["amount"]
        elif evt.type == "withdraw":
            balance -= evt.data["amount"]
    return {"balance": balance, "events": len(EVENT_LOG)}

def main() -> None:
    append(Event("deposit", {"amount": 50}))
    append(Event("withdraw", {"amount": 12}))
    append(Event("deposit", {"amount": 7}))

    print("Event log:", EVENT_LOG)
    print("Rebuilt state:", rebuild_state())

if __name__ == "__main__":
    main()
