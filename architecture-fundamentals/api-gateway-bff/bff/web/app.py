import os, httpx
from fastapi import FastAPI, HTTPException

CATALOG_URL = os.getenv("CATALOG_URL", "http://catalog:8000")
CART_URL    = os.getenv("CART_URL", "http://cart:8000")
CHECKOUT_URL= os.getenv("CHECKOUT_URL", "http://checkout:8000")

app = FastAPI(title="BFF: Web")

@app.get("/web/catalog")
async def web_catalog():
    async with httpx.AsyncClient() as c:
        r = await c.get(f"{CATALOG_URL}/catalog", timeout=5)
        r.raise_for_status()
        data = r.json()
    # Web formatting: include count
    return {"count": len(data["items"]), "items": data["items"], "client": "web"}

@app.get("/web/cart")
async def web_cart(user: str = "u1"):
    async with httpx.AsyncClient() as c:
        r = await c.get(f"{CART_URL}/cart", params={"user": user}, timeout=5)
        r.raise_for_status()
        return r.json()

@app.post("/web/cart")
async def web_add_cart(item: dict, user: str = "u1"):
    async with httpx.AsyncClient() as c:
        r = await c.post(f"{CART_URL}/cart", params={"user": user}, json=item, timeout=5)
        r.raise_for_status()
        return r.json()

@app.post("/web/checkout")
async def web_checkout(user: str = "u1"):
    # aggregate from cart + send to checkout
    async with httpx.AsyncClient() as c:
        cart = (await c.get(f"{CART_URL}/cart", params={"user": user}, timeout=5)).json()
        resp = await c.post(f"{CHECKOUT_URL}/checkout", json={"user": user, "items": cart["items"]}, timeout=5)
        resp.raise_for_status()
        return resp.json()
