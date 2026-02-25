# Changelog

## v2.2.0 (2026-02-15)

### Features

- add order cancellation within 1 hour (abc1234)
- add JWT refresh token endpoint (mno5678)

### Bug Fixes

- prevent negative quantities in order items (def2345)
- handle race condition in inventory check (pqr6789)

### Performance

- add index on orders.customer_id (ghi3456)

### Documentation

- update API reference for v2.2 (jkl4567)

### Refactoring

- extract PaymentAdapter from OrderService (vwx8901)

### Tests

- add property-based tests for Order total (stu7890)
