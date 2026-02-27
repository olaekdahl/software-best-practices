from __future__ import annotations

import queue
import threading
import time
import uuid
from dataclasses import dataclass

@dataclass(frozen=True)
class Job:
    job_id: str
    payload: str

@dataclass(frozen=True)
class Result:
    job_id: str
    output: str

class JobServer:
    def __init__(self) -> None:
        self._jobs: queue.Queue[Job] = queue.Queue()
        self._results: dict[str, Result] = {}
        self._stop = threading.Event()
        self._worker = threading.Thread(target=self._run, daemon=True)

    def start(self) -> None:
        self._worker.start()

    def stop(self) -> None:
        self._stop.set()
        self._jobs.put(Job("STOP", ""))
        self._worker.join(timeout=2)

    def submit(self, payload: str) -> str:
        job_id = uuid.uuid4().hex
        self._jobs.put(Job(job_id, payload))
        return job_id

    def get_result(self, job_id: str) -> Result | None:
        return self._results.get(job_id)

    def _run(self) -> None:
        while not self._stop.is_set():
            job = self._jobs.get()
            if job.job_id == "STOP":
                return
            # Simulate long work.
            time.sleep(0.3)
            self._results[job.job_id] = Result(job.job_id, output=job.payload.upper())

def main() -> None:
    server = JobServer()
    server.start()

    print("Client: submit work and continue immediately (no blocking).")
    job_id = server.submit("render_report_for_user_123")
    print(f"Client: got job_id={job_id}, doing other things...")
    time.sleep(0.1)

    print("Client: later, poll for result (or you could use callbacks/webhooks).")
    while True:
        res = server.get_result(job_id)
        if res:
            print("Client: received:", res)
            break
        time.sleep(0.05)

    server.stop()

if __name__ == "__main__":
    main()
