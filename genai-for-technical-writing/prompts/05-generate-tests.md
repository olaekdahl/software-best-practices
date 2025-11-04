# Prompt: Generate minimal tests from examples

Context:

- Code: {{code_files}} <!-- e.g., `src/widgetizer/widget.py` -->
- Examples: {{examples}} <!-- e.g., `examples/usage.py` -->

Task:

- Write lightweight unit tests covering:
  - Happy path for `render_markdown`
  - Happy path and a tags-disabled variant for `summarize`
- Use plain `pytest`; no external dependencies.

Constraints:

- Keep tests small and fast.
- Make assertions specific and readable.

Output:

- A `pytest`-style test module as Markdown code fences (or a Python file if requested).
