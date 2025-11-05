---
status: "accepted"
date: 2025-11-04
decision-makers: [Team]
consulted: []
informed: []
---

# ADR 0001: Adopt FastAPI and Redocly for API and Docs

## Context and Problem Statement

We need a small, runnable API and a maintainable way to generate and publish API documentation for this repository’s teaching examples. The solution should:

- Be simple enough for newcomers to run locally
- Produce a clean OpenAPI 3.1 schema
- Support idempotency and basic auth examples
- Render docs locally and as a single-file artifact for static hosting

## Decision Drivers

- Developer experience and approachability
- Standards compliance (OpenAPI 3.1)
- Clear, attractive docs with minimal tooling
- Works on Linux/macOS/Windows without heavyweight dependencies

## Considered Options

1. FastAPI + Pydantic v2 + Redocly CLI (ReDoc)
2. Flask (+ Flask-Smorest) + Redocly CLI
3. Django REST Framework + drf-spectacular + Redocly CLI
4. Hand-written OpenAPI YAML + CDN ReDoc only

## Decision Outcome

Chosen option: "FastAPI + Pydantic v2 + Redocly CLI", because FastAPI natively generates OpenAPI schemas from type hints; Pydantic v2 produces modern, accurate JSON Schema; and Redocly CLI provides both local linting and a single self-contained HTML build. This hits our needs with minimal boilerplate and a great DX.

### Consequences

* Good, because very fast local startup and hot reload
* Good, because accurate OpenAPI 3.1 generation from code + models
* Good, because easy to lint and produce a standalone HTML (`build-docs`) for static hosting
* Good, because Swagger UI (/docs) and OpenAPI JSON/YAML routes out of the box
* Bad, because requires Python 3.10+ and Node.js for Redocly CLI (optional)
* Bad, because some duplication in security naming if both FastAPI and custom OpenAPI tweaks are used (can be reconciled later)

### Confirmation

* Redocly CLI lint passes on the generated spec (`npx @redocly/cli lint api-design/jobs-api.yaml`).
* Static docs build succeeds (`npx @redocly/cli build-docs …`).
* Swagger UI serves at `/docs` and `/openapi.json` responds 200.

## Pros and Cons of the Options

### 1. FastAPI + Pydantic v2 + Redocly CLI
- Pros:
  - Best-in-class DX, async-ready, type-driven schema
  - Minimal code to get OpenAPI, Swagger UI, and docs
  - Redocly CLI adds lint + one-file HTML builds
- Cons:
  - Another runtime (Node) for Redocly CLI (optional)

### 2. Flask (+ Flask-Smorest) + Redocly CLI
- Pros:
  - Familiar, very lightweight
  - Flask-Smorest emits OpenAPI 3.x
- Cons:
  - More scaffolding than FastAPI to reach parity
  - Async support is add-on compared to FastAPI’s design

### 3. Django REST Framework + drf-spectacular + Redocly CLI
- Pros:
  - Rich ecosystem; spectacular generates high-quality schemas
- Cons:
  - Heavyweight for a tiny teaching repo; setup overhead

### 4. Hand-written OpenAPI YAML + CDN ReDoc only
- Pros:
  - Zero app runtime dependency
  - Works entirely from static files
- Cons:
  - Easy to drift out of sync with code
  - No generated server stubs or live examples

## More Information

Implementation: `app.py`

Spec export: `scripts/export_openapi.py`

Docs: `api-design/README.md` and `api-design/redoc.html`

Lint/build: `npx @redocly/cli lint|build-docs`

