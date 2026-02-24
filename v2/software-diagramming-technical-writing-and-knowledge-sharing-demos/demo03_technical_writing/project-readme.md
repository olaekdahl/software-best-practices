# Order Service

Manages the order lifecycle from creation through fulfillment. Handles payment orchestration, inventory reservation, and shipping coordination.

## Quick Start

```bash
# Clone and setup
git clone https://github.com/acme/order-service.git
cd order-service

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up local database
docker compose up -d postgres redis rabbitmq
alembic upgrade head

# Seed test data
python -m scripts.seed_data

# Run locally
uvicorn app.main:app --reload --port 8000

# Run tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html
```

## Architecture

```
order-service/
  app/
    api/              # HTTP handlers, request/response models
      routes/         # FastAPI routers grouped by domain
      middleware/     # Auth, logging, error handling
    domain/           # Business logic, entities, value objects
      models/         # Order, OrderItem, OrderStatus
      events/         # Domain events (OrderCreated, OrderShipped)
      rules/          # Business rules and validators
    application/      # Use cases, service orchestration
      commands/       # Create, submit, cancel workflows
      queries/        # List, search, reporting
    infrastructure/   # DB, API clients, message queues
      persistence/    # SQLAlchemy models, repositories
      messaging/      # RabbitMQ publisher, outbox
      clients/        # Stripe, ShipStation adapters
  tests/
    unit/             # Fast, isolated tests (~500ms)
    integration/      # Tests with real DB and queue (~10s)
    e2e/              # Full API tests with Docker (~60s)
  migrations/         # Alembic schema migrations
  scripts/            # Utility scripts (seed, backfill, etc.)
```

## Tech Stack

- Python 3.12 / FastAPI
- PostgreSQL 16 / SQLAlchemy 2.0
- Redis 7 (caching, rate limiting)
- RabbitMQ 3.13 (async events)
- Docker / Kubernetes
- GitHub Actions (CI/CD)

## API Documentation

API docs are available at `/docs` (Swagger UI) or `/redoc` (ReDoc) when running locally.

Key endpoints:

| Method | Path | Description |
|--------|------|-------------|
| POST | `/v1/orders` | Create a new order |
| GET | `/v1/orders` | List orders (paginated) |
| GET | `/v1/orders/{id}` | Get order details |
| POST | `/v1/orders/{id}/submit` | Submit order for payment |
| POST | `/v1/orders/{id}/cancel` | Cancel an order |
| GET | `/v1/orders/{id}/history` | Get order status history |

## Configuration

All configuration is via environment variables. See `.env.example` for defaults.

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgres://localhost:5432/orders` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` |
| `RABBITMQ_URL` | RabbitMQ connection string | `amqp://guest:guest@localhost:5672` |
| `STRIPE_API_KEY` | Stripe secret key | (required) |
| `LOG_LEVEL` | Logging level | `INFO` |
| `PORT` | HTTP server port | `8000` |
| `CORS_ORIGINS` | Allowed CORS origins | `http://localhost:3000` |

## Development

```bash
# Format code
ruff format .

# Lint
ruff check .

# Type check
mypy app/

# Run all quality checks
make check

# Run only unit tests (fast)
pytest tests/unit -x

# Run with verbose output
pytest -v --tb=short

# Generate test coverage report
pytest --cov=app --cov-report=html
open htmlcov/index.html
```

## Deployment

Deployed via GitHub Actions. See `.github/workflows/deploy.yml`.

| Branch/Tag | Target | Approval |
|------------|--------|----------|
| `main` | Staging | Automatic |
| `v*.*.*` tag | Production | Requires 1 approval |

### Rollback

```bash
# Rollback to previous deployment
kubectl rollout undo deployment/order-service -n marketplace

# Rollback to specific revision
kubectl rollout undo deployment/order-service --to-revision=3
```

## Contributing

1. Create a feature branch from `main`
2. Write tests for new functionality
3. Ensure `make check` passes (lint, type check, tests)
4. Open a pull request with a clear description
5. Get at least one approval before merging
6. Squash and merge - keep main history clean

### Commit Convention

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add order cancellation within 1 hour
fix: prevent negative quantities in order items
docs: update API reference for v2.1
perf: add index on orders.customer_id
test: add property-based tests for Order.total
```

## Monitoring

- **Metrics:** Prometheus at `/metrics`, Grafana dashboard "Order Service"
- **Logs:** JSON structured logs shipped to Elasticsearch
- **Traces:** OpenTelemetry traces exported to Jaeger
- **Alerts:** PagerDuty integration for SEV1/SEV2

## Team

- **Owner:** Platform Team (@platform-team)
- **Slack:** #order-service-dev
- **On-call:** See [PagerDuty schedule](https://acme.pagerduty.com/schedules)
- **Architecture:** See [ADR index](docs/adr/)
