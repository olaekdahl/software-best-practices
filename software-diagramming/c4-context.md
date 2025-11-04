# App diagram

- This is my app
- Here's some markdown

``` mermaid
flowchart
  User([User])
  System[Purchase Portal\nAllows users to browse and place orders]
  Email[Email Service\nSends notifications]
  Payments[Payment Provider\nProcesses payments]

  User -->|HTTPS / Uses| System
  System -- Sends notifications --> Email
  System -->|Charges cards| Payments
```
