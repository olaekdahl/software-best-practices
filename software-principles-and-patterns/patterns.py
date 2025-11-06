### Strategy
# BAD
def total(base, tier):
    if tier == "vip":
        return int(base * 0.8)
    elif tier == "regular":
        return int(base * 0.9)
    return base
# GOOD
from abc import ABC, abstractmethod

class Pricing(ABC):
    @abstractmethod
    def total(self, base: int) -> int: ...

class Vip(Pricing):
    def total(self, base): return int(base * 0.8)

class Regular(Pricing):
    def total(self, base): return int(base * 0.9)

def checkout(base: int, pricing: Pricing) -> int:
    return pricing.total(base)

# usage: checkout(100, Vip())

### Adapter
# BAD
# vendor client exposes send_mail(to, content)
def notify_user(user_email, msg, vendor_client):
    vendor_client.send_mail(to=user_email, content=msg)  # hard dependency

# GOOD
class EmailPort:
    def send(self, to: str, body: str) -> None: ...

class SendGridAdapter(EmailPort):
    def __init__(self, sg): self.sg = sg
    def send(self, to, body): self.sg.send_mail(to=to, content=body)

def notify_user(user_email, msg, emailer: EmailPort):
    emailer.send(user_email, msg)

# usage: notify_user("a@b.com", "hi", SendGridAdapter(sg_client))

### Facade
# BAD
def place_order(user, items, gateway, ledger, notifier):
    charge = gateway.charge(user, items)
    ledger.record(charge)
    notifier.send(user, "Thanks!")
    return charge

# GOOD
class PaymentsFacade:
    def __init__(self, gateway, ledger, notifier):
        self.gw, self.ledger, self.notifier = gateway, ledger, notifier
    def charge_and_notify(self, user, items):
        tx = self.gw.charge(user, items)
        self.ledger.record(tx)
        self.notifier.send(user, "Thanks!")
        return tx

# usage: PaymentsFacade(gw, ledg, notif).charge_and_notify(user, items)
# BAD
def fetch_profile(api):
    # If api is slow/flaky, every call waits and often times out
    return api.get("/profile")

# GOOD
import time

class Circuit:
    def __init__(self, threshold=3, reset_after=10):
        self.failures = 0
        self.opened_at = 0
        self.threshold = threshold
        self.reset_after = reset_after

    def call(self, fn, *a, **k):
        if self.opened_at and time.time() - self.opened_at < self.reset_after:
            raise RuntimeError("circuit open")
        try:
            r = fn(*a, **k)
            self.failures = 0; self.opened_at = 0
            return r
        except Exception:
            self.failures += 1
            if self.failures >= self.threshold:
                self.opened_at = time.time()
            raise

# usage: Circuit().call(api.get, "/profile")

### Saga
# BAD
def place_order(ctx, inv, pay, ship):
    inv.reserve(ctx)             # succeeds
    pay.charge(ctx)              # fails → reservation remains stuck
    ship.create(ctx)

# GOOD
steps = [
    ("reserve",     "release"),
    ("charge",      "refund"),
    ("create_ship", "delete_ship"),
]

def run_saga(ctx, bus):
    done = []
    try:
        for do, undo in steps:
            bus[do](ctx)         # forward action
            done.append((do, undo))
        return {"ok": True}
    except Exception:
        for _, undo in reversed(done):
            bus[undo](ctx)       # compensate
        return {"ok": False}

# usage: run_saga(ctx, {"reserve": inv.reserve, "release": inv.release, ...})

### CQRS
# BAD
# write: validates and writes to normalized tables
def create_order(db, order):
    db.insert("orders", order)   # heavy rules here

# read: joins multiple tables each time (slow)
def get_order_view(db, order_id):
    return db.query("""
      SELECT o.id, c.name, SUM(i.qty*i.price) total
      FROM orders o JOIN customers c ON ... JOIN items i ON ...
      WHERE o.id = ?
    """, order_id)

# GOOD
# command side
def create_order(dbw, projector, order):
    dbw.insert("orders", order)              # authoritative write
    projector.order_created(order)           # update read model

# read side (fast, precomputed view)
def get_order_view(dbr, order_id):
    return dbr.get("order_view", order_id)   # single-key lookup

# example projector
class Projector:
    def __init__(self, dbrw): self.dbrw = dbrw
    def order_created(self, order):
        view = {
            "id": order["id"],
            "customer": order["customer_name"],
            "total": sum(it["qty"]*it["price"] for it in order["items"]),
        }
        self.dbrw.upsert("order_view", view["id"], view)
