from __future__ import annotations

import random
import time

# 'Distributed' store: many partitions
PARTITIONS: list[dict[str, dict]] = [{ } for _ in range(20)]
INDEX: dict[str, int] = {}  # user_id -> partition index

def put(user_id: str, doc: dict) -> None:
    p = random.randrange(len(PARTITIONS))
    PARTITIONS[p][user_id] = doc
    INDEX[user_id] = p

def get_slow(user_id: str) -> dict | None:
    # Full scan across partitions (slow)
    for part in PARTITIONS:
        if user_id in part:
            return part[user_id]
    return None

def get_fast(user_id: str) -> dict | None:
    p = INDEX.get(user_id)
    if p is None:
        return None
    return PARTITIONS[p].get(user_id)

def main() -> None:
    for i in range(5000):
        put(f"u{i}", {"id": f"u{i}", "v": i})

    target = "u4321"

    t0 = time.perf_counter()
    a = get_slow(target)
    t1 = (time.perf_counter() - t0) * 1000

    t0 = time.perf_counter()
    b = get_fast(target)
    t2 = (time.perf_counter() - t0) * 1000

    print("Slow scan:", f"{t1:.3f}ms", "found:", a["id"])
    print("Index lookup:", f"{t2:.3f}ms", "found:", b["id"])
    print("Index table avoids full scans.")

if __name__ == "__main__":
    main()
