# Web App Request Flow (Mermaid)

```mermaid
sequenceDiagram
    participant User
    participant Browser
    participant API
    participant DB

    User->>Browser: Click "Login"
    Browser->>API: POST /login
    API->>DB: Query user credentials
    DB-->>API: Return user record
    API-->>Browser: Return JWT token
    Browser-->>User: Show dashboard
