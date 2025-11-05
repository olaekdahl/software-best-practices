
.PHONY: venv deps kafka up down sync api consumers

venv:
	python -m venv .venv

deps:
	. .venv/bin/activate && pip install -r requirements.txt

kafka:
	docker compose up -d

down:
	docker compose down -v

sync:
	uvicorn sync_http.app:app --reload --port 8000

api:
	uvicorn kafka_version.producer_api:app --reload --port 8001

consumers:
	python3 kafka_version/consumers/inventory_consumer.py & \
	python3 kafka_version/consumers/payment_consumer.py & \
	python3 kafka_version/consumers/email_consumer.py
