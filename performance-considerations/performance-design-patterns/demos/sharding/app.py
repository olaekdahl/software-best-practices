from __future__ import annotations

import hashlib

SHARDS = [dict() for _ in range(4)]

def shard_for(key: str) -> int:
    h = hashlib.sha256(key.encode()).digest()
    return h[0] % len(SHARDS)

def put(key: str, value: str) -> None:
    s = shard_for(key)
    SHARDS[s][key] = value

def get(key: str) -> str | None:
    s = shard_for(key)
    return SHARDS[s].get(key)

def main() -> None:
    for k in ["alice", "bob", "carol", "dave", "erin"]:
        put(k, f"profile:{k}")

    for k in ["alice", "erin"]:
        s = shard_for(k)
        print(f"{k} routed to shard {s} -> {get(k)}")

    print("Sharding spreads load; each shard handles only its partition of keys.")

if __name__ == "__main__":
    main()
