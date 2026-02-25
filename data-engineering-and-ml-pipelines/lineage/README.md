# Data Lineage

Track **where data comes from, how it is transformed, and where it goes** across
the pipeline.  This lightweight, stdlib-only example shows how to capture and
query lineage metadata without external infrastructure.

## Why lineage matters

| Concern | How lineage helps |
|---|---|
| **Debugging** | Trace a bad prediction back to the exact CSV row and transform step that produced it. |
| **Compliance** | Prove which sources contributed to a report or model. |
| **Impact analysis** | Before changing a source schema, find every downstream asset that depends on it. |
| **Reproducibility** | Record file hashes and timestamps so any output can be re-derived. |

## What's in here

| File | Purpose |
|---|---|
| `lineage_tracker.py` | Core `LineageTracker` class — records assets, transformations, and dependencies as a DAG. |
| `trace_pipeline.py` | Walks the existing pipeline end-to-end and builds a full lineage graph. |

## Quick run

```bash
# From the repo root
python3 data-engineering-and-ml-pipelines/lineage/trace_pipeline.py
```

This will:

1. Scan the project's real data files and outputs.
2. Build a lineage DAG covering **ingest → transform → train → serve**.
3. Print the lineage graph and an impact-analysis query.
4. Write `lineage/output/lineage.json` with the full metadata.

## Example output

```
=== LINEAGE GRAPH ===
[source]  customers.csv  (CSV, 3 records, sha256:ab12…)
[source]  orders.json  (JSON, 4 records, sha256:cd34…)
[source]  regions_db  (SQLite in-memory, 2 records)
   │
   ▼  transform: ingest_and_clean
[derived] cleaned_customers.csv  (CSV, 3 records, sha256:ef56…)
[derived] customer_order_summary.csv  (CSV, 2 records, sha256:78ab…)
   │
   ▼  transform: train_model
[derived] model.json  (JSON model artifact, sha256:9cde…)
   │
   ▼  transform: serve_model
[derived] /predict endpoint  (FastAPI, consumes model.json)

=== IMPACT ANALYSIS: what depends on customers.csv? ===
 → cleaned_customers.csv
 → customer_order_summary.csv
 → model.json (indirectly)
```

## Key concepts demonstrated

- **Assets** — any data artifact (file, table, endpoint) with metadata (hash, record count, schema snapshot).
- **Transformations** — named processing steps with inputs and outputs.
- **DAG traversal** — upstream (root-cause) and downstream (impact) queries.
- **Hashing** — SHA-256 fingerprints for change detection and reproducibility.
