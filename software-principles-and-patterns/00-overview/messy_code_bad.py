# Messy, tightly-coupled example (violates SRP, DRY, DIP)
# Talking points:
# - Multiple responsibilities jammed in one function (SRP violation).
# - Hard-coded side effects (payment/email) make testing hard (DIP violation).
# - Likely regex/pricing duplication across code (DRY violation).
# - Ask: how many reasons to change live here?
#
# What to notice (anti-patterns):
# - SRP: This one function validates input, computes prices, charges a card,
#   and sends email. Multiple reasons to change are tangled together.
# - DRY: Email regex and pricing logic like this often get duplicated in multiple
#   places, drifting out of sync. Here it's already a "naive" one-off.
# - DIP: Payment and email are hard-coded to print statements. In real code,
#   these would be concrete SDK calls wired directly, making testing hard.
#
# Try asking the audience: "How many different tests would you need to cover
# all responsibilities here? What breaks when a requirement changes?"

import re


def process_order(order: dict) -> None:
    # validate (UI/HTTP concerns bleeding into domain logic)
    if not order.get("email"):
        raise ValueError("email required")
    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", order["email"]):
        raise ValueError("invalid email")

    # price calc (likely to be duplicated across handlers, jobs, etc.)
    subtotal = sum(item["price"] * item["qty"] for item in order["items"])  # naive
    tax = subtotal * 0.07
    total = subtotal + tax

    # payment (hard-coded dependency on a concrete side effect)
    print(f"[PAYMENT] Charging card {order['card'][-4:]} amount ${total:.2f}")

    # send email (hard-coded, mixed concerns with payment + pricing)
    print(f"[EMAIL] To: {order['email']} — Thanks! We charged ${total:.2f}")


if __name__ == "__main__":
    process_order({
        "email": "user@example.com",
        "card": "4111111111111111",
        "items": [
            {"sku": "A", "price": 10.0, "qty": 2},
            {"sku": "B", "price": 5.0, "qty": 3},
        ],
    })
