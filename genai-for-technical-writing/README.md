# GenAI for Technical Writing

This folder contains a tiny, made-up project and a set of prompt templates you can use to generate documentation with an LLM (e.g., GitHub Copilot Chat). It includes:

- A small example module (`src/widgetizer`) with docstrings
- A few seed docs under `docs/`
- Focused prompt templates under `prompts/`
- A usage guide for GitHub Copilot (`github-copilot-instructions.md`)

## Quick start

- Explore `src/widgetizer/` and `examples/usage.py`.
- Open `prompts/` and pick a prompt (e.g., `01-generate-readme.md`).
- Paste a prompt into your LLM and follow the variables/placeholders.

## Suggested flow

1. Generate a project README from code and seeds.
2. Generate API docs from docstrings and type hints.
3. Generate a lightweight architecture doc and diagram.
4. Generate a changelog or release notes from git history (optional).

See `github-copilot-instructions.md` for tips on running prompts effectively in VS Code.