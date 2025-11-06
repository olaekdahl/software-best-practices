"""Ingest from multiple sources (CSV, JSON, SQLite), clean, and prepare outputs.

Run:
  python3 data-engineering-and-ml-pipelines/ingestion-and-transformation/ingest_transform.py
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import csv
import json
import sqlite3
from typing import Dict, List, Tuple


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
OUT = ROOT / "output"
OUT.mkdir(parents=True, exist_ok=True)


@dataclass
class Customer:
    customer_id: str
    name: str
    email: str
    region: str | None = None


def read_customers_csv(fp: Path) -> List[Customer]:
    customers: Dict[str, Customer] = {}
    with fp.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cid = str(row.get("customer_id", "")).strip()
            if not cid:
                continue
            name = (row.get("name") or "").strip().title()
            email = (row.get("email") or "unknown@example.com").strip().lower()
            # Deduplicate by first seen customer_id
            if cid not in customers:
                customers[cid] = Customer(customer_id=cid, name=name, email=email)
    return list(customers.values())


def read_orders_json(fp: Path) -> List[Tuple[str, float]]:
    orders = []
    with fp.open(encoding="utf-8") as f:
        data = json.load(f)
        for row in data:
            cid = str(row.get("customer_id", "")).strip()
            amount = float(row.get("amount", 0) or 0)
            if cid:
                orders.append((cid, amount))
    return orders


def read_regions_sqlite() -> Dict[str, str]:
    """Simulate a database source with a small in-memory table."""
    conn = sqlite3.connect(":memory:")
    cur = conn.cursor()
    cur.execute("create table regions (customer_id text primary key, region text)")
    cur.executemany(
        "insert into regions(customer_id, region) values(?, ?)",
        [
            ("1", "NA"),
            ("2", "EU"),
        ],
    )
    regions: Dict[str, str] = {}
    for cid, region in cur.execute("select customer_id, region from regions"):
        regions[str(cid)] = str(region)
    conn.close()
    return regions


def summarize_orders(orders: List[Tuple[str, float]]) -> Dict[str, Tuple[int, float]]:
    summary: Dict[str, Tuple[int, float]] = {}
    for cid, amount in orders:
        count, total = summary.get(cid, (0, 0.0))
        summary[cid] = (count + 1, total + float(amount))
    return summary


def write_csv(fp: Path, rows: List[Dict[str, object]], fieldnames: List[str]) -> None:
    with fp.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    customers_csv = DATA / "customers.csv"
    orders_json = DATA / "orders.json"
    if not customers_csv.exists() or not orders_json.exists():
        raise SystemExit("Missing input files. Ensure data/ contains customers.csv and orders.json")

    customers = read_customers_csv(customers_csv)
    orders = read_orders_json(orders_json)
    regions = read_regions_sqlite()

    # Attach regions
    for c in customers:
        c.region = regions.get(c.customer_id)

    # Prepare cleaned customers
    cleaned_rows = [
        {"customer_id": c.customer_id, "name": c.name, "email": c.email, "region": c.region or "UNK"}
        for c in customers
    ]
    write_csv(OUT / "cleaned_customers.csv", cleaned_rows, ["customer_id", "name", "email", "region"])

    # Prepare order summary
    s = summarize_orders(orders)
    summary_rows = [
        {"customer_id": cid, "order_count": cnt, "total_amount": round(total, 2)}
        for cid, (cnt, total) in sorted(s.items())
    ]
    write_csv(OUT / "customer_order_summary.csv", summary_rows, ["customer_id", "order_count", "total_amount"])

    print(f"Wrote {len(cleaned_rows)} customers → {OUT/'cleaned_customers.csv'}")
    print(f"Wrote {len(summary_rows)} customer summaries → {OUT/'customer_order_summary.csv'}")


if __name__ == "__main__":
    main()
