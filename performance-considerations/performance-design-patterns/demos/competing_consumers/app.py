from __future__ import annotations

import queue
import threading
import time

def worker(name: str, q: queue.Queue[int]) -> None:
    while True:
        item = q.get()
        if item == -1:
            q.task_done()
            return
        time.sleep(0.05)  # work
        print(f"{name} processed {item}")
        q.task_done()

def main() -> None:
    q: queue.Queue[int] = queue.Queue()
    workers = [threading.Thread(target=worker, args=(f"W{i}", q), daemon=True) for i in range(4)]
    for w in workers:
        w.start()

    for i in range(20):
        q.put(i)

    q.join()
    for _ in workers:
        q.put(-1)
    q.join()
    print("Work distributed across consumers; scale by adding workers.")

if __name__ == "__main__":
    main()
