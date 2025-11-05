# Software Best Practices

A practical, runnable collection of patterns, diagrams, and a tiny FastAPI “Jobs API” to teach and demo software best practices.

## Quickstart

Prereqs → Install → Run → Verify

- Prerequisites
  - Python 3.10+
  - Node.js (optional, for Redocly CLI to lint/build API docs)

- Install
  ```bash
  pip install -r requirements.txt
  ```

- Run the app (hot reload)
  ```bash
  uvicorn app:app --reload
  # App listens on http://127.0.0.1:8000 by default
  ```
  Note: Running `python app.py` also works, but using the import string (`uvicorn app:app --reload`) avoids a uvicorn reload warning.

- Verify the API
  ```bash
  # Submit a job (idempotent via Idempotency-Key)
  curl -s -X POST 'http://127.0.0.1:8000/jobs' \
    -H 'Authorization: Bearer test' \
    -H 'Idempotency-Key: 123' \
    -H 'Content-Type: application/json' \
    -d '{"dataset":"demo","model":"baseline"}' | jq

  # Repeat the same request returns 200 with the same job id
  curl -s -X POST 'http://127.0.0.1:8000/jobs' \
    -H 'Authorization: Bearer test' -H 'Idempotency-Key: 123' \
    -H 'Content-Type: application/json' \
    -d '{"dataset":"demo","model":"baseline"}' | jq

  # Get the job (replace <id> with returned id)
  curl -s 'http://127.0.0.1:8000/jobs/<id>' -H 'Authorization: Bearer test' | jq

  # Explore docs
  open http://127.0.0.1:8000/docs          # Swagger UI
  curl -s http://127.0.0.1:8000/openapi.yaml | head
  ```

- Generate and view Redoc docs
  ```bash
  # Export OpenAPI YAML (no server required)
  python3 scripts/export_openapi.py

  # Lint the spec (Node optional)
  npx @redocly/cli lint api-design/jobs-api.yaml

  # View with the CDN-based page
  (cd api-design && python3 -m http.server 8080)
  # then browse http://localhost:8080/redoc.html

  # Or build a single-file HTML doc
  npx @redocly/cli build-docs api-design/jobs-api.yaml -o api-design/jobs-api.html
  ```

## Configuration

- App host/port
  - Defaults: 127.0.0.1:8000 (see `app.py`)
  - Override via uvicorn if needed:
    ```bash
    uvicorn app:app --host 0.0.0.0 --port 8000 --reload
    ```

- Auth
  - Endpoints require an HTTP Bearer token (demo only; any token is accepted)
  - Example header: `Authorization: Bearer test`

- Idempotency
  - POST /jobs requires header `Idempotency-Key: <string>`
  - First call → 201 Created; repeats → 200 with the same job id

## Develop

- Hot reload
  - `python app.py` starts uvicorn with `reload=True`

- Lint API description
  ```bash
  npx @redocly/cli lint api-design/jobs-api.yaml
  ```

- Diagramming helpers
  - C4 PlantUML and Mermaid examples under `software-diagramming/`
  - Generate simple Mermaid from code: `python scripts/gen_mermaid.py`

## Architecture

- C4 L2 (Containers) examples:
  - `software-diagramming/c4-container.puml`
  - `software-diagramming/webapp-flow-c4.puml`

- Other C4 levels:
  - Context: `software-diagramming/c4-context.puml`
  - Component: `software-diagramming/c4-component.puml`
  - Code: `software-diagramming/c4-code.puml`

- ADRs (MADR):
  - Index: [`docs/adr/`](docs/adr/README.md)
  - [ADR 0001: Adopt FastAPI and Redocly for API and Docs](docs/adr/0001-adopt-fastapi-and-redocly.md)
  - [ADR 0002: Adopt Idempotency-Key header for POST /jobs](docs/adr/0002-adopt-idempotency-key-header.md)

## Operations

- Runbook
  - Start: `python app.py` (or `uvicorn app:app --reload`)
  - Smoke check: `curl -s http://127.0.0.1:8000/openapi.json | jq .info`
  - Docs: Swagger UI at `/docs`, Redoc via `api-design/redoc.html`

- SLOs / Alerts / Dashboards
  - Not defined (sample app). Add HTTP availability and latency SLIs if promoted beyond a demo.

## Contributing

- Branching
  - Create feature branches from `main`; open small, focused PRs

- PR checks (suggested)
  - Export and lint OpenAPI: `python scripts/export_openapi.py && npx @redocly/cli lint api-design/jobs-api.yaml`
  - Keep diagrams in-sync; commit generated files under `software-diagramming/generated/` as needed

- Code style
  - Python 3.10+, type hints encouraged
  - Keep docs skimmable; prefer small diagrams and link to details
