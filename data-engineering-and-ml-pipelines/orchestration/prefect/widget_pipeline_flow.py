"""Prefect flow mirroring the simple orchestrator.

Run locally:
  python3 data-engineering-and-ml-pipelines/orchestration/prefect/widget_pipeline_flow.py
"""

from __future__ import annotations

from pathlib import Path
import runpy
from datetime import datetime, timezone

from prefect import flow, task


ROOT = Path(__file__).resolve().parents[2]
INGEST_DIR = ROOT / "ingestion-and-transformation"
ORCH_DIR = ROOT / "orchestration"
ML_DIR = ROOT / "ml-pipeline"


@task
def extract() -> None:
    data_dir = INGEST_DIR / "data"
    customers = (data_dir / "customers.csv").read_text(encoding="utf-8")
    orders = (data_dir / "orders.json").read_text(encoding="utf-8")
    print("extract: customers bytes", len(customers), "orders bytes", len(orders))


@task
def transform() -> None:
    runpy.run_path(str(INGEST_DIR / "ingest_transform.py"))
    print("transform: completed ingest_transform.py")


@task
def load() -> None:
    src = INGEST_DIR / "output"
    wh = ORCH_DIR / "warehouse_prefect"
    wh.mkdir(parents=True, exist_ok=True)
    for name in ["cleaned_customers.csv", "customer_order_summary.csv"]:
        (wh / name).write_text((src / name).read_text(encoding="utf-8"), encoding="utf-8")
    print("load: copied files to", wh)


@task
def train() -> None:
    runpy.run_path(str(ML_DIR / "train_model.py"))
    print("train: model trained")


@task
def evaluate() -> None:
    model_fp = ML_DIR / "model_store" / "model.json"
    size = model_fp.stat().st_size if model_fp.exists() else 0
    print("evaluate: model size bytes", size)


@flow(name="widget-pipeline-prefect")
def widget_pipeline_flow() -> None:
    extract()
    transform()
    # fan-out
    load_f = load.submit()
    train_f = train.submit()
    # fan-in
    load_f.result()
    train_f.result()
    evaluate()
    dt = datetime.now(timezone.utc)
    print("flow completed at", dt.isoformat().replace("+00:00", "Z"))


if __name__ == "__main__":
    widget_pipeline_flow()
