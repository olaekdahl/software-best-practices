"""A tiny orchestration demo with a DAG of dependent tasks.

Run:
  python3 data-engineering-and-ml-pipelines/orchestration/simple_orchestrator.py
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, List
import runpy
from datetime import datetime, timezone


ROOT = Path(__file__).resolve().parent
LOG = ROOT / "output"
LOG.mkdir(parents=True, exist_ok=True)


TaskFunc = Callable[[], None]


@dataclass
class Task:
    name: str
    run: TaskFunc
    deps: List[str] = field(default_factory=list)


class Orchestrator:
    def __init__(self, tasks: List[Task]):
        self.tasks: Dict[str, Task] = {t.name: t for t in tasks}
        self.done: List[str] = []

    def run_all(self) -> None:
        while len(self.done) < len(self.tasks):
            scheduled = False
            for name, task in self.tasks.items():
                if name in self.done:
                    continue
                if all(d in self.done for d in task.deps):
                    self._log(f"START {name}")
                    task.run()
                    self.done.append(name)
                    self._log(f"DONE  {name}")
                    scheduled = True
            if not scheduled:
                missing = {n: [d for d in t.deps if d not in self.done] for n, t in self.tasks.items() if n not in self.done}
                raise RuntimeError(f"No runnable tasks. Cycles or missing deps? {missing}")

    def _log(self, msg: str) -> None:
        dt = datetime.now(timezone.utc)
        line = f"{dt.isoformat().replace('+00:00','Z')} | {msg}\n"
        (LOG / "run.log").open("a", encoding="utf-8").write(line)
        print(line, end="")


def task_extract() -> None:
    # Just read the input files to prove availability
    base = ROOT.parent / "ingestion-and-transformation" / "data"
    customers = (base / "customers.csv").read_text(encoding="utf-8")
    orders = (base / "orders.json").read_text(encoding="utf-8")
    (LOG / "extract.ok").write_text(f"customers={len(customers)} bytes orders={len(orders)} bytes", encoding="utf-8")


def task_transform() -> None:
    # Execute the ingestion/transform script in-process
    script = ROOT.parent / "ingestion-and-transformation" / "ingest_transform.py"
    runpy.run_path(str(script))
    (LOG / "transform.ok").write_text("transform complete", encoding="utf-8")


def task_load() -> None:
    # Simulate loading into a warehouse by copying files into an area
    wh = ROOT / "warehouse"
    wh.mkdir(parents=True, exist_ok=True)
    src = ROOT.parent / "ingestion-and-transformation" / "output"
    for name in ("cleaned_customers.csv", "customer_order_summary.csv"):
        content = (src / name).read_text(encoding="utf-8")
        (wh / name).write_text(content, encoding="utf-8")
    (LOG / "load.ok").write_text("warehouse loaded", encoding="utf-8")


def task_train() -> None:
    script = ROOT.parent / "ml-pipeline" / "train_model.py"
    runpy.run_path(str(script))
    (LOG / "train.ok").write_text("model trained", encoding="utf-8")


def task_evaluate() -> None:
    model_fp = ROOT.parent / "ml-pipeline" / "model_store" / "model.json"
    data = model_fp.read_text(encoding="utf-8") if model_fp.exists() else "{}"
    (LOG / "evaluate.ok").write_text(f"model bytes={len(data)}", encoding="utf-8")


def main() -> None:
    tasks = [
        Task("extract", task_extract),
        Task("transform", task_transform, deps=["extract"]),
        Task("load", task_load, deps=["transform"]),
        Task("train", task_train, deps=["transform"]),
        Task("evaluate", task_evaluate, deps=["train", "load"]),
    ]
    Orchestrator(tasks).run_all()


if __name__ == "__main__":
    main()
