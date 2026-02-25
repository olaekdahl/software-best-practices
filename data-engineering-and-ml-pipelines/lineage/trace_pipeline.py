"""Trace the existing widget pipeline and build a complete lineage graph.

Run:
    python3 data-engineering-and-ml-pipelines/lineage/trace_pipeline.py

Walks the real project files, registers every asset and transformation,
then prints the lineage graph, runs impact-analysis queries, and writes
the full metadata to ``lineage/output/lineage.json``.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure the lineage package is importable when run from the repo root.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from lineage_tracker import (
    Asset,
    LineageTracker,
    Transformation,
    count_csv_rows,
    csv_columns,
    file_sha256,
    json_keys,
    json_record_count,
)


ROOT = Path(__file__).resolve().parents[1]  # data-engineering-and-ml-pipelines/
DATA = ROOT / "ingestion-and-transformation" / "data"
TRANSFORM_OUT = ROOT / "ingestion-and-transformation" / "output"
MODEL_STORE = ROOT / "ml-pipeline" / "model_store"
LINEAGE_OUT = Path(__file__).resolve().parent / "output"


def _asset_from_csv(fp: Path, kind: str = "source") -> Asset:
    return Asset(
        name=fp.name,
        kind=kind,
        file_path=str(fp),
        format="CSV",
        record_count=count_csv_rows(fp),
        schema_snapshot=csv_columns(fp),
        sha256=file_sha256(fp),
    )


def _asset_from_json(fp: Path, kind: str = "source") -> Asset:
    return Asset(
        name=fp.name,
        kind=kind,
        file_path=str(fp),
        format="JSON",
        record_count=json_record_count(fp),
        schema_snapshot=json_keys(fp),
        sha256=file_sha256(fp),
    )


def build_lineage() -> LineageTracker:
    tracker = LineageTracker()

    # ------------------------------------------------------------------
    # 1. Source assets
    # ------------------------------------------------------------------
    customers_csv = DATA / "customers.csv"
    orders_json = DATA / "orders.json"

    if customers_csv.exists():
        tracker.add_asset(_asset_from_csv(customers_csv, kind="source"))

    if orders_json.exists():
        tracker.add_asset(_asset_from_json(orders_json, kind="source"))

    tracker.add_asset(Asset(
        name="regions_db",
        kind="source",
        format="SQLite",
        description="In-memory SQLite table with customer→region mapping",
        record_count=2,
        schema_snapshot=["customer_id", "region"],
    ))

    # ------------------------------------------------------------------
    # 2. Ingestion & transformation → derived assets
    # ------------------------------------------------------------------
    cleaned = TRANSFORM_OUT / "cleaned_customers.csv"
    summary = TRANSFORM_OUT / "customer_order_summary.csv"

    if cleaned.exists():
        tracker.add_asset(_asset_from_csv(cleaned, kind="derived"))
    else:
        tracker.add_asset(Asset(
            name="cleaned_customers.csv", kind="derived", format="CSV",
            description="(not yet generated — run ingest_transform.py first)",
        ))

    if summary.exists():
        tracker.add_asset(_asset_from_csv(summary, kind="derived"))
    else:
        tracker.add_asset(Asset(
            name="customer_order_summary.csv", kind="derived", format="CSV",
            description="(not yet generated — run ingest_transform.py first)",
        ))

    tracker.add_transformation(Transformation(
        name="ingest_and_clean",
        description="Read CSV + JSON + SQLite, deduplicate, enrich with regions, "
                    "summarise orders, write cleaned outputs.",
        inputs=["customers.csv", "orders.json", "regions_db"],
        outputs=["cleaned_customers.csv", "customer_order_summary.csv"],
        script="ingestion-and-transformation/ingest_transform.py",
    ))

    # ------------------------------------------------------------------
    # 3. ML training → model artifact
    # ------------------------------------------------------------------
    model_json = MODEL_STORE / "model.json"
    if model_json.exists():
        tracker.add_asset(_asset_from_json(model_json, kind="derived"))
    else:
        tracker.add_asset(Asset(
            name="model.json", kind="derived", format="JSON",
            description="(not yet generated — run train_model.py first)",
        ))

    tracker.add_transformation(Transformation(
        name="train_model",
        description="Generate synthetic data, fit simple linear regression, "
                    "save slope + intercept to JSON.",
        inputs=["customer_order_summary.csv"],
        outputs=["model.json"],
        script="ml-pipeline/train_model.py",
    ))

    # ------------------------------------------------------------------
    # 4. Serving endpoint (logical asset)
    # ------------------------------------------------------------------
    tracker.add_asset(Asset(
        name="/predict endpoint",
        kind="endpoint",
        format="FastAPI",
        description="HTTP GET /predict?x=N — returns y = slope*x + intercept",
        schema_snapshot=["x (query param)", "prediction (response)"],
        metadata={"url": "http://127.0.0.1:8000/predict"},
    ))

    tracker.add_transformation(Transformation(
        name="serve_model",
        description="FastAPI app loads model.json and exposes /predict.",
        inputs=["model.json"],
        outputs=["/predict endpoint"],
        script="ml-pipeline/serve_model.py",
    ))

    return tracker


def main() -> None:
    tracker = build_lineage()

    # -- Print full graph --------------------------------------------------
    print("=" * 60)
    print("  DATA LINEAGE GRAPH")
    print("=" * 60)
    tracker.print_graph()

    # -- Impact analysis examples -----------------------------------------
    for source in ["customers.csv", "orders.json"]:
        if tracker.get_asset(source):
            tracker.print_impact(source)

    # -- Upstream query example -------------------------------------------
    print("\n=== UPSTREAM: what feeds into model.json? ===")
    for ancestor in tracker.upstream("model.json"):
        print(f"  ← {ancestor}")

    # -- Root & leaf summary -----------------------------------------------
    print(f"\nRoots (original sources): {tracker.roots()}")
    print(f"Leaves (final outputs):   {tracker.leaves()}")

    # -- Persist full lineage to JSON --------------------------------------
    out_file = LINEAGE_OUT / "lineage.json"
    tracker.to_json(out_file)
    print(f"\nFull lineage written to {out_file}")


if __name__ == "__main__":
    main()
