from __future__ import annotations

import queue
import time

def main() -> None:
    pq: queue.PriorityQueue[tuple[int, str]] = queue.PriorityQueue()
    pq.put((10, "low: generate weekly report"))
    pq.put((1, "high: fraud alert"))
    pq.put((5, "med: send receipt email"))

    while not pq.empty():
        prio, task = pq.get()
        print(f"Processing priority={prio}: {task}")
        time.sleep(0.05)

if __name__ == "__main__":
    main()
