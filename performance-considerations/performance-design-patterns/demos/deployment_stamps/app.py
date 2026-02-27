from __future__ import annotations

import random
from dataclasses import dataclass

@dataclass
class Stamp:
    name: str
    version: str

    def handle(self, request_id: str) -> str:
        return f"stamp={self.name} version={self.version} request={request_id}"

class Router:
    def __init__(self, stamps: list[Stamp]) -> None:
        self._stamps = stamps

    def route(self, request_id: str) -> str:
        # Simple scale-out: pick a stamp (could be based on tenant, geo, load)
        stamp = random.choice(self._stamps)
        return stamp.handle(request_id)

def main() -> None:
    stamps = [Stamp("stamp-a", "1.2.0"), Stamp("stamp-b", "1.2.0"), Stamp("stamp-c", "1.3.0")]
    r = Router(stamps)

    for i in range(6):
        print(r.route(f"req-{i}"))
    print("Capacity grows by adding stamps; multiple versions can run side-by-side for safe rollout.")

if __name__ == "__main__":
    main()
