```mermaid
sequenceDiagram
  actor User
  participant Web
  participant API
  participant Svc as OrderService
  participant DB as Postgres

  User->>Web: Access site
  Web->>API: GET /orders
  activate API
  API->>Svc: listOrders()
  activate Svc
  Svc->>DB: SELECT orders
  DB-->>Svc: rows
  Svc-->>API: orders[]
  deactivate Svc
  API-->>Web: 200 JSON
  deactivate API

  alt Error
    API-->>Web: 500 Internal Error
  end
