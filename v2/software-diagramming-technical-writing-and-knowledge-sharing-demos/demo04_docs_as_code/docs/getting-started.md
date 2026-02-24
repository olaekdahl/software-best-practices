# Getting Started

Welcome to the Order Service. This guide will get you up and running in under 5 minutes.

## Prerequisites

- Python 3.12 or later
- Docker and Docker Compose (for local databases)
- Git

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/acme/order-service.git
cd order-service
```

### 2. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Start infrastructure

```bash
docker compose up -d
```

This starts PostgreSQL, Redis, and RabbitMQ locally.

### 5. Run database migrations

```bash
alembic upgrade head
```

### 6. Start the application

```bash
uvicorn app.main:app --reload --port 8000
```

The API is now available at [http://localhost:8000](http://localhost:8000).

## Verify it works

```bash
# Health check
curl http://localhost:8000/health

# Create a test order
curl -X POST http://localhost:8000/v1/orders \
  -H "Content-Type: application/json" \
  -d '{"customer_id": "cust-001", "items": [{"sku": "WIDGET-01", "quantity": 2}]}'
```

## API Documentation

Interactive API docs are available at:

- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Next Steps

- Read the [API Guide](api-guide.md) for detailed endpoint documentation
- See [Troubleshooting](troubleshooting.md) if you run into issues
- Review the [Architecture Decision Records](../adr/) for design context
