from __future__ import annotations

import random
from dataclasses import dataclass, field

@dataclass
class Agent:
    name: str
    capacity: int
    running: int = 0
    jobs: list[str] = field(default_factory=list)

    def can_take(self) -> bool:
        return self.running < self.capacity

    def assign(self, job_id: str) -> None:
        self.running += 1
        self.jobs.append(job_id)

class Supervisor:
    def __init__(self, agents: list[Agent]) -> None:
        self.agents = agents

    def schedule(self, job_id: str) -> str:
        candidates = [a for a in self.agents if a.can_take()]
        if not candidates:
            return "no-capacity"
        # Choose least-loaded agent (simple heuristic)
        a = min(candidates, key=lambda x: x.running / x.capacity)
        a.assign(job_id)
        return a.name

def main() -> None:
    agents = [Agent("A1", 3), Agent("A2", 2), Agent("A3", 5)]
    sup = Supervisor(agents)

    for i in range(12):
        job = f"job-{i}"
        dest = sup.schedule(job)
        print(job, "->", dest)

    for a in agents:
        print(a.name, "running", a.running, "jobs", a.jobs)

if __name__ == "__main__":
    main()
