
import time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Sync HTTP Order API")

class Order(BaseModel):
    order_id: str = Field(..., examples=["o-123"])
    user_id: str = Field(..., examples=["u-42"])
    sku: str = Field(..., examples=["SKU-ABC"])
    qty: int = Field(..., ge=1, examples=[2])
    email: str = Field(..., examples=["user@example.com"])

def reserve_inventory(sku: str, qty: int) -> bool:
    # simulate RPC/DB with latency
    time.sleep(0.4)
    return True

def charge_payment(user_id: str, order_id: str) -> bool:
    time.sleep(0.6)
    return True

def send_email(to_addr: str, subject: str, body: str) -> None:
    time.sleep(0.2)
    print(f"[EMAIL] to={to_addr} subject={subject}")

@app.post("/order")
def place_order(order: Order):
    t0 = time.time()
    ok_inv = reserve_inventory(order.sku, order.qty)
    if not ok_inv:
        raise HTTPException(status_code=409, detail="Inventory not available")

    ok_pay = charge_payment(order.user_id, order.order_id)
    if not ok_pay:
        raise HTTPException(status_code=402, detail="Payment failed")

    send_email(order.email, "Order received", f"Thanks! Order {order.order_id}")
    elapsed = (time.time() - t0) * 1000
    return {"status": "ok", "mode": "sync", "elapsed_ms": round(elapsed)}
