from __future__ import annotations

import time

class FakeDB:
    def get_user(self, user_id: int) -> dict:
        time.sleep(0.2)  # slow read
        return {"id": user_id, "name": f"user-{user_id}", "tier": "premium" if user_id % 2 else "free"}

class CacheAside:
    def __init__(self, db: FakeDB) -> None:
        self._db = db
        self._cache: dict[int, dict] = {}

    def get_user(self, user_id: int) -> dict:
        if user_id in self._cache:
            return self._cache[user_id]
        row = self._db.get_user(user_id)
        self._cache[user_id] = row
        return row

def timed(label: str, fn):
    t0 = time.perf_counter()
    out = fn()
    dt = (time.perf_counter() - t0) * 1000
    print(f"{label}: {dt:.1f}ms -> {out}")

def main() -> None:
    db = FakeDB()
    svc = CacheAside(db)

    timed("First read (miss)", lambda: svc.get_user(7))
    timed("Second read (hit)", lambda: svc.get_user(7))

if __name__ == "__main__":
    main()
