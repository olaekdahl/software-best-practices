# Data Engineering & ML Pipelines for Analytics

This folder contains small, runnable demos for common data/ML pipeline concepts. All examples use standard Python libraries unless noted. Run them with `python3` from the repo root.

## Demos

- ingestion-and-transformation/ — Extract from multiple sources (CSV, JSON, SQLite), clean, and prepare outputs for analysis.
- batch-vs-streaming/ — Compare a scheduled batch job with a simple simulated streaming pipeline.
- orchestration/ — A lightweight DAG-style workflow runner showing task dependencies.
- orchestration/airflow/ — Airflow DAG version of the pipeline (optional dependency).
- orchestration/prefect/ — Prefect flow version of the pipeline (optional dependency).
- ml-pipeline/ — Minimal ML pipeline: data prep → training (linear regression) → deploy with a tiny FastAPI service.

See each subfolder for scripts and usage notes below.

## Quick run

- Ingestion & transform:
  - `python3 data-engineering-and-ml-pipelines/ingestion-and-transformation/ingest_transform.py`
- Batch job:
  - `python3 data-engineering-and-ml-pipelines/batch-vs-streaming/batch_pipeline.py`
- Streaming job (simulated):
  - `python3 data-engineering-and-ml-pipelines/batch-vs-streaming/streaming_pipeline.py --poll-interval 0.5 --pattern "events*.jsonl"`
- Train model and serve predictions:
  - Train the model (writes `ml-pipeline/model_store/model.json`):
    - `python3 data-engineering-and-ml-pipelines/ml-pipeline/train_model.py`
  - Start the API (from repo root, no cd needed):
    - `uvicorn serve_model:app --reload --app-dir data-engineering-and-ml-pipelines/ml-pipeline`

Note: The serving step uses FastAPI/uvicorn (already in this repo's requirements).

### How the training script works

The training step is intentionally simple and uses only Python's standard library:

- It generates synthetic pairs of inputs and outputs `(x, y)` following a straight‑line relationship with a bit of random noise, roughly `y ≈ 3x + 2`.
- It computes the "best‑fit" straight line through those points using basic statistics (averages and sums). This is classic simple linear regression, yielding two numbers:
  - slope (m) — how steep the line is
  - intercept (b) — where it crosses the y‑axis
- It saves those numbers to JSON at `ml-pipeline/model_store/model.json`.

When you start the API, it loads the JSON file and, for any input `x`, returns a prediction `y = m*x + b`. There's no heavy ML framework involved here—just a tiny, transparent demo showing the flow: generate -> fit -> save -> serve.

Quick test after starting the server:

```bash
curl http://127.0.0.1:8000/health
curl "http://127.0.0.1:8000/predict?x=5"
```

## Makefile shortcuts

You can also use the included Makefile from the repo root:

```bash
# Run everything except the server
make -C data-engineering-and-ml-pipelines all

# Or run individually
make -C data-engineering-and-ml-pipelines ingest
make -C data-engineering-and-ml-pipelines batch
make -C data-engineering-and-ml-pipelines stream
make -C data-engineering-and-ml-pipelines orchestrate
make -C data-engineering-and-ml-pipelines train

# Start the prediction service (stop with Ctrl+C)
make -C data-engineering-and-ml-pipelines serve

# Clean generated outputs
make -C data-engineering-and-ml-pipelines clean
```

## Optional orchestration frameworks

Airflow and Prefect versions of the pipeline live under `orchestration/airflow/` and `orchestration/prefect/`.
They replicate: extract → transform → load → train → evaluate.

### Airflow

Step-by-step local demo (no production hardening):

1. (Optional) Create a virtual environment.

  ```bash
  python3 -m venv .venv && source .venv/bin/activate
  ```

2. Install Airflow:

  ```bash
  pip install "apache-airflow==3.1.2"
  ```

3. Set an Airflow home directory (inside this repo or elsewhere):

  ```bash
  export AIRFLOW_HOME="$(pwd)/airflow_home"
  mkdir -p "$AIRFLOW_HOME/dags"
  ```

4. Copy the DAG:

  ```bash
  cp data-engineering-and-ml-pipelines/orchestration/airflow/dags/widget_pipeline_dag.py "$AIRFLOW_HOME/dags/"
  ```

5. Initialize the metadata DB:

  ```bash
  airflow db connect
  ```

6. Start services:

  ```bash
  airflow standalone
  ```

7. Login: Check `simple_auth_manager_passwords.json.generated` for username and password for web UI login.
8. Trigger the DAG:

  ```bash
  airflow dags trigger widget_pipeline
  ```

9. (Optional) Inspect tasks:

  ```bash
  airflow tasks list widget_pipeline
  airflow tasks test widget_pipeline extract 2025-11-05
  ```

10. View results under the original project folders (the DAG runs your local scripts).

Cleanup (optional): remove the `airflow_home` directory or deactivate the venv.

### Prefect

Local flow run:

1. (Optional) Create a virtual environment.

  ```bash
  python3 -m venv .venv && source .venv/bin/activate
  ```

2. Install Prefect:

  ```bash
  pip install "prefect==2.*"
  ```

3. Run the flow directly:

  ```bash
  python3 data-engineering-and-ml-pipelines/orchestration/prefect/widget_pipeline_flow.py
  ```

4. (Optional UI) Start Orion server:

  ```bash
  prefect server start
  ```

5. (Optional) Register a deployment (advanced use):

  ```bash
  prefect deployment build data-engineering-and-ml-pipelines/orchestration/prefect/widget_pipeline_flow.py:widget_pipeline_flow -n local-run
  prefect deployment apply widget_pipeline_flow-deployment.yaml
  prefect deployment run widget-pipeline-prefect/local-run
  ```

Cleanup: stop `prefect server`, remove `.venv` if created.
