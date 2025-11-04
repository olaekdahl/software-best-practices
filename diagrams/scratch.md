``` mermaid
graph
    User -- HTTP -->WebApp
    WebApp -->|SQL| Database
```
``` mermaid
sequenceDiagram
    participant User
    participant API
    participant DB
    User->>API: Sends request
    API->>DB: Query data
    DB-->>API: Return result
    API-->>User: Response
```
``` mermaid
graph TD
    A[Parent Portal] --> B[Backend API]
    B --> C[(Azure SQL DB)]
    B --> D[(Azure AI Search)]
```
``` mermaid
flowchart TD
    %% Persons
    P[Parent/Guardian]
    T[Teacher]
    A[School Admin]
    V[Vendor Rep]

    %% System
    PP[[Purchase Portal System]]

    %% External Systems
    ENTRA[(Microsoft Entra ID)]
    EMAIL[(SendGrid Email)]
    SEARCH[(Azure AI Search)]
    SQL[(Azure SQL Database)]

    %% Relationships
    P --> PP
    T --> PP
    A --> PP
    V --> PP

    ENTRA --- PP
    PP --- EMAIL
    PP --- SEARCH
    PP --- SQL

    %% Notes
    classDef ext fill:#eef,stroke:#889;
    class ENTRA,EMAIL,SEARCH,SQL ext;

```