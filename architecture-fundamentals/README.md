
# Architecture Fundamentals — Sync HTTP vs Event-Driven with Kafka (Runnable Demo)

This project shows the same "place order" flow in two architectures:

1) **Synchronous HTTP** (single request does all the work)
2) **Event-driven with Kafka** (API is fast; background consumers do the work)

## Prerequisites

- Python 3.10+
- Docker and Docker Compose (for Kafka)

## 1) Set up Python env and install deps

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## 2) Run the Synchronous HTTP version

```bash
uvicorn sync_http.app:app --reload --port 8000
```

Test:

```bash
curl -X POST http://localhost:8000/order -H "Content-Type: application/json" \
  -d '{"order_id":"o-1","user_id":"u-1","sku":"ABC","qty":1,"email":"user@example.com"}'
```

## 3) Start Kafka (single-node, KRaft)

```bash
docker compose up -d
```

## 4) Run the Kafka Producer API

```bash
uvicorn kafka_version.producer_api:app --reload --port 8001
```

Send an order (fast response):

```bash
curl -X POST http://localhost:8001/order -H "Content-Type: application/json" \
  -d '{"order_id":"o-2","user_id":"u-1","sku":"ABC","qty":1,"email":"user@example.com"}'
```

## 5) Run the Kafka consumers (in three separate terminals)

```bash
python3 kafka_version/consumers/inventory_consumer.py
python3 kafka_version/consumers/payment_consumer.py
python3 kafka_version/consumers/email_consumer.py
```

Watch logs print as events are processed.

## Pros and Cons (Summary)

Synchronous HTTP:

- Pros: simple, easy error propagation, good for fast/reliable dependencies.
- Cons: client latency grows, timeouts/retries inside controller, limited independent scaling.

Kafka (Event-driven):

- Pros: fast API response, loose coupling, independent scaling of steps, natural retry/DLQ patterns.
- Cons: eventual consistency, more complex tracing, design for idempotency, extra infra to operate.
