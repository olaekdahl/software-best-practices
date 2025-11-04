``` mermaid
classDiagram
  class Order {
    +UUID id
    +Status status
    +addItem(SKU: String, qty: int)
    +Money total()
  }
  class LineItem {
    +String SKU
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
