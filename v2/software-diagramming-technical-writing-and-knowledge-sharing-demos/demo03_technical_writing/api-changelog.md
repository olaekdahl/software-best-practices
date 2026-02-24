# Changelog

All notable changes to the Order Service are documented in this file.

This project follows [Conventional Commits](https://www.conventionalcommits.org/) and [Semantic Versioning](https://semver.org/).

## [2.2.0] - 2026-02-15

### Features

- Add order cancellation within 1 hour of confirmation (abc1234)
- Add JWT refresh token endpoint for extended sessions (mno5678)
- Support bulk order creation via CSV upload (xyz9012)

### Bug Fixes

- Prevent negative quantities in order items (def2345)
- Handle race condition in inventory reservation check (pqr6789)
- Fix cursor-based pagination returning duplicate items at page boundaries (rst3456)

### Performance

- Add composite index on `orders(customer_id, created_at)` - 3x faster order history queries (ghi3456)
- Enable connection pooling with PgBouncer - reduces connection overhead by 40% (uvw7890)

### Documentation

- Update API reference for v2.2 endpoints (jkl4567)
- Add runbook for connection pool exhaustion (abc8901)

## [2.1.0] - 2026-01-15

### Features

- Add order status history tracking with timestamps (aaa1111)
- Implement cursor-based pagination for order listing (bbb2222)
- Add webhook notifications for order status changes (ccc3333)

### Bug Fixes

- Fix timezone handling in order creation timestamps (ddd4444)
- Correct discount calculation for percentage-based coupons (eee5555)

### Refactoring

- Extract PaymentAdapter from OrderService for better testability (vwx8901)
- Split OrderRouter into separate command and query routers (fff6666)

### Tests

- Add property-based tests for Order.total calculation (stu7890)
- Add integration tests for RabbitMQ event publishing (ggg7777)

## [2.0.0] - 2025-12-01

### Breaking Changes

- API prefix changed from `/api/` to `/v1/` for versioning support
- Order creation now requires `idempotency_key` header
- Removed deprecated `/orders/search` endpoint (use query params on `/v1/orders`)

### Features

- Add OpenAPI 3.0 spec generation from FastAPI routes (hhh8888)
- Implement circuit breaker for Stripe payment calls (iii9999)
- Add structured JSON logging with correlation IDs (jjj0000)

### Bug Fixes

- Fix memory leak in WebSocket connection handler (kkk1111)
- Correct HTTP status codes: 422 for validation errors instead of 400 (lll2222)

### Infrastructure

- Migrate from Docker Compose to Kubernetes (mmm3333)
- Add Prometheus metrics endpoint at `/metrics` (nnn4444)
- Configure GitHub Actions CI with parallel test execution (ooo5555)

## [1.0.0] - 2025-09-15

### Features

- Initial release of Order Service
- CRUD operations for orders and order items
- Stripe payment integration
- Email notifications via SendGrid
- Basic authentication with JWT
