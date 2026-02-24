"""
Demo 01 - Naive Performance (Anti-patterns)
==============================================
Code with obvious performance problems.

Instructor talking points:
- N+1 query pattern
- Unnecessary recomputation
- Blocking I/O in a loop
- No pagination for large datasets
- String concatenation in loops

Run: python main.py
"""

from __future__ import annotations

import time
from dataclasses import dataclass


# ============================================================================
# Simulated "database" with artificial delays
# ============================================================================

USERS_DB = {i: {"id": i, "name": f"User_{i}", "dept": f"dept_{i % 5}"} for i in range(100)}
ORDERS_DB = {
    i: {"id": i, "user_id": i % 100, "amount": 10.0 + (i * 0.5), "status": "completed"}
    for i in range(500)
}


def simulate_db_query(table: str, query_ms: float = 5.0) -> None:
    """Simulate database query latency."""
    time.sleep(query_ms / 1000)


# ============================================================================
# Anti-pattern 1: N+1 queries
# ============================================================================

def get_users_with_orders_n_plus_1() -> list[dict]:
    """Fetch users then fetch orders one-by-one.

    This makes 1 query for users + N queries for orders = N+1 queries.
    """
    # Query 1: Get all users
    simulate_db_query("users")
    users = list(USERS_DB.values())[:20]

    results = []
    for user in users:
        # Query N: Get orders for EACH user separately
        simulate_db_query("orders")
        user_orders = [
            o for o in ORDERS_DB.values() if o["user_id"] == user["id"]
        ]
        results.append({
            "user": user["name"],
            "order_count": len(user_orders),
            "total": sum(o["amount"] for o in user_orders),
        })

    return results


# ============================================================================
# Anti-pattern 2: Recomputation in loops
# ============================================================================

def compute_statistics_naive(data: list[float]) -> dict:
    """Recomputes values redundantly inside loops."""
    result = {}

    # BAD: Sorting the entire list multiple times
    result["min"] = sorted(data)[0]
    result["max"] = sorted(data)[-1]  # Sorting again!
    result["median"] = sorted(data)[len(data) // 2]  # And again!

    # BAD: Recomputing sum and len repeatedly
    result["mean"] = sum(data) / len(data)
    result["variance"] = sum((x - sum(data) / len(data)) ** 2 for x in data) / len(data)

    return result


# ============================================================================
# Anti-pattern 3: String concatenation in loops
# ============================================================================

def build_report_naive(n: int) -> str:
    """Build a large string via concatenation (O(n^2) behavior)."""
    report = ""
    for i in range(n):
        # BAD: String concatenation creates a new string each iteration
        report = report + f"Line {i}: This is report entry number {i}\n"
    return report


# ============================================================================
# Anti-pattern 4: No pagination
# ============================================================================

def get_all_records_naive() -> list[dict]:
    """Load everything into memory at once."""
    simulate_db_query("records", query_ms=50)
    # BAD: Loading all records without pagination
    return [
        {"id": i, "data": "x" * 1000}  # Large records
        for i in range(10_000)
    ]


# ============================================================================
# Anti-pattern 5: Blocking I/O in sequence
# ============================================================================

def fetch_multiple_apis_sequential() -> list[str]:
    """Call multiple APIs one after another (sequential blocking)."""
    results = []
    urls = [f"api_{i}" for i in range(5)]
    for url in urls:
        # BAD: Each call blocks until complete
        time.sleep(0.1)  # Simulate 100ms per API call
        results.append(f"Response from {url}")
    return results


# ============================================================================
# Main demo with timing
# ============================================================================

def timed(label: str, func, *args):
    """Run a function and print elapsed time."""
    start = time.perf_counter()
    result = func(*args)
    elapsed = time.perf_counter() - start
    print(f"  {label}: {elapsed:.3f}s")
    return result


def main():
    print("=== Demo: Naive Performance (Anti-patterns) ===\n")

    # N+1 queries
    print("--- Anti-pattern 1: N+1 Queries ---")
    result = timed("20 users with orders (N+1)", get_users_with_orders_n_plus_1)
    print(f"  Made ~21 queries for {len(result)} users")
    print()

    # Recomputation
    print("--- Anti-pattern 2: Redundant Recomputation ---")
    data = list(range(100_000))
    timed("Statistics with recomputation", compute_statistics_naive, [float(x) for x in data])
    print()

    # String concatenation
    print("--- Anti-pattern 3: String Concatenation O(n^2) ---")
    timed("Build report (10K lines, concat)", build_report_naive, 10_000)
    print()

    # No pagination
    print("--- Anti-pattern 4: No Pagination ---")
    result = timed("Load all 10K records at once", get_all_records_naive)
    print(f"  Memory: ~{len(result) * 1000 / 1024:.0f} KB of data loaded")
    print()

    # Sequential I/O
    print("--- Anti-pattern 5: Sequential API Calls ---")
    result = timed("5 sequential API calls", fetch_multiple_apis_sequential)
    print(f"  Total time ~0.5s for 5 x 100ms calls")

    print("\n--- Performance Problems ---")
    print("1. N+1: 21 queries instead of 2 (JOIN or batch)")
    print("2. Recomputation: sorted() called 3x on same data")
    print("3. String concat: O(n^2) instead of O(n) with join()")
    print("4. No pagination: loads all records into memory")
    print("5. Sequential I/O: 0.5s instead of 0.1s with concurrency")


if __name__ == "__main__":
    main()
