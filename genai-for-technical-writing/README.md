# Widgetizer

A tiny Python library and example used to demo AI‑assisted technical writing. Widgetizer turns small, typed objects into readable Markdown and summaries. It exists to give writers and engineers a compact, realistic target for prompt‑driven docs.

## Quick start

Install nothing. Run the example and see output:

```bash
python3 genai-for-technical-writing/examples/usage.py
```

Minimal usage in code:

```python
from widgetizer import Widget, render_markdown, summarize

cart = Widget(name="Cart", fields={"items": 3, "total": 59.90}, tags=["checkout", "cart"])
print(render_markdown(cart))
print(summarize([cart]))
```

## How it’s built

- Core dataclass: `Widget` (name, fields, tags)
- Render: `render_markdown(widget) -> str`
- Summarize: `summarize(widgets, include_tags=True) -> str`

These live in `src/widgetizer/`. Seeds in `docs/` describe purpose and architecture; `examples/usage.py` shows a runnable flow.

## Data flow

```mermaid
flowchart LR
	A[Input data\n(name, fields, tags)] --> B[Widget]
	B --> C[render_markdown]
	C --> D[Markdown]
	B -. collection .-> E[summarize]
	E --> F[One‑paragraph summary]
```

## Run the example

From the repo root:

```bash
python3 genai-for-technical-writing/examples/usage.py
```

You’ll see a Markdown rendering of a widget and a short collection summary.

## Generate docs with the prompts

Prompts live in `genai-for-technical-writing/prompts/`:

- `01-generate-readme.md`: build this README from code and seeds
- `02-generate-api-docs.md`: produce API docs from types and docstrings
- `03-generate-architecture-diagram.md`: create a diagram and short notes
- `04-generate-changelog.md`, `05-generate-tests.md`: optional extras

Suggested workflow:
1) Open a prompt, fill the variables (code path, seeds, examples).
2) Paste into your LLM (e.g., GitHub Copilot Chat in VS Code).
3) Review and commit the generated docs.

See `docs/overview.md` and `docs/architecture.md` for seed context and `github-copilot-instructions.md` for tips.