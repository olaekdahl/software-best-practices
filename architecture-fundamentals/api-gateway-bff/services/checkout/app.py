from fastapi import FastAPI, Body, HTTPException
app = FastAPI(title="Domain Service: Checkout")

@app.post("/checkout")
def checkout(payload: dict = Body(...)):
    # pretend to take payment and create order
    if not payload.get("user") or not payload.get("items"):
        raise HTTPException(status_code=400, detail="missing user or items")
    return {"status": "ok", "order_id": "ORD-123", "total": sum(i.get("price",0) for i in payload["items"])}
