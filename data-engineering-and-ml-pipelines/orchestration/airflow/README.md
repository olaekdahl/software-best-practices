# Airflow Demo (Orchestration)

This folder contains a minimal Airflow DAG that mirrors the custom orchestrator:
`extract -> transform -> load -> train -> evaluate`.

## Files

- `dags/widget_pipeline_dag.py`: Defines tasks using PythonOperator.

## Setup (Local Quickstart)

1. Create and activate a virtual environment (optional).
2. Install Airflow (you can pin a version as needed):

   ```bash
   pip install "apache-airflow==3.1.2"
   ```

3. Set AIRFLOW_HOME (or let Airflow default):

   ```bash
   export AIRFLOW_HOME="$(pwd)/airflow_home"
   mkdir -p "$AIRFLOW_HOME/dags"
   ```

4. Copy the `dags/` folder into `$AIRFLOW_HOME/dags/`.

   ```bash
   cp data-engineering-and-ml-pipelines/orchestration/airflow/dags/widget_pipeline_dag.py "$AIRFLOW_HOME/dags/"
   ```

5. Initialize metadata DB:

   ```bash
   airflow db check
   ```

6. Start webserver & scheduler:

   ```bash
   airflow standalone
   ```

7. Browse to `http://localhost:8080/`.

8. Check `simple_auth_manager_passwords.json.generated` for username and password.

9. Trigger the DAG manually in the UI or via CLI:

   ```bash
   airflow dags trigger widget_pipeline
   airflow tasks test widget_pipeline extract <run_id_or_date>
   ```

## Notes

- The Airflow DAG calls the same underlying scripts used by the custom orchestrator.
- For simplicity, scripts are executed directly; in a production setup you might containerize or use a task queue.
- This demo avoids extra providers and keeps everything Python-only.
