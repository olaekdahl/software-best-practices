from __future__ import annotations

import random
import time
from dataclasses import dataclass

@dataclass
class CircuitBreaker:
    failure_threshold: int = 3
    recovery_seconds: float = 1.0

    _failures: int = 0
    _state: str = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    _opened_at: float = 0.0

    def call(self, fn, *args, **kwargs):
        now = time.time()
        if self._state == "OPEN":
            if now - self._opened_at >= self.recovery_seconds:
                self._state = "HALF_OPEN"
            else:
                raise RuntimeError("circuit open")

        try:
            result = fn(*args, **kwargs)
        except Exception:
            self._failures += 1
            if self._failures >= self.failure_threshold:
                self._state = "OPEN"
                self._opened_at = now
            raise
        else:
            # Success resets breaker (or closes from HALF_OPEN)
            self._failures = 0
            self._state = "CLOSED"
            return result

def flaky_dependency() -> str:
    if random.random() < 0.5:
        raise RuntimeError("dependency failed")
    return "ok"

def main() -> None:
    cb = CircuitBreaker(failure_threshold=2, recovery_seconds=0.8)

    for i in range(12):
        time.sleep(0.1)
        try:
            out = cb.call(flaky_dependency)
            print(i, "call =>", out, "(state=CLOSED)")
        except Exception as e:
            print(i, "call =>", str(e), f"(state={cb._state}, failures={cb._failures})")

if __name__ == "__main__":
    main()
