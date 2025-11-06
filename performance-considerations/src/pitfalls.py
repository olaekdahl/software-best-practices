from __future__ import annotations

import io
import os
import time


def excessive_io(path: str):
    # Simulate reading file line by line vs buffered read
    with open(path, "w", encoding="utf-8") as f:
        for i in range(50_000):
            f.write(f"line {i}\n")
    t0 = time.perf_counter()
    with open(path, "r", encoding="utf-8") as f:
        for _ in f:  # line by line (OK, but high Python overhead)
            pass
    t1 = time.perf_counter()
    with open(path, "r", encoding="utf-8") as f:
        data = f.read()  # single read
    t2 = time.perf_counter()
    print(f"Excessive I/O: iterative={t1-t0:.4f}s, single read={t2-t1:.4f}s, size={len(data)}")
    os.remove(path)


_LEAK_CONTAINER: list[bytes] = []


def memory_growth(leak_iters: int = 5_000):
    # Demonstrate a 'leak' pattern (holding references)
    for _ in range(leak_iters):
        _LEAK_CONTAINER.append(b"x" * 1024)  # 1KB each
    print(f"Memory growth pattern: stored {len(_LEAK_CONTAINER)} KB ~ {len(_LEAK_CONTAINER)}")


def unnecessary_computation(n: int = 100_000):
    # Recompute expensive value each loop vs caching
    def expensive(x: int) -> int:
        return sum(i * i for i in range(200)) + x
    t0 = time.perf_counter()
    s1 = sum(expensive(i) for i in range(n))
    t1 = time.perf_counter()
    cache = sum(i * i for i in range(200))
    t2 = time.perf_counter()
    s2 = sum(cache + i for i in range(n))
    t3 = time.perf_counter()
    print(f"Unnecessary computation: naive={t1-t0:.4f}s cached={t3-t2:.4f}s (same result? {s1==s2})")


def blocking_call_demo():
    # Simulate blocking call where streaming would help
    import requests  # optional; if unavailable, skip
    url = "https://httpbin.org/delay/1"
    t0 = time.perf_counter()
    try:
        requests.get(url, timeout=2)
        t1 = time.perf_counter()
        print(f"Blocking network call took {t1-t0:.2f}s (consider async or batching)")
    except Exception as e:
        print(f"Skipping network demo (requests not installed or network issue): {e}")


def main():
    print("-- performance pitfalls --")
    excessive_io("/tmp/p_big.txt")
    memory_growth(2000)
    unnecessary_computation(50_000)
    blocking_call_demo()


if __name__ == "__main__":
    main()
