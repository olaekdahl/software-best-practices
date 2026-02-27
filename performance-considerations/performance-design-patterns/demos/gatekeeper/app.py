from __future__ import annotations

import time
from dataclasses import dataclass

@dataclass
class Request:
    user: str
    path: str

class RateLimiter:
    def __init__(self, per_second: int) -> None:
        self.per_second = per_second
        self._counts: dict[int, int] = {}

    def allow(self) -> bool:
        now_s = int(time.time())
        self._counts.setdefault(now_s, 0)
        self._counts[now_s] += 1
        return self._counts[now_s] <= self.per_second

class Gatekeeper:
    def __init__(self, valid_users: set[str], limiter: RateLimiter) -> None:
        self.valid_users = valid_users
        self.limiter = limiter

    def forward(self, req: Request) -> str:
        if req.user not in self.valid_users:
            return "401 unauthorized (blocked at gatekeeper)"
        if not self.limiter.allow():
            return "429 too many requests (blocked at gatekeeper)"
        return backend(req)

def backend(req: Request) -> str:
    return f"200 ok from backend for {req.user} {req.path}"

def main() -> None:
    gk = Gatekeeper(valid_users={"alice", "bob"}, limiter=RateLimiter(per_second=3))
    for i in range(6):
        print(gk.forward(Request("alice", f"/items/{i}")))
        time.sleep(0.1)

if __name__ == "__main__":
    main()
