# Technical Writing and Knowledge Sharing

Templates, tools, and demos for effective technical communication.

## What's inside

### Vale linting (`vale-example/`)

A full Vale configuration for prose linting with Google, Microsoft, and write-good style rules. Includes sample docs and ADR templates.

```bash
# Install Vale (macOS)
brew install vale

# Lint docs
cd technical-writing-and-knowledge-sharing/vale-example
vale docs/
```

## Additional demos

### `writing-templates/` — Writing Templates

Practical templates for common engineering documents:

- **BLUF communication** — Bottom Line Up Front writing style
- **ADR (Architecture Decision Records)** — Two real ADR examples
- **Project README template** — Structured README for new projects
- **Runbook** — Operational runbook for high error rate incidents
- **Incident report** — Blameless postmortem template
- **API changelog** — Versioned changelog format

```bash
# Browse templates
ls technical-writing-and-knowledge-sharing/writing-templates/
```

### `docs-as-code/` — Docs-as-Code Pipeline

A full docs-as-code pipeline with CI integration:

- `lint_docs.py` — Custom Python doc linter
- `docs/` — Sample documentation (getting started, API guide, contributing)
- `openapi.yaml` — OpenAPI spec for Spectral linting
- `.markdownlint.yml` / `cspell.json` — Markdown and spelling config
- `.github/workflows/docs-ci.yml` — CI workflow for doc quality

```bash
cd technical-writing-and-knowledge-sharing/docs-as-code
python lint_docs.py docs/
```

### `living-documentation/` — Auto-Generated Documentation

Generate living documentation from code:

- `order_domain.py` — Domain model with rich docstrings
- `generate_docs.py` — Doc generator that extracts docs from code
- `output/` — Pre-generated markdown and Mermaid outputs
- `adr-template.md` / `conventional-commits.md` — Additional templates

```bash
cd technical-writing-and-knowledge-sharing/living-documentation
python generate_docs.py
# Generated files appear in output/
```
