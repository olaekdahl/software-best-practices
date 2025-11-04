# Modeling examples: UML, ERD, DFD, and State Machines

This file shows small, copyable examples for common diagram types. Each section includes a short explanation and at least one diagram sample (Mermaid-first; PlantUML where valuable).

---

## UML basics: structural vs behavioral

- Structural: what the system is (static) — e.g., Class diagrams.
- Behavioral: what the system does (dynamic) — e.g., Sequence, Activity, State.

Tip: Use Sequence/Activity for flows; Class for data/structure; State for lifecycles.

---

## UML — Sequence (behavioral)

### Mermaid (sequence)

```mermaid
sequenceDiagram
  autonumber
  actor User
  participant Web
  participant API
  participant DB

  User->>Web: Click "Checkout"
  Web->>API: POST /orders
  activate API
  API->>DB: INSERT order
  DB-->>API: OK
  API-->>Web: 201 Created
  deactivate API
  Web-->>User: Confirmation

  alt Invalid input
    API-->>Web: 400 Bad Request
  end
```

### PlantUML (sequence)

```plantuml
@startuml
autonumber
actor User
participant Web
participant API
database DB

User ->> Web : Click Checkout
Web  ->> API : POST /orders
activate API
API  ->> DB  : INSERT order
DB   -->> API: OK
API  -->> Web: 201 Created
deactivate API
Web  -->> User: Confirmation

alt Invalid input
  API -->> Web : 400 Bad Request
end
@enduml
```

---

## UML — Class (structural)

### Mermaid (class)

```mermaid
classDiagram
  class Order {
    +UUID id
    +Status status
    +addLineItem(sku: string, qty: int)
    +Money total()
  }
  class LineItem {
    +string sku
    +int qty
    +Money price
  }
  class Payment {
    +Money amount
    +bool authorized
  }

  Order "1" o-- "*" LineItem : contains
  Order "0..1" --> "1" Payment : settled by
```

### PlantUML (class)

```plantuml
@startuml
class Order {
  +UUID id
  +Status status
  +addLineItem(sku: String, qty: int)
  +Money total()
}
class LineItem {
  +String sku
  +int qty
  +Money price
}
class Payment {
  +Money amount
  +boolean authorized
}

Order "1" o-- "*" LineItem : contains
Order "0..1" --> "1" Payment : settled by
@enduml
```

---

## UML — State (behavioral)

### Mermaid (state)

```mermaid
stateDiagram-v2
  [*] --> Pending
  Pending --> Paid: paymentReceived
  Paid --> Shipped: ship()
  Shipped --> Delivered
  Paid --> Cancelled: cancel()
  Cancelled --> [*]
```

### PlantUML (state)

```plantuml
@startuml
[*] --> Pending
Pending --> Paid : paymentReceived
Paid --> Shipped : ship()
Shipped --> Delivered
Paid --> Cancelled : cancel()
Cancelled --> [*]
@enduml
```

---

## UML — Activity (behavioral)

### Mermaid (flowchart approximation)

```mermaid
flowchart TD
  A[Start] --> B{Valid?}
  B -- Yes --> C[Process order]
  B -- No  --> D[Show error]
  C --> E[Send confirmation]
  D --> E
  E --> F[End]
```

### PlantUML (activity)

```plantuml
@startuml
start
:Validate input;
if (Valid?) then (yes)
  :Process order;
  :Send confirmation;
  stop
else (no)
  :Show error;
  stop
endif
@enduml
```

---

## ERD — Entities, relationships, cardinality

### Mermaid ER

```mermaid
erDiagram
  CUSTOMER ||--o{ ORDER : places
  ORDER ||--|{ LINE_ITEM : contains
  PRODUCT ||--o{ LINE_ITEM : referenced

  CUSTOMER {
    UUID id
    string name
    string email
  }
  ORDER {
    UUID id
    date placed_at
    decimal total
  }
  PRODUCT {
    UUID id
    string sku
    string name
    decimal price
  }
  LINE_ITEM {
    UUID order_id
    UUID product_id
    int qty
    decimal price
  }
```

Notes

- Cardinality: `||` one, `o{` zero-or-many, `|{` one-or-many.
- Normalization vs pragmatism:
  - Normalization reduces duplication (e.g., product name/price live in PRODUCT).
  - Pragmatism may de-normalize for performance or historical accuracy (e.g., copy price into LINE_ITEM). Document why.

---

## Data Flow Diagram (DFD) — Sources/sinks, processes, data stores, trust boundaries

Mermaid doesn’t have a native DFD, but you can approximate with flowchart shapes and subgraphs labeled as trust boundaries.

### Mermaid (DFD approximation)

```mermaid
flowchart LR
  %% External actors (sources/sinks)
  User([User])
  Payment([Payment Provider])

  %% Trust boundary: Internal system
  subgraph "Trust Boundary: Internal"
    API([Process: API])
    OrderSvc([Process: Order Service])
    DB[(Data Store: Postgres)]
  end

  User -->|HTTP request| API
  API -->|Command| OrderSvc
  OrderSvc -->|Read/Write| DB
  OrderSvc -->|Charge| Payment
  API -->|HTTP response| User
```

Legend

- Sources/sinks: rounded rectangles ([User])
- Processes: rounded rectangles labeled `Process:`
- Data stores: cylinder `[(...)]`
- Trust boundaries: subgraphs labeled accordingly

---

## State machines — Lifecycle and invariants

Pick critical domain objects (e.g., Order) and encode their lifecycle and invariants.

### Mermaid — Order lifecycle with invariants

```mermaid
stateDiagram-v2
  [*] --> Draft
  Draft --> Submitted: submit()
  Submitted --> Paid: paymentReceived
  Paid --> Fulfilled: ship()
  Submitted --> Cancelled: cancel()
  Paid --> Refunded: refund()
  Cancelled --> [*]
  Fulfilled --> [*]

  note right of Paid
    Invariants:
    - total > 0
    - paymentId set
  end note
```

Guidance

- Keep states mutually exclusive and exhaustive where possible.
- Attach invariants to states where they hold.
- Transitions should be triggered by events or commands and be auditable.
