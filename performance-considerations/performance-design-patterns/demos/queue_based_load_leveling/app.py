from __future__ import annotations

import queue
import threading
import time

q: queue.Queue[int] = queue.Queue()

def producer() -> None:
    # Burst of work (spiky traffic)
    for i in range(30):
        q.put(i)
    print("Producer: burst enqueued 30 items quickly.")

def consumer() -> None:
    # Controlled pace
    while True:
        item = q.get()
        if item == -1:
            q.task_done()
            return
        time.sleep(0.05)
        print("Consumer processed", item)
        q.task_done()

def main() -> None:
    t = threading.Thread(target=consumer, daemon=True)
    t.start()

    producer()
    q.join()
    q.put(-1)
    q.join()
    print("Queue absorbs burst; consumer processes at stable rate.")

if __name__ == "__main__":
    main()
