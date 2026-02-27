from __future__ import annotations

import concurrent.futures
import time

def app_a(x: int) -> str:
    time.sleep(0.05)
    return f"A:{x*x}"

def app_b(x: int) -> str:
    time.sleep(0.05)
    return f"B:{x+1}"

def main() -> None:
    # Consolidate "apps" onto a shared worker pool instead of separate hosts.
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        futures = []
        for i in range(10):
            futures.append(pool.submit(app_a, i))
            futures.append(pool.submit(app_b, i))

        for fut in concurrent.futures.as_completed(futures):
            print(fut.result())

    print("Multiple components share one pool -> higher utilization / less overprovisioning.")

if __name__ == "__main__":
    main()
