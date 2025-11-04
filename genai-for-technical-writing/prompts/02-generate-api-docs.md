# Prompt: Generate API docs from code and docstrings

Context:

- Code: {{code_files}} <!-- e.g., `src/widgetizer/widget.py`, `src/widgetizer/__init__.py` -->
- Examples: {{examples}} <!-- e.g., `examples/usage.py` -->

Task:

- Produce API documentation for public symbols with:
  - Short summary
  - Parameters and types
  - Returns
  - A minimal usage example for each function/class

Constraints:

- Generate as Markdown with clear subsections per symbol.
- Infer reasonable types where missing.
- Flag any docstring gaps as TODOs (brief and actionable).

Output:

- A single Markdown file suitable for docs/API.md.
