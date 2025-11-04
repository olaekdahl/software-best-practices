# Observer / Strategy demo
# Talking points:
# - Subject notifies decoupled subscribers (Observer).
# - Swap algorithms at runtime via strategies (Strategy).
# - Consider error isolation and unsubscribe hygiene.
#
# Intent
# - Observer: let multiple subscribers react to events from a subject, decoupled.
# - Strategy: make an algorithm interchangeable at runtime via a common interface.
#
# When to use
# - Observer: broadcast state changes without hard-coding listeners; enable plug-ins.
# - Strategy: replace if/elif chains with composable behaviors selected by context.
#
# Trade-offs
# - Observer here is synchronous/in-process; for scale consider queues or signals.
# - Be mindful of memory leaks by unsubscribing; guard exceptions so one observer
#   doesn't break the rest.
# - Strategy proliferation: keep a registry/factory to manage choices.
from __future__ import annotations
from typing import Protocol, List, Callable

# --- Observer ---
class Observer(Protocol):
    def update(self, message: str) -> None: ...


class Subject:
    def __init__(self) -> None:
        self._observers: List[Observer] = []

    def subscribe(self, obs: Observer) -> None:
        self._observers.append(obs)

    def unsubscribe(self, obs: Observer) -> None:
        self._observers.remove(obs)

    def notify(self, message: str) -> None:
        # Copy to avoid mutation during iteration (unsubscribe while notifying)
        for o in self._observers.copy():
            # In production, wrap in try/except to isolate observer failures
            o.update(message)


class PrintObserver:
    def __init__(self, name: str) -> None:
        self.name = name

    def update(self, message: str) -> None:
        print(f"[{self.name}] {message}")


# --- Strategy ---
class DiscountStrategy(Protocol):
    def apply(self, total: float) -> float: ...


class NoDiscount:
    def apply(self, total: float) -> float:
        return total


class TenPercent:
    def apply(self, total: float) -> float:
        return round(total * 0.9, 2)


class Context:
    def __init__(self, strategy: DiscountStrategy) -> None:
        self.strategy = strategy

    def price(self, total: float) -> float:
        # Delegate algorithm choice to the injected strategy
        return self.strategy.apply(total)


if __name__ == "__main__":
    # Observer
    subject = Subject()
    subject.subscribe(PrintObserver("A"))
    subject.subscribe(PrintObserver("B"))
    subject.notify("Event happened")

    # Strategy
    ctx = Context(TenPercent())  # swap strategies without changing the Context
    print("Strategy price:", ctx.price(100.0))
