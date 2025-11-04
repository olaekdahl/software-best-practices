"""Widgetizer: tiny demo module for doc generation.

Provides a small API for creating, rendering, and summarizing widgets.
"""

from .widget import Widget, render_markdown, summarize

__all__ = ["Widget", "render_markdown", "summarize"]
