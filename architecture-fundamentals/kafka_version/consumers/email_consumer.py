
import json, time
from kafka import KafkaConsumer

TOPIC = "orders"

def send_email(addr: str, subject: str, body: str):
    time.sleep(0.2)
    print(f"[EMAIL] to={addr} subject={subject} body={body}")

consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers="localhost:9092",
    group_id="email-svc",
    auto_offset_reset="earliest",
    enable_auto_commit=True,
    value_deserializer=lambda v: json.loads(v.decode("utf-8")),
)

print("[EMAIL] listening...")
for msg in consumer:
    evt = msg.value
    if evt.get("type") == "OrderPlaced":
        p = evt["payload"]
        send_email(p["email"], "Order received", f"Thanks! Order {p['order_id']}")
