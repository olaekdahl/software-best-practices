# Software Diagramming, Technical Writing, and Knowledge Sharing - Demos

Progressive demos from basic diagrams to full docs-as-code pipelines. Demos use native file formats (`.puml`, `.mmd`, `.md`, `.yaml`, `.yml`) so instructors can demonstrate how these tools are normally used in practice.

| Demo | Topic | File Formats | Complexity |
|------|-------|-------------|-----------|
| demo01_basic_diagrams | PlantUML and Mermaid basics | `.puml`, `.mmd` | Foundational |
| demo02_c4_model | C4 model (Context, Container, Component, Deployment) | `.puml`, `.mmd` | Intermediate |
| demo03_technical_writing | BLUF, ADRs, README, runbook, postmortem | `.md` | Intermediate |
| demo04_docs_as_code | Full docs-as-code pipeline with CI | `.md`, `.yaml`, `.yml`, `.json`, `.py` | Advanced |
| demo05_living_documentation | Auto-generated docs from code | `.py`, `.md`, `.mmd` | Real-world |

## Prerequisites

- **PlantUML preview:** VS Code extension `jebbs.plantuml` (requires Java)
- **Mermaid preview:** VS Code extension or GitHub/GitLab native rendering
- **Python 3.11+:** Only needed for demo04 (linter) and demo05 (doc generator)
- **Optional CLI tools:** `markdownlint-cli`, `cspell`, `@stoplight/spectral-cli`

## How to Use

### Demos 01-03: Open files directly

```bash
# Open diagram files in VS Code with preview extensions
code demo01_basic_diagrams/sequence-order-flow.puml

# Open markdown files to review writing templates
code demo03_technical_writing/adr-0001-use-postgresql.md
```

### Demo 04: Run the doc linter

```bash
cd demo04_docs_as_code
python lint_docs.py docs/
```

### Demo 05: Generate living documentation

```bash
cd demo05_living_documentation
python generate_docs.py
# Generated files appear in output/
```
