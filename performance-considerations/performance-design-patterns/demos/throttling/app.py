from __future__ import annotations

import time

class TokenBucket:
    def __init__(self, rate_per_sec: float, burst: int) -> None:
        self.rate = rate_per_sec
        self.capacity = burst
        self.tokens = float(burst)
        self.updated = time.time()

    def allow(self) -> bool:
        now = time.time()
        elapsed = now - self.updated
        self.updated = now
        self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
        if self.tokens >= 1.0:
            self.tokens -= 1.0
            return True
        return False

def main() -> None:
    limiter = TokenBucket(rate_per_sec=5, burst=3)

    allowed = 0
    blocked = 0
    for i in range(20):
        if limiter.allow():
            allowed += 1
            print(i, "allowed")
        else:
            blocked += 1
            print(i, "throttled (429)")
        time.sleep(0.05)

    print("allowed:", allowed, "blocked:", blocked)

if __name__ == "__main__":
    main()
