"""
Demo 01 - Anti-pattern: No Design Principles
=============================================
This is an intentionally BAD example showing what happens when code
ignores SOLID, DRY, KISS, and YAGNI principles.

Instructor talking points:
- God class doing everything (violates SRP)
- Conditional chains instead of polymorphism (violates OCP)
- Duplicated validation logic (violates DRY)
- Hard-coded dependencies (violates DIP)
- Speculative features nobody asked for (violates YAGNI)

Run: python main.py
"""


class OrderSystem:
    """God class that handles orders, payments, notifications, and reporting."""

    def __init__(self):
        self.orders = []
        self.tax_rates = {"CA": 0.0725, "NY": 0.08, "TX": 0.0625}

    def create_order(self, customer_name, email, items, state, payment_type):
        # Duplicated email validation (also in subscribe_newsletter)
        if "@" not in email or "." not in email:
            print("Invalid email!")
            return None

        # Conditional chain for tax - grows with every new state
        if state == "CA":
            tax_rate = 0.0725
        elif state == "NY":
            tax_rate = 0.08
        elif state == "TX":
            tax_rate = 0.0625
        else:
            tax_rate = 0.0

        subtotal = sum(price for _, price in items)
        tax = subtotal * tax_rate
        total = subtotal + tax

        # Conditional chain for payment - grows with every new provider
        if payment_type == "credit_card":
            print(f"Charging credit card ${total:.2f}")
            payment_ok = True
        elif payment_type == "paypal":
            print(f"Charging PayPal ${total:.2f}")
            payment_ok = True
        elif payment_type == "crypto":
            # YAGNI: nobody asked for crypto payments yet
            print(f"Charging crypto ${total:.2f}")
            payment_ok = True
        elif payment_type == "bank_transfer":
            # YAGNI: speculative feature
            print(f"Bank transfer ${total:.2f}")
            payment_ok = True
        else:
            print("Unknown payment type!")
            payment_ok = False

        if not payment_ok:
            return None

        order = {
            "customer": customer_name,
            "email": email,
            "items": items,
            "subtotal": subtotal,
            "tax": tax,
            "total": total,
            "state": state,
            "payment_type": payment_type,
            "status": "completed",
        }
        self.orders.append(order)

        # Hard-coded notification - can't swap provider
        print(f"Sending email to {email}: Your order total is ${total:.2f}")

        # Hard-coded logging - no abstraction
        print(f"LOG: Order created for {customer_name}, total=${total:.2f}")

        return order

    def subscribe_newsletter(self, email):
        # DUPLICATED email validation (same as in create_order)
        if "@" not in email or "." not in email:
            print("Invalid email!")
            return False
        print(f"Subscribed {email} to newsletter")
        return True

    def generate_report(self):
        # Reporting mixed into the order class
        print("\n=== Sales Report ===")
        grand_total = 0
        for order in self.orders:
            print(
                f"  {order['customer']}: ${order['total']:.2f} "
                f"({order['payment_type']})"
            )
            grand_total += order["total"]
        print(f"  Grand Total: ${grand_total:.2f}")
        print("===================")

    def export_csv(self):
        # YAGNI: nobody asked for CSV export yet
        print("customer,total,payment_type")
        for order in self.orders:
            print(f"{order['customer']},{order['total']},{order['payment_type']}")

    def export_xml(self):
        # YAGNI: definitely nobody asked for XML
        print("<orders>")
        for order in self.orders:
            print(f"  <order customer='{order['customer']}' total='{order['total']}'/>")
        print("</orders>")


def main():
    system = OrderSystem()

    print("=== Demo: No Design Principles (Anti-patterns) ===\n")

    # Create some orders
    system.create_order(
        "Alice", "alice@example.com",
        [("Widget", 29.99), ("Gadget", 49.99)],
        "CA", "credit_card"
    )
    print()

    system.create_order(
        "Bob", "bob@example.com",
        [("Widget", 29.99)],
        "NY", "paypal"
    )
    print()

    # Subscribe to newsletter
    system.subscribe_newsletter("charlie@example.com")
    print()

    # Generate report
    system.generate_report()

    print("\n--- Problems with this code ---")
    print("1. OrderSystem is a god class (SRP violation)")
    print("2. Tax/payment logic uses if/elif chains (OCP violation)")
    print("3. Email validation duplicated (DRY violation)")
    print("4. Hard-coded email and logging (DIP violation)")
    print("5. CSV/XML export built without requirement (YAGNI violation)")
    print("6. Adding a new state or payment type requires modifying existing code")


if __name__ == "__main__":
    main()
