# REST vs GraphQL

This demo shows the same simple domain (books) exposed via:

- REST endpoints under `/rest/...`
- A GraphQL endpoint at `/graphql`

Frameworks used: FastAPI (REST) and Strawberry GraphQL (GraphQL), served by Uvicorn.

## Run

```bash
# Install deps once (from repo root)
pip install -r requirements.txt

# Run (either form works)
cd api-design/rest-graphql-demo
python3 server.py                       # runs uvicorn programmatically
# or
uvicorn server:app --reload --port 9000

# Server listens on http://localhost:9000
```

## Try REST

List books:

```bash
curl http://localhost:9000/rest/books
```

Get one book:

```bash
curl http://localhost:9000/rest/books/1
```

Create a book:

```bash
curl -X POST http://localhost:9000/rest/books \
  -H "Content-Type: application/json" \
  -d '{"title":"Refactoring","author":"Martin Fowler"}'
```

## Try GraphQL

Interactive GraphiQL is available in the browser at:

- http://localhost:9000/graphql

Query all books:

```bash
curl -X POST http://localhost:9000/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"{ books { id title author } }"}'
```

Query one book by id:

```bash
curl -X POST http://localhost:9000/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"{ book(id: \"1\") { id title author } }"}'
```

Mutation (add a book):

```bash
curl -X POST http://localhost:9000/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"mutation { addBook(title: \"Refactoring\", author: \"Martin Fowler\") { id title author } }"}'
```

## Design files

- `rest_openapi.yaml` — OpenAPI 3.1 description of the REST surface
- `graphql_schema.graphql` — GraphQL SDL schema for the same domain
