from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PKG_INIT = ROOT / "genai-for-technical-writing" / "src" / "widgetizer" / "__init__.py"
SNAP = Path(__file__).resolve().parent / "snapshots" / "widget_cart.md"

spec = importlib.util.spec_from_file_location("widgetizer", PKG_INIT)
assert spec and spec.loader, "Could not load local widgetizer package."
widgetizer = importlib.util.module_from_spec(spec)
sys.modules["widgetizer"] = widgetizer
spec.loader.exec_module(widgetizer)  # type: ignore[attr-defined]


def test_widget_markdown_snapshot_matches():
    Widget = widgetizer.Widget
    render_markdown = widgetizer.render_markdown

    cart = Widget(name="Cart", fields={"items": 2, "total": 20.0}, tags=["checkout"]) 
    md = render_markdown(cart)

    expected = SNAP.read_text(encoding="utf-8")
    assert md == expected, f"Markdown changed.\n--- expected:\n{expected}\n--- actual:\n{md}"
