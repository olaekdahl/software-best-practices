from __future__ import annotations

import concurrent.futures
import random
import time

def slow_unreliable(name: str) -> str:
    # Simulate occasional slowness/failure.
    t = random.choice([0.05, 0.1, 0.8])
    time.sleep(t)
    if t > 0.5:
        raise RuntimeError(f"{name} dependency timed out")
    return f"{name} ok in {t:.2f}s"

def main() -> None:
    # Separate thread pools = separate bulkheads
    fast_pool = concurrent.futures.ThreadPoolExecutor(max_workers=8)
    slow_pool = concurrent.futures.ThreadPoolExecutor(max_workers=2)

    futures = []
    for i in range(10):
        futures.append(fast_pool.submit(slow_unreliable, f"fast_path_{i}"))
    for i in range(6):
        futures.append(slow_pool.submit(slow_unreliable, f"slow_path_{i}"))

    done = 0
    for fut in concurrent.futures.as_completed(futures):
        done += 1
        try:
            print("Result:", fut.result())
        except Exception as e:
            print("Error:", e)

    print(f"Completed {done} tasks. Slow-path overload doesn't starve fast-path capacity.")
    fast_pool.shutdown(wait=True)
    slow_pool.shutdown(wait=True)

if __name__ == "__main__":
    main()
