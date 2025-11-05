### DRY
# BAD
def calculate_discount(price, customer_type):
    if customer_type == "vip":
        return price * 0.8
    elif customer_type == "regular":
        return price * 0.9

def print_invoice(price, customer_type):
    # Duplicating the same discount logic here
    if customer_type == "vip":
        total = price * 0.8
    elif customer_type == "regular":
        total = price * 0.9
    print(f"Total: {total}")

# GOOD
def apply_discount(price, customer_type):
    discounts = {"vip": 0.8, "regular": 0.9}
    return price * discounts.get(customer_type, 1.0)

def print_invoice(price, customer_type):
    total = apply_discount(price, customer_type)
    print(f"Total: {total}")

### KISS
# BAD
class MessageSender:
    def __init__(self, strategy):
        self.strategy = strategy

    def send(self, msg):
        self.strategy.execute(msg)

class ConsoleStrategy:
    def execute(self, msg):
        print(msg)

# usage
MessageSender(ConsoleStrategy()).send("Hello, world!")

# GOOD
def send_message(msg):
    print(msg)

send_message("Hello, world!")

### YAGNI
# BAD
class PaymentProcessor:
    def process(self, payment_method, amount):
        if payment_method == "credit":
            self._process_credit_card(amount)
        elif payment_method == "crypto":
            self._process_crypto(amount)
        # preparing for "future" payment types…
        elif payment_method == "barter" or payment_method == "giftcard":
            pass  # Not implemented yet

    def _process_credit_card(self, amount): pass
    def _process_crypto(self, amount): pass

# GOOD
class PaymentProcessor:
    def process_credit_card(self, amount):
        print(f"Processing credit card payment: ${amount}")

