"""Airflow DAG mirroring the simple orchestrator.

Pipeline: extract -> transform -> load -> train -> evaluate

Each task runs existing scripts or lightweight Python code. This keeps the
example focused on orchestration rather than implementation details.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
import runpy

from airflow import DAG
from airflow.operators.python import PythonOperator

ROOT = Path(__file__).resolve().parents[3]  # points to data-engineering-and-ml-pipelines/
INGEST_DIR = ROOT / "ingestion-and-transformation"
ORCH_DIR = ROOT / "orchestration"
ML_DIR = ROOT / "ml-pipeline"


def task_extract():
    data_dir = INGEST_DIR / "data"
    customers = (data_dir / "customers.csv").read_text(encoding="utf-8")
    orders = (data_dir / "orders.json").read_text(encoding="utf-8")
    print("extract: customers bytes", len(customers), "orders bytes", len(orders))


def task_transform():
    script = INGEST_DIR / "ingest_transform.py"
    runpy.run_path(str(script))
    print("transform: completed ingest_transform.py")


def task_load():
    src = INGEST_DIR / "output"
    wh = ORCH_DIR / "warehouse_airflow"
    wh.mkdir(parents=True, exist_ok=True)
    for name in ["cleaned_customers.csv", "customer_order_summary.csv"]:
        (wh / name).write_text((src / name).read_text(encoding="utf-8"), encoding="utf-8")
    print("load: copied files to", wh)


def task_train():
    runpy.run_path(str(ML_DIR / "train_model.py"))
    print("train: model trained")


def task_evaluate():
    model_fp = ML_DIR / "model_store" / "model.json"
    size = model_fp.stat().st_size if model_fp.exists() else 0
    print("evaluate: model size bytes", size)


default_args = {
    "owner": "demo",
    "start_date": datetime(2025, 11, 5),
    "retries": 0,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="widget_pipeline",
    default_args=default_args,
    schedule_interval=None,  # trigger manually
    catchup=False,
    description="Widget pipeline demo using Airflow",
    tags=["demo", "widgetizer"],
) as dag:
    extract = PythonOperator(task_id="extract", python_callable=task_extract)
    transform = PythonOperator(task_id="transform", python_callable=task_transform)
    load = PythonOperator(task_id="load", python_callable=task_load)
    train = PythonOperator(task_id="train", python_callable=task_train)
    evaluate = PythonOperator(task_id="evaluate", python_callable=task_evaluate)

    extract >> transform >> [load, train] >> evaluate
