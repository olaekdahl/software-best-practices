import os, httpx
from fastapi import FastAPI

CATALOG_URL = os.getenv("CATALOG_URL", "http://catalog:8000")
CART_URL    = os.getenv("CART_URL", "http://cart:8000")

app = FastAPI(title="BFF: Mobile")

@app.get("/mobile/catalog")
async def mobile_catalog():
    # Mobile aggregation/formatting: lightweight (names only)
    async with httpx.AsyncClient() as c:
        data = (await c.get(f"{CATALOG_URL}/catalog", timeout=5)).json()
    return {"items": [{"sku": i["sku"], "name": i["name"]} for i in data["items"]], "client": "mobile"}

@app.get("/mobile/cart")
async def mobile_cart(user: str = "u1"):
    async with httpx.AsyncClient() as c:
        r = await c.get(f"{CART_URL}/cart", params={"user": user}, timeout=5)
        return r.json()

@app.post("/mobile/cart")
async def mobile_add_cart(item: dict, user: str = "u1"):
    async with httpx.AsyncClient() as c:
        r = await c.post(f"{CART_URL}/cart", params={"user": user}, json=item, timeout=5)
        return r.json()
