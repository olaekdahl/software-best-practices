# Demo 04 - Docs-as-Code Pipeline

## Purpose

Demonstrate a complete docs-as-code workflow where documentation is treated with the same rigor as source code: linted, spell-checked, link-validated, and gated in CI. This demo is structured as a realistic project directory.

## Instructor Notes

- Walk through the project structure to show how docs live alongside code
- Run the Python linter against the sample docs to show it catching real issues
- Open the CI workflow and explain each stage of the docs pipeline
- Show the OpenAPI spec and explain how it can be validated with Spectral
- Open the markdownlint config and discuss which rules to enable/disable for your team
- Point out the cspell config with the custom tech dictionary

## Files

| File | Format | What It Demonstrates |
|------|--------|---------------------|
| `docs/getting-started.md` | Markdown | A clean getting-started guide (passes all lint rules) |
| `docs/api-guide.md` | Markdown | Intentionally has lint issues - used to demo the linter |
| `docs/troubleshooting.md` | Markdown | A well-structured troubleshooting guide |
| `openapi.yaml` | OpenAPI 3.0 | API specification for validation with Spectral |
| `.github/workflows/docs-ci.yml` | GitHub Actions | CI pipeline that lints, spell-checks, and validates docs |
| `.markdownlint.yml` | YAML | Markdownlint configuration with rule customization |
| `cspell.json` | JSON | Spell checker config with custom tech dictionary |
| `lint_docs.py` | Python | A simple custom doc linter (demonstrates the concept) |

## How to Demo

### 1. Run the custom linter

```bash
python lint_docs.py docs/
```

This will show issues in `docs/api-guide.md` (intentional problems) and a clean report for the other files.

### 2. Run markdownlint

```bash
# Install
npm install -g markdownlint-cli

# Lint all docs
markdownlint 'docs/**/*.md'
```

### 3. Validate OpenAPI spec

```bash
# Install Spectral
npm install -g @stoplight/spectral-cli

# Validate
spectral lint openapi.yaml
```

### 4. Spell check

```bash
# Install cspell
npm install -g cspell

# Check docs
cspell 'docs/**/*.md'
```

## Key Takeaways

1. **Docs live in the repo** - same PR, same review, same CI
2. **Lint docs like code** - markdownlint for formatting, cspell for spelling
3. **Validate API specs** - Spectral catches breaking changes and style violations
4. **Check links** - lychee or markdown-link-check catches broken links
5. **Automate in CI** - every PR touching docs gets validated
6. **Custom dictionaries** - add your tech terms so spell check does not flag them
