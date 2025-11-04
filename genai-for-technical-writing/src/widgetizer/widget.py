"""A tiny, made-up API for demonstrating documentation generation.

Design goals:
- Be small but non-trivial
- Include docstrings and types for API doc generation
- Have clear behavior and examples for README generation
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Mapping, Optional


@dataclass(slots=True)
class Widget:
    """A simple data container representing a widget.

    Attributes:
        name: Human-friendly name of the widget.
        fields: Key/value attributes describing the widget.
        tags: Optional labels for quick grouping/filtering.
    """

    name: str
    fields: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Return a JSON-serializable dictionary representation of the widget."""

        return {"name": self.name, "fields": self.fields, "tags": list(self.tags)}


def render_markdown(widget: Widget) -> str:
    """Render a widget as Markdown.

    Example output:

    # Widget: Cart

    - Tags: checkout, cart
    - Fields:
      - items: 3
      - total: 59.90
    """

    lines: List[str] = [f"# Widget: {widget.name}"]
    if widget.tags:
        lines.append(f"\n- Tags: {', '.join(widget.tags)}")
    if widget.fields:
        lines.append("- Fields:")
        for k, v in widget.fields.items():
            lines.append(f"  - {k}: {v}")
    return "\n".join(lines) + "\n"


def summarize(widgets: Iterable[Widget], *, include_tags: bool = True) -> str:
    """Produce a one-paragraph summary of a widget collection.

    Args:
        widgets: An iterable of Widget objects.
        include_tags: If true, includes distinct tags in the summary.

    Returns:
        A single paragraph suitable for inclusion in README or overview docs.
    """

    widgets_list = list(widgets)
    count = len(widgets_list)
    names = ", ".join(w.name for w in widgets_list[:5])
    tag_part = ""
    if include_tags:
        tags: List[str] = sorted({t for w in widgets_list for t in w.tags})
        if tags:
            tag_part = f" Distinct tags: {', '.join(tags[:8])}."
    return f"This project manages {count} widgets (e.g., {names}).{tag_part}"
