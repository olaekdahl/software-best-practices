
import json, time
from kafka import KafkaConsumer

TOPIC = "orders"

def charge_payment(user_id: str, order_id: str) -> bool:
    time.sleep(0.6)
    print(f"[PAY] charged user={user_id} order={order_id}")
    return True

consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers="localhost:9092",
    group_id="payment-svc",
    auto_offset_reset="earliest",
    enable_auto_commit=True,
    value_deserializer=lambda v: json.loads(v.decode("utf-8")),
)

print("[PAY] listening...")
for msg in consumer:
    evt = msg.value
    if evt.get("type") == "OrderPlaced":
        p = evt["payload"]
        charge_payment(p["user_id"], p["order_id"])
