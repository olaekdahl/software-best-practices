#!/usr/bin/env python3
"""
Export the FastAPI app's OpenAPI schema to YAML at api-design/jobs-api.yaml
without running the server.

Usage:
  python scripts/export_openapi.py

Requires: pyyaml (PyYAML). Install with:
  pip install pyyaml fastapi uvicorn pydantic
"""
from __future__ import annotations
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "api-design" / "jobs-api.yaml"


def main() -> int:
    try:
        import yaml  # type: ignore
    except Exception:
        sys.stderr.write("PyYAML is required. Install with: pip install pyyaml\n")
        return 2

    # Import the FastAPI app from app.py
    sys.path.insert(0, str(ROOT))
    try:
        from app import create_app  # type: ignore
    except Exception as e:  # pragma: no cover
        sys.stderr.write(f"Failed to import app: {e}\n")
        return 1

    app = create_app()
    openapi = app.openapi()

    TARGET.parent.mkdir(parents=True, exist_ok=True)
    with TARGET.open("w", encoding="utf-8") as f:
        yaml.safe_dump(openapi, f, sort_keys=False)

    print(f"Wrote {TARGET.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
