from __future__ import annotations

import queue
import threading
import time
from dataclasses import dataclass

@dataclass(frozen=True)
class LogEntry:
    msg: str
    ts: float

log_q: queue.Queue[LogEntry] = queue.Queue()

def sidecar_logger() -> None:
    while True:
        entry = log_q.get()
        if entry.msg == "STOP":
            log_q.task_done()
            return
        # Sidecar handles cross-cutting concern (logging/metrics) off the main path
        print(f"[sidecar] {entry.ts:.3f} {entry.msg}")
        log_q.task_done()

def app_work() -> None:
    for i in range(5):
        # Main app does business work and emits logs asynchronously
        log_q.put(LogEntry(f"processed item {i}", time.time()))
        time.sleep(0.05)

def main() -> None:
    t = threading.Thread(target=sidecar_logger, daemon=True)
    t.start()

    app_work()
    log_q.join()
    log_q.put(LogEntry("STOP", time.time()))
    log_q.join()
    print("Main app stayed simple; sidecar took responsibility for logging.")

if __name__ == "__main__":
    main()
