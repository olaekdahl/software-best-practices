from __future__ import annotations

from collections import defaultdict

# Base table
ORDERS: list[dict] = [
    {"user": "alice", "total": 10},
    {"user": "bob", "total": 7},
    {"user": "alice", "total": 3},
]

# Materialized view: totals per user
TOTALS: dict[str, int] = defaultdict(int)

def rebuild_view() -> None:
    TOTALS.clear()
    for o in ORDERS:
        TOTALS[o["user"]] += o["total"]

def insert_order(user: str, total: int) -> None:
    ORDERS.append({"user": user, "total": total})
    # Incremental view maintenance (fast)
    TOTALS[user] += total

def query_total(user: str) -> int:
    return TOTALS[user]

def main() -> None:
    rebuild_view()
    print("Initial totals:", dict(TOTALS))

    insert_order("alice", 5)
    print("After insert, view updated:", dict(TOTALS))
    print("Query is O(1): alice total =", query_total("alice"))

if __name__ == "__main__":
    main()
