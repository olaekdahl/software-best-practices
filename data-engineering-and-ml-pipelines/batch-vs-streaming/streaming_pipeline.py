"""Streaming pipeline demo (simulated): processes events with low latency.

Reads JSON Lines events and maintains rolling metrics. Writes a metrics file
after each event to simulate near-real-time outputs.

Run:
  python3 data-engineering-and-ml-pipelines/batch-vs-streaming/streaming_pipeline.py
"""

from __future__ import annotations

from pathlib import Path
import json
import time
from datetime import datetime, timezone


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "events.jsonl"
OUT = ROOT / "output"
OUT.mkdir(parents=True, exist_ok=True)


def write_metrics(metrics_fp: Path, state: dict) -> None:
    dt = datetime.now(timezone.utc)
    state_out = {**state, "updated_at": dt.isoformat().replace("+00:00", "Z")}
    with metrics_fp.open("w", encoding="utf-8") as f:
        json.dump(state_out, f, indent=2)


def main() -> None:
    if not DATA.exists():
        raise SystemExit("Missing events data file. See data/events.jsonl")

    state = {
        "event_count": 0,
        "orders": 0,
        "refunds": 0,
        "revenue": 0.0,
        "last_event": None,
    }

    metrics_fp = OUT / "streaming_metrics.json"
    with DATA.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            evt = json.loads(line)
            etype = evt.get("event_type")
            amt = float(evt.get("amount", 0) or 0)
            state["event_count"] += 1
            state["last_event"] = etype
            if etype == "order_placed":
                state["orders"] += 1
                state["revenue"] += amt
            elif etype == "order_refund":
                state["refunds"] += 1
                state["revenue"] += amt  # negative amount

            write_metrics(metrics_fp, state)
            print(f"Processed {etype}: revenue={state['revenue']:.2f}")
            time.sleep(0.4)  # Simulate streaming arrival

    print(f"Final metrics written → {metrics_fp}")


if __name__ == "__main__":
    main()
