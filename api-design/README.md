# API Design: Redoc example

This folder includes a minimal ReDoc setup to render API docs from the local OpenAPI spec `jobs-api.yaml`.

## View locally (quickest)

Open a terminal in this folder and serve it over HTTP:

```bash
# from repo root
cd api-design
python3 -m http.server 8080
# then browse http://localhost:8080/redoc.html
```

Notes:

- Serving over HTTP avoids CORS issues that can happen with file:// URLs.
- The page `redoc.html` loads ReDoc from a CDN and points to `./jobs-api.yaml`.

## Lint the OpenAPI spec

Use Redocly CLI to validate the spec before building docs:

```bash
# From repo root
npx @redocly/cli lint api-design/jobs-api.yaml

# Or from inside this folder
npx @redocly/cli lint jobs-api.yaml
```

Note: You may see a Node.js version warning from the CLI, linting still runs as long as the command executes.

## Generate jobs-api.yaml from the FastAPI app

You can export the OpenAPI schema directly from the sample FastAPI app without running a server:

```bash
# Install deps (once)
pip install -r requirements.txt

# Generate api-design/jobs-api.yaml from the app
python scripts/export_openapi.py

# Validate the generated spec
npx @redocly/cli lint api-design/jobs-api.yaml
```

Alternatively, run the app and fetch the schema:

```bash
# Start the app (in another terminal)
python app.py

# Save JSON then convert to YAML
curl -s http://127.0.0.1:8000/openapi.json -o api-design/jobs-api.json
npx @redocly/cli bundle api-design/jobs-api.json -o api-design/jobs-api.yaml
```

## Alternative: Generate a static HTML file with `redoc-cli`

If you prefer a single self-contained HTML file, you can use `redoc-cli`:

```bash
# Requires Node.js
npx @redocly/cli build-docs jobs-api.yaml -o jobs-api.html
```

Open `jobs-api.html` in your browser (or serve it as above).

## Troubleshooting

- If the UI shows an error, validate the spec with an online OpenAPI validator or a linter.
- If the spec path changes, update the `spec-url` in `redoc.html`.

## Bonus: REST vs GraphQL tiny demo (no deps)

A self-contained comparison lives in `rest-graphql-demo/`:

- `server.py` — minimal HTTP server exposing both REST (`/rest/...`) and GraphQL (`/graphql`)
- `rest_openapi.yaml` — OpenAPI description of the REST surface
- `graphql_schema.graphql` — GraphQL SDL for the same domain

Run it:

```bash
cd api-design/rest-graphql-demo
python3 server.py
# visit http://localhost:9000
```
