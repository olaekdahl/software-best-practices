
import json, time
from kafka import KafkaConsumer

TOPIC = "orders"

def reserve_inventory(sku: str, qty: int) -> bool:
    time.sleep(0.4)
    print(f"[INV] reserved sku={sku} qty={qty}")
    return True

consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers="localhost:9092",
    group_id="inventory-svc",
    auto_offset_reset="earliest",
    enable_auto_commit=True,
    value_deserializer=lambda v: json.loads(v.decode("utf-8")),
)

print("[INV] listening...")
for msg in consumer:
    evt = msg.value
    if evt.get("type") == "OrderPlaced":
        payload = evt["payload"]
        reserve_inventory(payload["sku"], payload["qty"])
