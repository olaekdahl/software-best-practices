from __future__ import annotations

import time

def user_service(user_id: int) -> dict:
    time.sleep(0.05)
    return {"id": user_id, "name": f"user-{user_id}"}

def orders_service(user_id: int) -> list[dict]:
    time.sleep(0.05)
    return [{"order_id": f"O{user_id}-{i}", "total": 10.0 + i} for i in range(3)]

def gateway_profile(user_id: int) -> dict:
    # One call from client -> gateway fans out and aggregates.
    user = user_service(user_id)
    orders = orders_service(user_id)
    return {"user": user, "recent_orders": orders}

def main() -> None:
    t0 = time.perf_counter()
    profile = gateway_profile(7)
    dt = (time.perf_counter() - t0) * 1000
    print(f"Aggregated response in {dt:.1f}ms:", profile)

if __name__ == "__main__":
    main()
