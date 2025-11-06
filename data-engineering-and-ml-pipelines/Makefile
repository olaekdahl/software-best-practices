.PHONY := all ingest batch stream orchestrate train serve clean airflow-dag airflow-web airflow-scheduler airflow-trigger prefect-flow prefect-server

PY ?= python3
UVICORN ?= uvicorn

# Run everything except the server
all: ingest batch stream orchestrate train

ingest:
	$(PY) ingestion-and-transformation/ingest_transform.py

batch: ingest
	$(PY) batch-vs-streaming/batch_pipeline.py

stream:
	$(PY) batch-vs-streaming/streaming_pipeline.py

orchestrate:
	$(PY) orchestration/simple_orchestrator.py

train:
	$(PY) ml-pipeline/train_model.py

serve:
	$(UVICORN) ml-pipeline.serve_model:app --reload

# --- Airflow helpers (optional) ---
AIRFLOW ?= airflow
AIRFLOW_HOME ?= $(PWD)/airflow_home
AIRFLOW_DAGS ?= $(AIRFLOW_HOME)/dags

airflow-dag:
	mkdir -p "$(AIRFLOW_DAGS)"
	cp orchestration/airflow/dags/widget_pipeline_dag.py "$(AIRFLOW_DAGS)/"
	@echo "DAG copied to $(AIRFLOW_DAGS)." 

airflow-web:
	$(AIRFLOW) webserver --port 8080

airflow-scheduler:
	$(AIRFLOW) scheduler

airflow-trigger:
	$(AIRFLOW) dags trigger widget_pipeline

# --- Prefect helpers (optional) ---
PREFECT ?= prefect

prefect-flow:
	$(PY) orchestration/prefect/widget_pipeline_flow.py

prefect-server:
	$(PREFECT) server start

clean:
	rm -rf ingestion-and-transformation/output
	rm -rf batch-vs-streaming/output
	rm -rf orchestration/output orchestration/warehouse
	rm -rf ml-pipeline/model_store
