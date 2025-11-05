
import json, os, time, asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable

TOPIC = os.getenv("KAFKA_TOPIC", "orders")
BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "localhost:9092")

# Lazy-initialized producer (so the API can start even if Kafka is coming up)
producer: KafkaProducer | None = None

def _make_producer() -> KafkaProducer:
    return KafkaProducer(
        bootstrap_servers=BOOTSTRAP,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        linger_ms=5,
    )

app = FastAPI(title="Kafka Producer API")

class Order(BaseModel):
    order_id: str = Field(..., examples=["o-123"])
    user_id: str = Field(..., examples=["u-42"])
    sku: str = Field(..., examples=["SKU-ABC"])
    qty: int = Field(..., ge=1, examples=[2])
    email: str = Field(..., examples=["user@example.com"])

@app.post("/order")
def place_order(order: Order):
    t0 = time.time()
    event = {
        "type": "OrderPlaced",
        "ts": time.time(),
        "payload": order.dict(),
    }
    # Ensure producer exists (create on first use if needed)
    global producer
    if producer is None:
        try:
            producer = _make_producer()
        except NoBrokersAvailable:
            # Broker not ready yet
            raise HTTPException(status_code=503, detail="Kafka broker not available")

    # fire-and-forget
    producer.send(TOPIC, event)
    producer.flush(1.0)
    elapsed = (time.time() - t0) * 1000
    return {"status": "accepted", "mode": "kafka", "elapsed_ms": round(elapsed)}


@app.on_event("startup")
async def _startup_try_connect():
    """
    Try to create the producer with a short backoff so first requests are likely to succeed,
    but don't fail the app if Kafka isn't ready yet (we'll return 503 instead).
    """
    global producer
    for attempt in range(5):
        try:
            producer = _make_producer()
            return
        except NoBrokersAvailable:
            await asyncio.sleep(0.5 * (attempt + 1))


@app.on_event("shutdown")
def _shutdown_close():
    global producer
    if producer:
        try:
            producer.close(timeout=2)
        except Exception:
            pass
