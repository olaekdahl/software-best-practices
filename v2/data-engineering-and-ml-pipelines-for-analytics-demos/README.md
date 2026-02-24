# Data Engineering and ML Pipelines for Analytics - Demos

Progressive demos from simple ETL to orchestrated ML pipelines.

| Demo | Topic | Complexity |
|------|-------|-----------|
| demo01_simple_etl | Basic ETL script with no structure | Naive |
| demo02_idempotent_pipeline | Idempotent, resumable pipeline | Intermediate |
| demo03_data_validation | Data contracts and schema validation | Intermediate |
| demo04_ml_lifecycle | Model train, validate, deploy, monitor | Advanced |
| demo05_orchestrated_pipeline | Full orchestrated pipeline with lineage | Real-world |

## Setup

```bash
pip install pandas jsonschema scikit-learn
```

## Running

```bash
cd demo01_simple_etl
python main.py
```
