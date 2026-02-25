# Demo 05 - Living Documentation: Auto-Generated from Code

## Purpose

Demonstrate how documentation can be generated directly from source code, keeping docs and code always in sync. This demo includes a Python script that extracts documentation from type hints, docstrings, and code structure, plus sample outputs showing what it produces.

## Instructor Notes

- Start by showing `order_domain.py` - this is the "source of truth"
- Then run `generate_docs.py` to generate the API reference and state diagram
- Compare the generated output with the source to show how they stay in sync
- Open the generated Mermaid state diagram to show how transitions map to code
- Discuss when to use auto-generated docs vs. hand-written docs
- Show the conventional commit changelog example

## Files

| File | Format | What It Demonstrates |
|------|--------|---------------------|
| `order_domain.py` | Python | Source code with rich docstrings and type hints (the "source of truth") |
| `generate_docs.py` | Python | Introspection script that extracts docs from Python source |
| `output/api-reference.md` | Markdown | Auto-generated API reference from docstrings |
| `output/order-states.mmd` | Mermaid | Auto-generated state diagram from transition annotations |
| `output/changelog.md` | Markdown | Auto-generated changelog from conventional commits |
| `adr-template.md` | Markdown | Blank ADR template for the team to copy |
| `conventional-commits.md` | Markdown | Reference guide for the conventional commits format |

## How to Demo

```bash
# Generate documentation from source code
python generate_docs.py

# View the generated files
cat output/api-reference.md
cat output/order-states.mmd
cat output/changelog.md
```

## Key Takeaways

1. **Docs from source** - Docstrings serve double duty: IDE help and generated docs
2. **State diagrams from code** - Transition annotations generate accurate diagrams
3. **Changelogs from commits** - Conventional commits enable automated changelogs
4. **CI generates on merge** - Every PR produces fresh documentation
5. **Reduces manual maintenance** - Focus writing effort on guides, not API references
6. **Not everything should be auto-generated** - Tutorials, ADRs, and runbooks need human authoring
