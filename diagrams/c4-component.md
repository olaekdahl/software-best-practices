``` mermaid
  flowchart LR
  subgraph "Order Service"
    API[Order API\nHTTP Controllers\nValidates/handles requests]
    APP[Application Service\nUse cases\nCoordinates domain]
    DOMAIN[Domain\nEntities & Aggregates\nBusiness rules]
    REPO[Repository\nData access\nPersistence operations]
  end

  DB[(PostgreSQL\nOrder storage)]

  API -->|Calls| APP
  APP -->|Invokes domain logic| DOMAIN
  APP -->|Persists/loads| REPO
  REPO -->|SQL| DB
  ```
