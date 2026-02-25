"""Lightweight data-lineage tracker — stdlib only.

Records **assets** (data files, tables, endpoints) and **transformations**
(processing steps) as a directed acyclic graph (DAG).  Supports:

- Registering assets with metadata (hash, record count, schema).
- Recording transformations that link input assets to output assets.
- Upstream / downstream traversal (root-cause & impact analysis).
- Exporting the full lineage graph to JSON.

Usage:
    from lineage_tracker import LineageTracker, Asset, Transformation

    tracker = LineageTracker()
    src = Asset(name="customers.csv", kind="source", ...)
    tracker.add_asset(src)
    ...
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class Asset:
    """A data artifact participating in the pipeline."""

    name: str
    kind: str  # "source", "derived", "endpoint"
    description: str = ""
    file_path: Optional[str] = None
    format: Optional[str] = None  # "CSV", "JSON", "SQLite", etc.
    record_count: Optional[int] = None
    schema_snapshot: Optional[List[str]] = None  # column names / keys
    sha256: Optional[str] = None
    created_at: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Transformation:
    """A processing step that consumes input assets and produces output assets."""

    name: str
    description: str = ""
    inputs: List[str] = field(default_factory=list)   # asset names
    outputs: List[str] = field(default_factory=list)   # asset names
    script: Optional[str] = None
    timestamp: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Tracker
# ---------------------------------------------------------------------------

class LineageTracker:
    """Maintains a DAG of assets linked by transformations."""

    def __init__(self) -> None:
        self._assets: Dict[str, Asset] = {}
        self._transforms: List[Transformation] = []
        # Adjacency lists
        self._children: Dict[str, Set[str]] = {}   # asset -> downstream assets
        self._parents: Dict[str, Set[str]] = {}     # asset -> upstream assets

    # -- mutations -----------------------------------------------------------

    def add_asset(self, asset: Asset) -> None:
        self._assets[asset.name] = asset
        self._children.setdefault(asset.name, set())
        self._parents.setdefault(asset.name, set())

    def add_transformation(self, txn: Transformation) -> None:
        if txn.timestamp is None:
            txn.timestamp = _now_iso()
        self._transforms.append(txn)
        for inp in txn.inputs:
            self._children.setdefault(inp, set())
            self._parents.setdefault(inp, set())
            for out in txn.outputs:
                self._children[inp].add(out)
                self._children.setdefault(out, set())
                self._parents.setdefault(out, set())
                self._parents[out].add(inp)

    # -- queries -------------------------------------------------------------

    def upstream(self, asset_name: str) -> List[str]:
        """All transitive ancestors (root-cause analysis)."""
        return self._traverse(asset_name, self._parents)

    def downstream(self, asset_name: str) -> List[str]:
        """All transitive descendants (impact analysis)."""
        return self._traverse(asset_name, self._children)

    def roots(self) -> List[str]:
        """Assets with no upstream parents (original sources)."""
        return [n for n, parents in self._parents.items() if not parents]

    def leaves(self) -> List[str]:
        """Assets with no downstream consumers (final outputs)."""
        return [n for n, children in self._children.items() if not children]

    def get_asset(self, name: str) -> Optional[Asset]:
        return self._assets.get(name)

    @property
    def assets(self) -> Dict[str, Asset]:
        return dict(self._assets)

    @property
    def transformations(self) -> List[Transformation]:
        return list(self._transforms)

    # -- export --------------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        return {
            "generated_at": _now_iso(),
            "assets": {n: asdict(a) for n, a in self._assets.items()},
            "transformations": [asdict(t) for t in self._transforms],
            "edges": {n: sorted(ch) for n, ch in self._children.items() if ch},
        }

    def to_json(self, fp: Path, *, indent: int = 2) -> None:
        fp.parent.mkdir(parents=True, exist_ok=True)
        with fp.open("w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=indent)

    # -- display -------------------------------------------------------------

    def print_graph(self) -> None:
        """Pretty-print the lineage graph to stdout."""
        visited: Set[str] = set()

        def _walk(name: str, depth: int = 0) -> None:
            if name in visited:
                return
            visited.add(name)
            asset = self._assets.get(name)
            kind = asset.kind if asset else "?"
            fmt = asset.format or "" if asset else ""
            sha = asset.sha256[:8] + "…" if asset and asset.sha256 else ""
            rec = f"{asset.record_count} records" if asset and asset.record_count is not None else ""
            details = ", ".join(filter(None, [fmt, rec, f"sha256:{sha}" if sha else ""]))
            prefix = "  " * depth
            print(f"{prefix}[{kind}]  {name}  ({details})")

            # Find transformation(s) that produce children
            child_names = sorted(self._children.get(name, set()))
            if child_names:
                txn_label = ""
                for t in self._transforms:
                    if name in t.inputs and any(c in t.outputs for c in child_names):
                        txn_label = t.name
                        break
                arrow = f"transform: {txn_label}" if txn_label else "→"
                print(f"{prefix}   │")
                print(f"{prefix}   ▼  {arrow}")
            for ch in child_names:
                _walk(ch, depth)

        for root in sorted(self.roots()):
            _walk(root)

    def print_impact(self, asset_name: str) -> None:
        """Show everything downstream of a given asset."""
        deps = self.downstream(asset_name)
        print(f"\n=== IMPACT ANALYSIS: what depends on {asset_name}? ===")
        if not deps:
            print("  (nothing)")
            return
        # Classify direct vs indirect
        direct = self._children.get(asset_name, set())
        for d in deps:
            tag = "" if d in direct else " (indirectly)"
            print(f"  → {d}{tag}")

    # -- internals -----------------------------------------------------------

    @staticmethod
    def _traverse(start: str, adj: Dict[str, Set[str]]) -> List[str]:
        result: list[str] = []
        stack = list(adj.get(start, set()))
        seen: set[str] = set()
        while stack:
            node = stack.pop()
            if node in seen:
                continue
            seen.add(node)
            result.append(node)
            stack.extend(adj.get(node, set()))
        return sorted(result)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def file_sha256(fp: Path) -> str:
    """Return hex SHA-256 of a file."""
    h = hashlib.sha256()
    with fp.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def count_csv_rows(fp: Path) -> int:
    """Return number of data rows (excluding header) in a CSV."""
    import csv as _csv

    with fp.open(newline="", encoding="utf-8") as f:
        reader = _csv.reader(f)
        next(reader, None)  # skip header
        return sum(1 for _ in reader)


def csv_columns(fp: Path) -> List[str]:
    """Return column names from the first row of a CSV."""
    import csv as _csv

    with fp.open(newline="", encoding="utf-8") as f:
        reader = _csv.reader(f)
        header = next(reader, None)
        return list(header) if header else []


def json_keys(fp: Path) -> List[str]:
    """Return top-level keys (or keys of the first object in a list)."""
    with fp.open(encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict):
        return sorted(data.keys())
    if isinstance(data, list) and data and isinstance(data[0], dict):
        return sorted(data[0].keys())
    return []


def json_record_count(fp: Path) -> Optional[int]:
    """Return number of records if the file holds a list."""
    with fp.open(encoding="utf-8") as f:
        data = json.load(f)
    return len(data) if isinstance(data, list) else None


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
