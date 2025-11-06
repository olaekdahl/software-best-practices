"""Batch pipeline demo: reads prepared outputs and writes a timestamped summary.

Run:
  python3 data-engineering-and-ml-pipelines/batch-vs-streaming/batch_pipeline.py
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import json
import csv

ROOT = Path(__file__).resolve().parent
INGEST_OUT = ROOT.parent / "ingestion-and-transformation" / "output"
OUT = ROOT / "output"
OUT.mkdir(parents=True, exist_ok=True)


def read_customer_summaries(fp: Path):
    rows = []
    with fp.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            row["order_count"] = int(row["order_count"]) if row.get("order_count") else 0
            row["total_amount"] = float(row["total_amount"]) if row.get("total_amount") else 0.0
            rows.append(row)
    return rows


def main() -> None:
    summary_fp = INGEST_OUT / "customer_order_summary.csv"
    if not summary_fp.exists():
        raise SystemExit(
            "Missing ingestion outputs. Run ingest_transform.py first (see README)."
        )

    rows = read_customer_summaries(summary_fp)
    total_revenue = round(sum(r["total_amount"] for r in rows), 2)
    order_count = sum(r["order_count"] for r in rows)
    top_customer = max(rows, key=lambda r: r["total_amount"]) if rows else None

    dt = datetime.now(timezone.utc)
    payload = {
        "generated_at": dt.isoformat().replace("+00:00", "Z"),
        "order_count": order_count,
        "total_revenue": total_revenue,
        "top_customer": {
            "customer_id": top_customer.get("customer_id") if top_customer else None,
            "total_amount": top_customer.get("total_amount") if top_customer else None,
        },
        "source": str(summary_fp.relative_to(Path.cwd())) if summary_fp.is_absolute() else str(summary_fp),
    }

    out_fp = OUT / f"batch_summary_{dt.strftime('%Y%m%dT%H%M%SZ')}.json"
    with out_fp.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    print(f"Wrote batch summary → {out_fp}")


if __name__ == "__main__":
    main()
