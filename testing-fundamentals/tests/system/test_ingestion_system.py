from __future__ import annotations

import os
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
SCRIPT = REPO_ROOT / "data-engineering-and-ml-pipelines" / "ingestion-and-transformation" / "ingest_transform.py"
OUT_DIR = REPO_ROOT / "data-engineering-and-ml-pipelines" / "ingestion-and-transformation" / "output"


def test_ingestion_script_end_to_end():
    if not SCRIPT.exists():
        # Skip gracefully if the demo was not added
        import pytest

        pytest.skip("ingestion demo not present")

    # Run the script
    proc = subprocess.run(["python3", str(SCRIPT)], cwd=str(REPO_ROOT), capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr

    cleaned = OUT_DIR / "cleaned_customers.csv"
    summary = OUT_DIR / "customer_order_summary.csv"
    assert cleaned.exists()
    assert summary.exists()

    # Validate non-empty outputs
    assert cleaned.read_text(encoding="utf-8").strip() != ""
    assert summary.read_text(encoding="utf-8").strip().splitlines()[-1]
