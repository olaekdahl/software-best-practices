"""
Demo 01 - Buggy App (Find the Bugs)
======================================
An application with several intentional bugs for live debugging.

Instructor talking points:
- Read the error messages carefully
- Reproduce the bug first
- Narrow the scope before fixing
- Each bug represents a common category

Run: python main.py
  (will fail in several places - that's the point!)
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field


# ============================================================================
# Bug 1: Off-by-one / boundary error
# ============================================================================

def paginate(items: list, page: int, page_size: int = 10) -> list:
    """Return a page of items.

    BUG: Off-by-one error causes missing first item and potential IndexError.
    """
    # BUG: start should be (page - 1) * page_size, not page * page_size
    start = page * page_size
    end = start + page_size
    return items[start:end]


# ============================================================================
# Bug 2: Mutable default argument
# ============================================================================

@dataclass
class ShoppingCart:
    """Shopping cart with items.

    BUG: Mutable default argument is shared across instances.
    """
    owner: str
    items: list = field(default_factory=list)  # Fixed version
    # items: list = []  # This would be the bug - uncomment to show


class BuggyShoppingCart:
    """Shopping cart that demonstrates the mutable default bug."""

    def __init__(self, owner: str, items: list = []):  # noqa: B006
        # BUG: Default list is shared across ALL instances
        self.owner = owner
        self.items = items

    def add(self, item: str) -> None:
        self.items.append(item)

    def __repr__(self) -> str:
        return f"Cart({self.owner}: {self.items})"


# ============================================================================
# Bug 3: Silent failure / swallowed exception
# ============================================================================

def load_config(path: str) -> dict:
    """Load configuration from a JSON file.

    BUG: Exception is silently swallowed, returns empty dict
    with no indication of failure.
    """
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        # BUG: Silent failure - no logging, returns empty dict
        # Consumers have no idea the config didn't load
        return {}


def load_config_fixed(path: str) -> dict:
    """Fixed version: fails explicitly or logs a warning."""
    try:
        with open(path) as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Config file not found: {path}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {path}: {e}")


# ============================================================================
# Bug 4: Race condition / state inconsistency
# ============================================================================

class BankAccount:
    """Bank account with deposit/withdraw.

    BUG: check-then-act race condition.
    Non-atomic read-compare-write in withdraw().
    """

    def __init__(self, balance: float):
        self.balance = balance
        self._transactions: list[str] = []

    def withdraw(self, amount: float) -> bool:
        """Withdraw amount if sufficient balance.

        BUG: Time gap between check and update.
        In concurrent scenarios, two threads could both
        pass the check before either updates the balance.
        """
        if self.balance >= amount:
            # BUG: Simulated delay between check and update
            # In real code, this gap exists without the sleep
            time.sleep(0.001)
            self.balance -= amount
            self._transactions.append(f"withdraw:{amount}")
            return True
        return False

    def deposit(self, amount: float) -> None:
        self.balance += amount
        self._transactions.append(f"deposit:{amount}")


# ============================================================================
# Bug 5: Resource leak
# ============================================================================

class ConnectionPool:
    """Simulated connection pool.

    BUG: Connections acquired but not released on error.
    """

    def __init__(self, max_connections: int = 5):
        self.max_connections = max_connections
        self.active = 0
        self.total_acquired = 0

    def acquire(self) -> int:
        if self.active >= self.max_connections:
            raise RuntimeError(f"Pool exhausted: {self.active}/{self.max_connections}")
        self.active += 1
        self.total_acquired += 1
        return self.total_acquired  # connection ID

    def release(self) -> None:
        self.active = max(0, self.active - 1)


def process_request_buggy(pool: ConnectionPool, data: str) -> str:
    """Process a request using a connection.

    BUG: Connection not released if processing raises an error.
    """
    conn_id = pool.acquire()
    # BUG: If this raises, connection is never released
    if "bad" in data:
        raise ValueError(f"Bad data: {data}")
    result = f"processed:{data}:conn{conn_id}"
    pool.release()
    return result


def process_request_fixed(pool: ConnectionPool, data: str) -> str:
    """Fixed: Connection always released via try/finally."""
    conn_id = pool.acquire()
    try:
        if "bad" in data:
            raise ValueError(f"Bad data: {data}")
        return f"processed:{data}:conn{conn_id}"
    finally:
        pool.release()


# ============================================================================
# Main demo
# ============================================================================

def main():
    print("=== Demo: Buggy App (Find the Bugs) ===\n")

    # --- Bug 1: Off-by-one ---
    print("--- Bug 1: Off-by-one in Pagination ---")
    items = list(range(1, 26))  # Items 1-25
    page1 = paginate(items, page=1, page_size=10)
    print(f"  Page 1 (should start with 1): {page1[:5]}...")
    print(f"  BUG: First {paginate(items, page=0, page_size=10)[0]} items are on page 0")
    print(f"  FIX: Use (page - 1) * page_size")
    print()

    # --- Bug 2: Mutable default ---
    print("--- Bug 2: Mutable Default Argument ---")
    cart_a = BuggyShoppingCart("Alice")
    cart_a.add("apple")
    cart_b = BuggyShoppingCart("Bob")
    cart_b.add("banana")
    print(f"  Alice's cart: {cart_a}")
    print(f"  Bob's cart:   {cart_b}")
    print(f"  BUG: Bob's cart contains Alice's items!")
    print(f"  FIX: Use None as default, create list in __init__")
    print()

    # --- Bug 3: Silent failure ---
    print("--- Bug 3: Silent Failure ---")
    config = load_config("/nonexistent/config.json")
    print(f"  Config loaded: {config}")
    print(f"  BUG: Empty dict returned, no error raised!")
    print(f"  FIX: Raise specific exceptions or log warnings")
    try:
        load_config_fixed("/nonexistent/config.json")
    except FileNotFoundError as e:
        print(f"  Fixed version raises: {e}")
    print()

    # --- Bug 4: Race condition ---
    print("--- Bug 4: Race Condition (check-then-act) ---")
    account = BankAccount(100.0)
    print(f"  Starting balance: ${account.balance:.2f}")

    import threading
    results = []

    def attempt_withdraw():
        success = account.withdraw(80.0)
        results.append(success)

    t1 = threading.Thread(target=attempt_withdraw)
    t2 = threading.Thread(target=attempt_withdraw)
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    print(f"  Both withdrawals succeeded: {results}")
    print(f"  Final balance: ${account.balance:.2f}")
    if account.balance < 0:
        print(f"  BUG: Negative balance! Both threads passed the check.")
    print(f"  FIX: Use threading.Lock or atomic operations")
    print()

    # --- Bug 5: Resource leak ---
    print("--- Bug 5: Resource Leak ---")
    pool = ConnectionPool(max_connections=3)
    for i in range(5):
        data = "good" if i % 2 == 0 else "bad-data"
        try:
            process_request_buggy(pool, data)
        except ValueError:
            pass  # Error handled but connection not released
    print(f"  Active connections: {pool.active}/{pool.max_connections}")
    print(f"  BUG: {pool.active} connections leaked due to unhandled release")
    print(f"  FIX: Use try/finally or context manager")

    # Show fixed version
    pool2 = ConnectionPool(max_connections=3)
    for i in range(5):
        data = "good" if i % 2 == 0 else "bad-data"
        try:
            process_request_fixed(pool2, data)
        except ValueError:
            pass
    print(f"  Fixed version - active: {pool2.active}/{pool2.max_connections}")


if __name__ == "__main__":
    main()
