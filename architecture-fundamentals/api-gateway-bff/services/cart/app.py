from fastapi import FastAPI, Body
from typing import List, Dict, Any

app = FastAPI(title="Domain Service: Cart")

# In-memory cart items per user (very naive)
DB: Dict[str, List[Dict[str, Any]]] = {}

@app.get("/cart")
def get_cart(user: str = "u1"):
    return {"user": user, "items": DB.get(user, []), "service": "cart"}

@app.post("/cart")
def add_to_cart(item: Dict[str, Any] = Body(...), user: str = "u1"):
    DB.setdefault(user, []).append(item)
    return {"status": "added", "user": user, "count": len(DB[user])}
