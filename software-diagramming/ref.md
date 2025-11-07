# Software Diagramming Quick Reference - Mermaid & PlantUML

Purpose: paste, tweak, and render the most common diagram types in Markdown (Mermaid) and PlantUML. Use VS Code’s Markdown preview for Mermaid; use a PlantUML extension for PlantUML.

Tip: Keep each statement on its own line in sequence diagrams. Do not mix Mermaid syntax inside PlantUML blocks (and vice versa).

---

## Copy & adapt templates

### Microservice request flow (Mermaid sequence)
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
```

### Microservice request flow (PlantUML sequence)
```plantuml
@startuml
actor User
participant Web
participant API
participant "OrderService" as Svc
database Postgres as DB

User ->> Web : Access site
Web  ->> API : GET /orders
activate API
API  ->> Svc : listOrders()
activate Svc
Svc  ->> DB  : SELECT orders
DB   -->> Svc: rows
Svc  -->> API: orders[]
deactivate Svc
API  -->> Web: 200 JSON
deactivate API

alt Error
  API -->> Web : 500 Internal Error
end
@enduml
```

### Layered architecture (Mermaid flowchart)
```mermaid
flowchart LR
  subgraph Client
    A[Browser]
  end
  subgraph Edge
    G[API Gateway]
  end
  subgraph Backend
    S1[Order Service]
    S2[User Service]
  end
  subgraph Data
    DB[(Postgres)]
    Cache[(Redis)]
  end

  A --> G
  G --> S1
  G --> S2
  S1 --> DB
  S1 --> Cache
```

### Layered architecture (PlantUML component)
```plantuml
@startuml
skinparam componentStyle rectangle
actor User
node "Edge" {
  [API Gateway] as APIG
}
node "Backend" {
  [Order Service] as OrderSvc
  [User Service] as UserSvc
}
database Postgres as PG
queue Redis as R

User --> APIG
APIG --> OrderSvc
APIG --> UserSvc
OrderSvc --> PG
OrderSvc --> R
@enduml
```

### Domain aggregate (Mermaid class)
```mermaid
classDiagram
  class Order {
    +id: UUID
    +status: Status
    +addLineItem(p: ProductId, q: int)
    +total(): Money
  }
  class LineItem {
    +productId: ProductId
    +qty: int
    +price: Money
  }
  class Payment {
    +amount: Money
    +authorized: bool
  }
  Order "1" o-- "*" LineItem
  Order "0..1" --> "1" Payment
```

### Domain aggregate (PlantUML class)
```plantuml
@startuml
package "Sales" {
  class Order {
    +UUID id
    +Status status
    +addLineItem(ProductId, int)
    +Money total()
  }
  class LineItem {
    +ProductId productId
    +int qty
    +Money price
  }
  class Payment {
    +Money amount
    +bool authorized
  }

  Order "1" o-- "*" LineItem
  Order "0..1" --> "1" Payment

  note right of Order
    Aggregate Root
  end note
}
@enduml
```

### C4 container view (PlantUML via C4-PlantUML)
Requires internet or local includes.
```plantuml
@startuml
' Option A: remote include (internet required)
!includeurl https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Container.puml

' Option B: local include
' !include ./C4_Container.puml

Person(user, "User")
System_Boundary(sys, "Purchase Portal") {
  Container(web, "Web App", "React", "Serves UI")
  Container(api, "API", "Node/Express", "REST endpoints")
  ContainerDb(db, "DB", "PostgreSQL", "Stores data")
}
Rel(user, web, "Uses")
Rel(web, api, "Calls")
Rel(api, db, "Reads/Writes")
@enduml
```

### C4-like container view (Mermaid approximation)
```mermaid
flowchart LR
  user([User])
  subgraph "Purchase Portal"
    web[Container: Web App]
    api[Container: API]
    db[(ContainerDb: PostgreSQL)]
  end
  user --> web
  web --> api
  api --> db
```

---

## Mermaid quick reference

- Use fenced code blocks with ```mermaid in Markdown.

### Flowchart
```mermaid
flowchart TD
  A[Start] --> B{Auth?}
  B -- Yes --> C[Dashboard]
  B -- No --> D[Login]
  subgraph Admin
    E[Admin Panel]
  end
  C -->|link| E
  classDef highlight fill:#fffae6,stroke:#e0a800
  class C,E highlight
```

### Sequence
```mermaid
sequenceDiagram
  autonumber
  participant A as Client
  participant B as API
  A->>B: Request
  activate B
  alt Valid
    B-->>A: 200 OK
  else Invalid
    B-->>A: 400 Error
  end
  deactivate B
```

### Class
```mermaid
classDiagram
  class User {
    +id: UUID
    +name: string
    +rename(n: string)
  }
  class Account
  User "1" --> "1" Account : owns
```

### State
```mermaid
stateDiagram-v2
  [*] --> Draft
  Draft --> Submitted
  Submitted --> Approved
  Submitted --> Rejected
  Approved --> [*]
```

### ER (Entity-Relationship)
```mermaid
erDiagram
  USER ||--o{ ORDER : places
  ORDER ||--|{ LINE_ITEM : contains
  USER {
    UUID id
    string email
  }
  ORDER {
    UUID id
    date placed_at
  }
```

### Gantt
```mermaid
gantt
  dateFormat  YYYY-MM-DD
  title       Release Plan
  section Dev
    Feature A :a1, 2025-11-01, 5d
    Feature B :after a1, 3d
```

Tips
- Directions: TD, LR, BT, RL control flowchart layout.
- Styling: classDef + class to style nodes.
- Links: click A "https://example.com" "Open" in flowcharts.
- Sequence: keep each actor/message on its own line; use alt/opt/loop.

---

## PlantUML quick reference

- Use fenced code blocks with ```plantuml in Markdown.
- Most diagram types start with @startuml and end with @enduml.

### Sequence
```plantuml
@startuml
autonumber
actor Client
participant API
Client -> API : GET /items
activate API
alt Found
  API -->> Client : 200 OK
else Not Found
  API -->> Client : 404
end
deactivate API
@enduml
```

### Class
```plantuml
@startuml
class User {
  +UUID id
  +string name
  +rename(string): void
}
User <|-- Admin
@enduml
```

### Component
```plantuml
@startuml
skinparam componentStyle rectangle
[Web] --> [API]
[API] --> (Auth)
database DB
[API] --> DB
@enduml
```

### Use Case
```plantuml
@startuml
actor Customer
usecase "Place Order" as U1
Customer --> U1
@enduml
```

### Activity
```plantuml
@startuml
start
:Validate input;
if (Valid?) then (yes)
  :Process;
  stop
else (no)
  :Show error;
  stop
endif
@enduml
```

### State
```plantuml
@startuml
[*] --> Draft
Draft --> Submitted
Submitted --> Approved
Submitted --> Rejected
Approved --> [*]
@enduml
```

### Deployment
```plantuml
@startuml
node "Kubernetes" {
  node "Pod" {
    component API
  }
}
database Postgres
API --> Postgres
@enduml
```

Tips
- Themes: try !theme blueprint, or skinparam for fine-grained styling.
- strictuml: add !pragma strictuml for stricter validation.
- Graphviz: some diagrams/renderers require Graphviz installed.

---

## VS Code tips

- Preview Mermaid: open Markdown file, press Ctrl+Shift+V.
- Preview PlantUML: install "PlantUML" extension; open the PUML block and start preview (Alt+D in many setups). Graphviz may be required for some renderers.
