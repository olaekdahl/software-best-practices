# BAD
# domain/service.py
import sqlite3  # domain tied to a specific DB

def get_customer_total(customer_id: int) -> float:
    conn = sqlite3.connect("app.db")
    cur = conn.cursor()
    cur.execute("SELECT SUM(amount) FROM orders WHERE customer_id=?", (customer_id,))
    return cur.fetchone()[0] or 0.0

# GOOD
# domain/ports.py
from abc import ABC, abstractmethod

class OrderRepo(ABC):
    @abstractmethod
    def sum_by_customer(self, customer_id: int) -> float: ...

# domain/service.py (pure domain)
def get_customer_total(customer_id: int, repo: OrderRepo) -> float:
    return repo.sum_by_customer(customer_id)

# adapters/sql_repo.py (infrastructure)
import sqlite3
from domain.ports import OrderRepo

class SQLiteOrderRepo(OrderRepo):
    def __init__(self, path="app.db"):
        self.path = path
    def sum_by_customer(self, customer_id: int) -> float:
        with sqlite3.connect(self.path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT SUM(amount) FROM orders WHERE customer_id=?", (customer_id,))
            return cur.fetchone()[0] or 0.0

# composition (app startup)
repo = SQLiteOrderRepo()
total = get_customer_total(42, repo)

