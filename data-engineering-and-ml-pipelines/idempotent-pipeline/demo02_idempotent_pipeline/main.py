"""
Demo 02 - Idempotent Pipeline
================================
A pipeline that can be safely re-run without creating duplicates.

Instructor talking points:
- Idempotency: same input, same result, no matter how many runs
- Use natural keys or hash-based dedup
- Track pipeline runs with metadata
- Separate extract, transform, load stages
- Handle partial failures gracefully

Run: python main.py
"""

from __future__ import annotations

import csv
import hashlib
import json
import sqlite3
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from io import StringIO
from typing import Any


# ============================================================================
# Sample data
# ============================================================================

RAW_SALES_CSV = """date,product_id,product_name,quantity,unit_price,customer_id,region
2025-01-01,P001,Widget A,5,29.99,C100,North
2025-01-01,P002,Widget B,3,49.99,C101,South
2025-01-02,P001,Widget A,2,29.99,C102,North
2025-01-02,P003,Gadget X,1,199.99,C100,East
2025-01-03,P002,Widget B,10,49.99,C103,West
"""


# ============================================================================
# Pipeline infrastructure
# ============================================================================

class StageStatus(Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


@dataclass
class StageResult:
    """Result of a pipeline stage execution."""
    name: str
    status: StageStatus
    records_in: int = 0
    records_out: int = 0
    records_rejected: int = 0
    duration_ms: int = 0
    error: str = ""


@dataclass
class PipelineRun:
    """Metadata for a pipeline execution."""
    run_id: str
    pipeline_name: str
    started_at: str = ""
    completed_at: str = ""
    stages: list[StageResult] = field(default_factory=list)
    status: str = "RUNNING"

    def summary(self) -> dict:
        return {
            "run_id": self.run_id,
            "pipeline": self.pipeline_name,
            "status": self.status,
            "stages": len(self.stages),
            "total_duration_ms": sum(s.duration_ms for s in self.stages),
        }


def compute_row_hash(row: dict) -> str:
    """Compute a deterministic hash for a data row (natural key)."""
    # Use business keys for dedup, not surrogate keys
    key_fields = sorted(row.keys())
    key_str = "|".join(f"{k}={row[k]}" for k in key_fields)
    return hashlib.sha256(key_str.encode()).hexdigest()[:16]


# ============================================================================
# Pipeline stages
# ============================================================================

def extract(source_csv: str) -> tuple[list[dict], StageResult]:
    """Extract stage: read raw data from source."""
    start = time.perf_counter()
    reader = csv.DictReader(StringIO(source_csv))
    rows = list(reader)
    elapsed = int((time.perf_counter() - start) * 1000)

    return rows, StageResult(
        name="extract",
        status=StageStatus.SUCCESS,
        records_in=len(rows),
        records_out=len(rows),
        duration_ms=elapsed,
    )


def transform(rows: list[dict]) -> tuple[list[dict], list[dict], StageResult]:
    """Transform stage: clean, validate, enrich data."""
    start = time.perf_counter()
    valid = []
    rejected = []

    for row in rows:
        # Validate
        errors = []
        try:
            qty = int(row.get("quantity", 0))
            if qty <= 0:
                errors.append(f"invalid quantity: {qty}")
        except ValueError:
            errors.append(f"non-numeric quantity: {row.get('quantity')}")
            qty = 0

        try:
            price = float(row.get("unit_price", 0))
            if price <= 0:
                errors.append(f"invalid price: {price}")
        except ValueError:
            errors.append(f"non-numeric price: {row.get('unit_price')}")
            price = 0

        if not row.get("product_name", "").strip():
            errors.append("missing product_name")

        if not row.get("customer_id", "").strip():
            errors.append("missing customer_id")

        if errors:
            rejected.append({**row, "_errors": errors})
            continue

        # Enrich
        total = qty * price
        row_hash = compute_row_hash(row)
        valid.append({
            "row_hash": row_hash,
            "date": row["date"],
            "product_id": row["product_id"],
            "product_name": row["product_name"].strip(),
            "quantity": qty,
            "unit_price": price,
            "total": round(total, 2),
            "customer_id": row["customer_id"],
            "region": row.get("region", "Unknown"),
            "loaded_at": datetime.now().isoformat(),
        })

    elapsed = int((time.perf_counter() - start) * 1000)
    return valid, rejected, StageResult(
        name="transform",
        status=StageStatus.SUCCESS,
        records_in=len(rows),
        records_out=len(valid),
        records_rejected=len(rejected),
        duration_ms=elapsed,
    )


def load(db: sqlite3.Connection, rows: list[dict]) -> StageResult:
    """Load stage: upsert data using row_hash for idempotency."""
    start = time.perf_counter()
    inserted = 0
    skipped = 0

    for row in rows:
        # Check if row already exists (idempotency via hash)
        existing = db.execute(
            "SELECT 1 FROM sales WHERE row_hash = ?",
            (row["row_hash"],)
        ).fetchone()

        if existing:
            skipped += 1
            continue

        db.execute("""
            INSERT INTO sales (row_hash, date, product_id, product_name,
                             quantity, unit_price, total, customer_id,
                             region, loaded_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            row["row_hash"], row["date"], row["product_id"],
            row["product_name"], row["quantity"], row["unit_price"],
            row["total"], row["customer_id"], row["region"],
            row["loaded_at"],
        ))
        inserted += 1

    db.commit()
    elapsed = int((time.perf_counter() - start) * 1000)

    return StageResult(
        name="load",
        status=StageStatus.SUCCESS,
        records_in=len(rows),
        records_out=inserted,
        records_rejected=skipped,
        duration_ms=elapsed,
    )


# ============================================================================
# Pipeline orchestrator
# ============================================================================

def setup_database() -> sqlite3.Connection:
    """Create database schema."""
    db = sqlite3.connect(":memory:")
    db.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            row_hash TEXT PRIMARY KEY,
            date TEXT NOT NULL,
            product_id TEXT NOT NULL,
            product_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            total REAL NOT NULL,
            customer_id TEXT NOT NULL,
            region TEXT,
            loaded_at TEXT NOT NULL
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS pipeline_runs (
            run_id TEXT PRIMARY KEY,
            pipeline_name TEXT,
            status TEXT,
            started_at TEXT,
            completed_at TEXT,
            metadata TEXT
        )
    """)
    return db


def run_pipeline(db: sqlite3.Connection, run_id: str) -> PipelineRun:
    """Execute the full ETL pipeline."""
    run = PipelineRun(
        run_id=run_id,
        pipeline_name="sales_etl",
        started_at=datetime.now().isoformat(),
    )

    print(f"  Pipeline run: {run_id}")

    # Stage 1: Extract
    raw_rows, extract_result = extract(RAW_SALES_CSV)
    run.stages.append(extract_result)
    print(f"    Extract: {extract_result.records_out} rows")

    # Stage 2: Transform
    valid_rows, rejected_rows, transform_result = transform(raw_rows)
    run.stages.append(transform_result)
    print(f"    Transform: {transform_result.records_out} valid, "
          f"{transform_result.records_rejected} rejected")

    if rejected_rows:
        for r in rejected_rows:
            print(f"      Rejected: {r.get('product_id', 'N/A')} - {r.get('_errors', [])}")

    # Stage 3: Load (idempotent)
    load_result = load(db, valid_rows)
    run.stages.append(load_result)
    print(f"    Load: {load_result.records_out} inserted, "
          f"{load_result.records_rejected} skipped (already exist)")

    run.completed_at = datetime.now().isoformat()
    run.status = "SUCCESS"

    # Record pipeline run metadata
    db.execute(
        "INSERT OR REPLACE INTO pipeline_runs VALUES (?, ?, ?, ?, ?, ?)",
        (run.run_id, run.pipeline_name, run.status,
         run.started_at, run.completed_at,
         json.dumps(run.summary())),
    )
    db.commit()

    return run


# ============================================================================
# Main
# ============================================================================

def main():
    print("=== Demo: Idempotent Pipeline ===\n")

    db = setup_database()

    # First run - inserts all valid rows
    print("--- Run 1 (First Execution) ---\n")
    run1 = run_pipeline(db, "run-001")
    print(f"\n  Result: {run1.summary()}")
    print()

    # Second run - should skip all rows (idempotent!)
    print("--- Run 2 (Re-execution - Idempotent) ---\n")
    run2 = run_pipeline(db, "run-002")
    print(f"\n  Result: {run2.summary()}")
    print()

    # Verify database state
    cursor = db.execute("SELECT COUNT(*) FROM sales")
    total_rows = cursor.fetchone()[0]
    print(f"  Total rows in database: {total_rows} (no duplicates)")

    cursor = db.execute("SELECT COUNT(*) FROM pipeline_runs")
    total_runs = cursor.fetchone()[0]
    print(f"  Total pipeline runs: {total_runs}")
    print()

    # Show final data
    print("--- Final Data ---\n")
    cursor = db.execute("SELECT date, product_id, product_name, quantity, total FROM sales ORDER BY date")
    print(f"  {'Date':<12} {'Product':<8} {'Name':<12} {'Qty':>4} {'Total':>10}")
    print(f"  {'-'*12} {'-'*8} {'-'*12} {'-'*4} {'-'*10}")
    for row in cursor:
        print(f"  {row[0]:<12} {row[1]:<8} {row[2]:<12} {row[3]:>4} {row[4]:>10.2f}")

    print("\n--- Idempotency Benefits ---")
    print("1. Safe to re-run: no duplicates created")
    print("2. Hash-based dedup using business keys")
    print("3. Pipeline metadata tracked for auditing")
    print("4. Rejected records logged with reasons")
    print("5. Each stage reports metrics independently")

    db.close()


if __name__ == "__main__":
    main()
