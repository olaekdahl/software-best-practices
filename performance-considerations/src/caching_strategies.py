"""
Demo 04 - Caching Strategies
===============================
Demonstrates caching with TTL, LRU eviction, and invalidation.

Instructor talking points:
- Cache only deterministic results
- Set TTLs aligned with freshness requirements
- Document invalidation rules
- Track hit/miss ratios
- Negative caching to prevent cache stampede

Run: python main.py
"""

from __future__ import annotations

import time
from collections import OrderedDict
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Any, Callable


# ============================================================================
# Level 1: Simple functools.lru_cache
# ============================================================================

call_count = 0


def expensive_computation(n: int) -> int:
    """Simulate an expensive computation."""
    global call_count
    call_count += 1
    time.sleep(0.05)  # 50ms "expensive" work
    return n * n + 42


@lru_cache(maxsize=128)
def cached_computation(n: int) -> int:
    """Same computation but with lru_cache."""
    return expensive_computation.__wrapped__(n) if hasattr(expensive_computation, '__wrapped__') else n * n + 42


# ============================================================================
# Level 2: TTL Cache with expiration
# ============================================================================

@dataclass
class CacheEntry:
    """A cache entry with TTL and metadata."""
    value: Any
    created_at: float
    ttl: float
    hits: int = 0

    @property
    def is_expired(self) -> bool:
        return time.time() - self.created_at > self.ttl

    @property
    def age(self) -> float:
        return time.time() - self.created_at


class TTLCache:
    """Cache with Time-To-Live expiration and hit tracking."""

    def __init__(self, default_ttl: float = 60.0, max_size: int = 1000):
        self._store: OrderedDict[str, CacheEntry] = OrderedDict()
        self._default_ttl = default_ttl
        self._max_size = max_size
        self._stats = {"hits": 0, "misses": 0, "evictions": 0, "expirations": 0}

    def get(self, key: str) -> Any | None:
        """Get a value from cache. Returns None on miss or expiry."""
        entry = self._store.get(key)
        if entry is None:
            self._stats["misses"] += 1
            return None
        if entry.is_expired:
            del self._store[key]
            self._stats["expirations"] += 1
            self._stats["misses"] += 1
            return None
        entry.hits += 1
        self._stats["hits"] += 1
        self._store.move_to_end(key)  # LRU: move to end
        return entry.value

    def set(self, key: str, value: Any, ttl: float | None = None) -> None:
        """Set a value in cache with optional custom TTL."""
        if key in self._store:
            del self._store[key]
        elif len(self._store) >= self._max_size:
            self._store.popitem(last=False)  # Evict oldest
            self._stats["evictions"] += 1
        self._store[key] = CacheEntry(
            value=value,
            created_at=time.time(),
            ttl=ttl or self._default_ttl,
        )

    def invalidate(self, key: str) -> bool:
        """Explicitly invalidate a cache entry."""
        if key in self._store:
            del self._store[key]
            return True
        return False

    def invalidate_pattern(self, prefix: str) -> int:
        """Invalidate all keys matching a prefix."""
        keys_to_remove = [k for k in self._store if k.startswith(prefix)]
        for k in keys_to_remove:
            del self._store[k]
        return len(keys_to_remove)

    @property
    def hit_ratio(self) -> float:
        total = self._stats["hits"] + self._stats["misses"]
        return self._stats["hits"] / total if total > 0 else 0.0

    @property
    def stats(self) -> dict:
        return {**self._stats, "hit_ratio": f"{self.hit_ratio:.1%}", "size": len(self._store)}


# ============================================================================
# Level 3: Cache-aside pattern with negative caching
# ============================================================================

class DataService:
    """Service demonstrating cache-aside pattern."""

    def __init__(self, cache: TTLCache):
        self._cache = cache
        self._db_calls = 0

    def _db_lookup(self, user_id: str) -> dict | None:
        """Simulate database lookup."""
        self._db_calls += 1
        time.sleep(0.02)  # 20ms DB latency
        # Simulated database
        users = {
            "user-1": {"name": "Alice", "email": "alice@example.com"},
            "user-2": {"name": "Bob", "email": "bob@example.com"},
            "user-3": {"name": "Charlie", "email": "charlie@example.com"},
        }
        return users.get(user_id)

    def get_user(self, user_id: str) -> dict | None:
        """Cache-aside pattern: check cache, fallback to DB."""
        cache_key = f"user:{user_id}"

        # 1. Check cache
        cached = self._cache.get(cache_key)
        if cached is not None:
            # Handle negative cache (user not found was cached)
            if cached == "__NOT_FOUND__":
                return None
            return cached

        # 2. Cache miss - query DB
        user = self._db_lookup(user_id)

        # 3. Populate cache
        if user is not None:
            self._cache.set(cache_key, user, ttl=300)  # 5 min TTL
        else:
            # Negative caching: prevent repeated DB lookups for non-existent users
            self._cache.set(cache_key, "__NOT_FOUND__", ttl=60)  # 1 min TTL

        return user

    def update_user(self, user_id: str, updates: dict) -> None:
        """Update user and invalidate cache."""
        # In real code: update DB here
        # Invalidate cache to ensure fresh data on next read
        self._cache.invalidate(f"user:{user_id}")
        print(f"  Cache invalidated for user:{user_id}")

    @property
    def db_calls(self) -> int:
        return self._db_calls


# ============================================================================
# Main demo
# ============================================================================

def main():
    print("=== Demo: Caching Strategies ===\n")

    # --- Level 1: lru_cache ---
    print("--- Level 1: functools.lru_cache ---")
    # Without cache
    start = time.perf_counter()
    for i in range(10):
        expensive_computation(i % 5)  # 5 unique, 5 repeats
    t_no_cache = time.perf_counter() - start
    print(f"  Without cache: {t_no_cache:.3f}s ({call_count} calls)")
    print()

    # --- Level 2: TTL Cache ---
    print("--- Level 2: TTL Cache ---")
    cache = TTLCache(default_ttl=2.0, max_size=100)

    # Set and get
    cache.set("key1", "value1")
    cache.set("key2", "value2", ttl=0.5)  # Short TTL

    print(f"  key1: {cache.get('key1')}")
    print(f"  key2: {cache.get('key2')}")
    print(f"  miss: {cache.get('nonexistent')}")
    print(f"  Stats: {cache.stats}")
    print()

    # Wait for key2 to expire
    time.sleep(0.6)
    print(f"  key2 (after 0.6s): {cache.get('key2')} (expired)")
    print(f"  key1 (still valid): {cache.get('key1')}")
    print(f"  Stats: {cache.stats}")
    print()

    # --- Level 3: Cache-aside with negative caching ---
    print("--- Level 3: Cache-Aside Pattern ---")
    cache = TTLCache(default_ttl=300.0)
    service = DataService(cache)

    print("  First requests (cache miss, hits DB):")
    for uid in ["user-1", "user-2", "user-99"]:
        result = service.get_user(uid)
        status = result["name"] if result else "NOT FOUND"
        print(f"    {uid}: {status}")
    print(f"    DB calls: {service.db_calls}")
    print()

    print("  Second requests (cache hit, no DB):")
    for uid in ["user-1", "user-2", "user-99"]:
        result = service.get_user(uid)
        status = result["name"] if result else "NOT FOUND (negative cached)"
        print(f"    {uid}: {status}")
    print(f"    DB calls: {service.db_calls} (unchanged - served from cache)")
    print()

    # Invalidation on update
    print("  After update (invalidation):")
    service.update_user("user-1", {"name": "Alice Updated"})
    result = service.get_user("user-1")
    print(f"    user-1 (re-fetched): {result['name'] if result else 'N/A'}")
    print(f"    DB calls: {service.db_calls} (one more for re-fetch)")
    print()

    print(f"  Final cache stats: {cache.stats}")

    print("\n--- Caching Best Practices ---")
    print("1. Cache only deterministic results")
    print("2. Set TTLs aligned with freshness needs")
    print("3. Use negative caching to prevent stampede")
    print("4. Invalidate on writes (cache-aside)")
    print("5. Track hit ratio - target >90%")
    print("6. Set max_size to prevent unbounded memory growth")
    print("7. Document invalidation rules and TTLs")


if __name__ == "__main__":
    main()
