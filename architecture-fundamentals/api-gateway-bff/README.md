# API Gateway + BFF (Kong + Python/FastAPI)

This is a tiny, runnable demo of the pattern shown in the diagram: a Kong API Gateway in front of two BFFs (Web and Mobile), which call three domain services (Cart, Catalog, Checkout).

``` mermaid
%%{init: {"theme": "default", "themeVariables": {
  "fontFamily": "Arial",
  "primaryBorderColor": "#34495E",
  "primaryColor": "#ECF0F1",
  "edgeLabelBackground":"#ffffff",
  "lineColor": "#34495E"
}}}%%
flowchart TD
    title["**API Gateway and BFF pattern**"]

    Mobile["Mobile App"]
    Web["Web App"]
    GW["API Gateway"]
    BFF_M["BFF (Mobile)"]
    BFF_W["BFF (Web)"]
    S1["Domain Service: Catalog"]
    S2["Domain Service: Cart"]
    S3["Domain Service: Checkout"]

    Mobile -->|HTTPS| GW
    Web -->|HTTPS| GW
    GW -->|route /mobile/*| BFF_M
    GW -->|route /web/*| BFF_W

    BFF_M -->|GET /catalog| S1
    BFF_M -->|GET/POST /cart| S2

    BFF_W -->|GET /catalog| S1
    BFF_W -->|GET/POST /cart| S2
    BFF_W -->|POST /checkout| S3


    style GW fill:#ECF0F1,stroke:#34495E
    style BFF_M fill:#ECF0F1,stroke:#34495E
    style BFF_W fill:#ECF0F1,stroke:#34495E
    style S1 fill:#ECF0F1,stroke:#34495E
    style S2 fill:#ECF0F1,stroke:#34495E
    style S3 fill:#ECF0F1,stroke:#34495E
```

## Quick start

Prereqs: Docker + Docker Compose.

```bash
cd kong-bff-demo
docker compose up -d --build
```

Kong runs at `http://localhost:8000`. A single API key is pre-created (`demo-key`). Include it on every request:

```bash
# List catalog via Web BFF (formatted with count)
curl -s -H "apikey: demo-key" http://localhost:8000/web/catalog | jq

# Add an item to cart via Mobile BFF
curl -s -H "apikey: demo-key" -H "Content-Type: application/json"   -d '{"sku":"SKU-2","price":14.50,"qty":1}'   http://localhost:8000/mobile/cart | jq

# Checkout via Web BFF (aggregates cart -> checkout domain service)
curl -s -H "apikey: demo-key" -X POST http://localhost:8000/web/checkout | jq
```

Rate limiting (60 req/min) and key-auth are applied at the gateway on both `/mobile/*` and `/web/*` routes.

## Layout

```text
kong-bff-demo/
├─ docker-compose.yml
├─ kong/kong.yml                # Kong (DB-less) routes, services, key-auth, rate-limiting
├─ bff/
│  ├─ web/app.py                # Web BFF (aggregation + formatting)
│  └─ mobile/app.py             # Mobile BFF (lightweight formatting)
└─ services/
   ├─ cart/app.py               # Domain Service: Cart (GET/POST /cart)
   ├─ catalog/app.py            # Domain Service: Catalog (GET /catalog)
   └─ checkout/app.py           # Domain Service: Checkout (POST /checkout)
```

## How it maps to the diagram

- **Clients → Kong** over HTTPS (plain HTTP here for simplicity).
- **Kong** handles *edge concerns* (auth, rate limiting, routing) and forwards based on path:
  - `/mobile/*` → **BFF (Mobile)**
  - `/web/*` → **BFF (Web)**
- BFFs perform **client-specific aggregation/formatting** and call domain services—no business rules live here.
- **Domain Services** expose narrow endpoints (`/cart`, `/catalog`, `/checkout`).

## Tear down

```bash
docker compose down -v
```

Notes: This demo is intentionally minimal and uses in-memory state.
