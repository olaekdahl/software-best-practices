"""
Demo 01 - Simple ETL Script (Anti-patterns)
==============================================
A naive ETL script with common data engineering anti-patterns.

Instructor talking points:
- No error handling or retry logic
- No idempotency (rerun = duplicates)
- No data validation
- No logging or observability
- Hardcoded paths and config
- No separation of concerns

Run: python main.py
"""

from __future__ import annotations

import csv
import json
import os
import sqlite3
from io import StringIO


# ============================================================================
# Simulated raw data (in real life: files, APIs, databases)
# ============================================================================

RAW_SALES_CSV = """date,product_id,product_name,quantity,unit_price,customer_id,region
2025-01-01,P001,Widget A,5,29.99,C100,North
2025-01-01,P002,Widget B,3,49.99,C101,South
2025-01-02,P001,Widget A,2,29.99,C102,North
2025-01-02,P003,Gadget X,1,199.99,C100,East
2025-01-03,P002,Widget B,10,49.99,C103,West
2025-01-03,P001,Widget A,-1,29.99,C104,North
2025-01-03,P004,,7,0,C105,South
2025-01-04,P001,Widget A,3,29.99,C100,North
2025-01-04,P002,Widget B,2,49.99,,East
"""


# ============================================================================
# Anti-pattern: Monolithic ETL function
# ============================================================================

def run_naive_etl():
    """Monolithic ETL with all anti-patterns.

    Problems:
    1. Extract, transform, load all in one function
    2. No error handling (one bad row crashes everything)
    3. No validation (accepts negative quantities, empty names)
    4. No idempotency (rerunning creates duplicates)
    5. Hardcoded database path
    6. No logging
    7. No data quality checks
    """
    # EXTRACT - read CSV
    reader = csv.DictReader(StringIO(RAW_SALES_CSV))
    rows = list(reader)
    print(f"  Extracted {len(rows)} rows")

    # TRANSFORM - calculate totals (no validation!)
    transformed = []
    for row in rows:
        total = int(row["quantity"]) * float(row["unit_price"])
        transformed.append({
            "date": row["date"],
            "product_id": row["product_id"],
            "product_name": row["product_name"],
            "quantity": int(row["quantity"]),
            "unit_price": float(row["unit_price"]),
            "total": total,
            "customer_id": row["customer_id"],
            "region": row["region"],
        })
    print(f"  Transformed {len(transformed)} rows")

    # LOAD - insert into SQLite (no dedup!)
    db = sqlite3.connect(":memory:")
    db.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            date TEXT,
            product_id TEXT,
            product_name TEXT,
            quantity INTEGER,
            unit_price REAL,
            total REAL,
            customer_id TEXT,
            region TEXT
        )
    """)

    for row in transformed:
        db.execute(
            "INSERT INTO sales VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (row["date"], row["product_id"], row["product_name"],
             row["quantity"], row["unit_price"], row["total"],
             row["customer_id"], row["region"]),
        )
    db.commit()
    print(f"  Loaded {len(transformed)} rows into database")

    # Quick query to show results
    cursor = db.execute("SELECT * FROM sales")
    results = cursor.fetchall()
    return db, results


# ============================================================================
# Show the problems
# ============================================================================

def analyze_problems(db: sqlite3.Connection):
    """Show data quality issues that the naive ETL didn't catch."""
    print("\n--- Data Quality Issues (Uncaught) ---\n")

    # Negative quantities
    cursor = db.execute("SELECT * FROM sales WHERE quantity < 0")
    negatives = cursor.fetchall()
    print(f"  Negative quantities: {len(negatives)} rows")
    for row in negatives:
        print(f"    {row}")

    # Missing product names
    cursor = db.execute(
        "SELECT * FROM sales WHERE product_name IS NULL OR product_name = ''"
    )
    missing_names = cursor.fetchall()
    print(f"  Missing product names: {len(missing_names)} rows")
    for row in missing_names:
        print(f"    {row}")

    # Zero prices
    cursor = db.execute("SELECT * FROM sales WHERE unit_price = 0")
    zero_prices = cursor.fetchall()
    print(f"  Zero prices: {len(zero_prices)} rows")
    for row in zero_prices:
        print(f"    {row}")

    # Missing customer IDs
    cursor = db.execute(
        "SELECT * FROM sales WHERE customer_id IS NULL OR customer_id = ''"
    )
    missing_customers = cursor.fetchall()
    print(f"  Missing customer IDs: {len(missing_customers)} rows")
    for row in missing_customers:
        print(f"    {row}")

    # Negative totals
    cursor = db.execute("SELECT * FROM sales WHERE total < 0")
    negative_totals = cursor.fetchall()
    print(f"  Negative totals: {len(negative_totals)} rows")


# ============================================================================
# Main
# ============================================================================

def main():
    print("=== Demo: Naive ETL Script (Anti-patterns) ===\n")

    print("--- Running ETL ---\n")
    db, results = run_naive_etl()

    print(f"\n--- Loaded Data ({len(results)} rows) ---\n")
    print(f"  {'Date':<12} {'Product':<10} {'Qty':>4} {'Price':>8} {'Total':>10} {'Customer':<8} {'Region':<6}")
    print(f"  {'-'*12} {'-'*10} {'-'*4} {'-'*8} {'-'*10} {'-'*8} {'-'*6}")
    for row in results:
        print(f"  {row[0]:<12} {row[1]:<10} {row[3]:>4} {row[4]:>8.2f} {row[5]:>10.2f} {row[6]:<8} {row[7]:<6}")

    analyze_problems(db)

    print("\n--- Problems with this ETL ---")
    print("1. No error handling: one bad row crashes the entire run")
    print("2. No idempotency: rerunning inserts duplicate rows")
    print("3. No validation: negative qty, empty names, zero prices accepted")
    print("4. No logging: no way to trace what happened")
    print("5. No separation: extract/transform/load are coupled")
    print("6. No data contracts: schema could change without notice")
    print("7. No lineage: can't trace where data came from")

    db.close()


if __name__ == "__main__":
    main()
