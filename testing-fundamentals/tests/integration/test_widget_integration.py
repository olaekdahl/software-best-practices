from __future__ import annotations

"""Integration test: use widgetizer API (from another folder) end-to-end.

This imports the local widgetizer package without installing it, similar to
examples/usage.py in the repo.
"""

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PKG_INIT = ROOT / "genai-for-technical-writing" / "src" / "widgetizer" / "__init__.py"

spec = importlib.util.spec_from_file_location("widgetizer", PKG_INIT)
assert spec and spec.loader, "Could not load local widgetizer package."
widgetizer = importlib.util.module_from_spec(spec)
sys.modules["widgetizer"] = widgetizer
spec.loader.exec_module(widgetizer)  # type: ignore[attr-defined]


def test_widgetizer_roundtrip():
    Widget = widgetizer.Widget
    render_markdown = widgetizer.render_markdown
    summarize = widgetizer.summarize

    cart = Widget(name="Cart", fields={"items": 2, "total": 20.0}, tags=["checkout"]) 
    md = render_markdown(cart)
    assert "# Widget: Cart" in md
    assert "items: 2" in md

    s = summarize([cart])
    assert "manages 1 widgets" in s
