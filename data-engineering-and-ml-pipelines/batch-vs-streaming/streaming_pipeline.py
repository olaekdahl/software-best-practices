"""Streaming pipeline demo (simulated): processes events with low latency.

Now supports a simple directory watch mode:
1) Processes the initial `data/events.jsonl` if present.
2) Then continuously watches the `data/` folder for any new `*.jsonl` files,
     processing each file in full as it appears.
3) Keeps running until Ctrl+C.

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
from typing import Dict, Iterable, Set
import argparse


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
DATA = DATA_DIR / "events.jsonl"
OUT = ROOT / "output"
OUT.mkdir(parents=True, exist_ok=True)


def write_metrics(metrics_fp: Path, state: Dict) -> None:
    dt = datetime.now(timezone.utc)
    state_out = {**state, "updated_at": dt.isoformat().replace("+00:00", "Z")}
    with metrics_fp.open("w", encoding="utf-8") as f:
        json.dump(state_out, f, indent=2)


def process_events_file(fp: Path, state: Dict, metrics_fp: Path, per_event_delay: float = 0.4) -> None:
    """Read a JSONL file and update rolling metrics.

    Each line should be a JSON object with keys like `event_type` and `amount`.
    """
    print(f"[stream] Processing file: {fp.name}")
    with fp.open(encoding="utf-8") as f:
        for lineno, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                evt = json.loads(line)
            except json.JSONDecodeError as e:
                print(f"[warn] {fp.name}:{lineno} JSON decode error: {e}")
                continue

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
            time.sleep(per_event_delay)  # Simulate streaming arrival


def discover_jsonl_files(dirpath: Path, pattern: str) -> Iterable[Path]:
    return sorted(p for p in dirpath.glob(pattern) if p.is_file())


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Process an initial JSONL file, then watch a directory for new JSONL files "
            "and process them until interrupted."
        )
    )
    parser.add_argument(
        "--watch-dir",
        type=Path,
        default=DATA_DIR,
        help="Directory to watch for new files (default: data/ next to this script)",
    )
    parser.add_argument(
        "--poll-interval",
        type=float,
        default=1.0,
        help="Polling interval in seconds (default: 1.0)",
    )
    parser.add_argument(
        "--pattern",
        type=str,
        default="*.jsonl",
        help="Glob pattern for files to process (default: *.jsonl)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    watch_dir: Path = args.watch_dir.resolve()
    poll_interval: float = float(args.poll_interval)
    pattern: str = str(args.pattern)

    watch_dir.mkdir(parents=True, exist_ok=True)

    state: Dict = {
        "event_count": 0,
        "orders": 0,
        "refunds": 0,
        "revenue": 0.0,
        "last_event": None,
    }

    metrics_fp = OUT / "streaming_metrics.json"

    # 1) Process initial events.jsonl if present
    processed: Set[str] = set()
    initial_file = watch_dir / "events.jsonl"
    if initial_file.exists():
        process_events_file(initial_file, state, metrics_fp)
        processed.add(initial_file.resolve().name)
    else:
        print("[info] No initial data/events.jsonl found. Waiting for new files…")

    # 2) Watch the data directory for new .jsonl files
    print(
        f"[watch] Watching {watch_dir} for new files matching '{pattern}'. Press Ctrl+C to stop."
    )

    try:
        # Track sizes to avoid processing files that are still being written
        last_sizes: Dict[str, int] = {}
        while True:
            candidates = list(discover_jsonl_files(watch_dir, pattern))
            for fp in candidates:
                name = fp.resolve().name
                if name in processed:
                    continue

                try:
                    size = fp.stat().st_size
                except FileNotFoundError:
                    continue  # transient

                # size stable check across two polls
                prev = last_sizes.get(name)
                if prev is None:
                    last_sizes[name] = size
                    continue  # observe it once, confirm on next pass

                if prev != size:
                    last_sizes[name] = size
                    continue  # still growing

                # size stable, process
                process_events_file(fp, state, metrics_fp)
                processed.add(name)
                last_sizes.pop(name, None)

            time.sleep(poll_interval)
    except KeyboardInterrupt:
        print("\n[watch] Stopping. Final metrics at:", metrics_fp)


if __name__ == "__main__":
    main()
