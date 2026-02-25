# Postmortem: Payment Processing Outage

**Incident ID:** INC-2026-0210
**Date:** 2026-02-10
**Duration:** 23 minutes (09:42 UTC - 10:05 UTC)
**Severity:** SEV2
**Author:** On-call engineer (Demo User)

---

## Summary

For 23 minutes, 35% of payment submissions returned HTTP 500 errors. The root cause was a connection pool leak in the payment adapter caused by unhandled timeout exceptions.

## Impact

- **Users affected:** Approximately 450 customers saw "Payment failed" errors
- **Orders lost:** 112 orders failed to process (estimated $7,800 in revenue at risk)
- **Recovery rate:** 89% of affected customers retried successfully after resolution
- **SLO impact:** Error rate SLI at 96.5% (target: 99.9%) for a 23-minute window

## Timeline

| Time (UTC) | Event |
|------------|-------|
| 09:35 | Stripe API begins responding with elevated latency (p99 jumps from 200ms to 3,500ms) |
| 09:42 | Circuit breaker trips after 5 consecutive timeouts |
| 09:42 | Alert `payment_error_rate_high` fires |
| 09:44 | On-call acknowledges alert, begins investigation |
| 09:48 | Identifies circuit breaker in OPEN state from metrics dashboard |
| 09:52 | Checks Stripe status page - confirms degraded performance |
| 09:55 | Stripe performance recovers to normal latency |
| 09:57 | Circuit breaker transitions to HALF_OPEN, begins allowing test requests |
| 09:58 | Discovers connection pool is at 95% utilization despite Stripe recovery |
| 10:00 | Identifies leaked connections from timeout exceptions not releasing connections |
| 10:02 | Restarts payment service pods to reset connection pools |
| 10:05 | All pods healthy, error rate at normal levels |

## Root Cause

When the Stripe API became slow, payment requests timed out. The timeout exception handler in the payment adapter did not properly release the HTTP connection back to the pool. Each timed-out request leaked one connection. After approximately 7 minutes, the connection pool (size 20) was exhausted, causing all subsequent payment requests to fail even after Stripe recovered.

The connection leak was in this code path:

```python
# BEFORE (buggy)
def charge(self, amount: float) -> str:
    conn = self.pool.get_connection()
    try:
        response = conn.post("/charges", json={"amount": amount}, timeout=5)
        return response.json()["id"]
    except TimeoutError:
        raise PaymentTimeoutError("Stripe timeout")
    # BUG: connection not returned to pool on timeout
```

```python
# AFTER (fixed)
def charge(self, amount: float) -> str:
    conn = self.pool.get_connection()
    try:
        response = conn.post("/charges", json={"amount": amount}, timeout=5)
        return response.json()["id"]
    except TimeoutError:
        raise PaymentTimeoutError("Stripe timeout")
    finally:
        self.pool.release_connection(conn)  # Always release
```

## Five Whys

1. **Why did payments fail?** Connection pool was exhausted.
2. **Why was the pool exhausted?** Connections were not returned after timeout exceptions.
3. **Why were connections not returned?** The exception handler did not include a `finally` block to release the connection.
4. **Why was this not caught in testing?** Integration tests did not simulate timeout scenarios with connection pool exhaustion.
5. **Why was connection pool utilization not monitored?** Pool metrics were collected but no alert was configured for high utilization.

## Action Items

| Action | Owner | Due Date | Status |
|--------|-------|----------|--------|
| Fix connection leak with `finally` block | Alice | 2026-02-11 | Done |
| Add integration test for timeout + pool exhaustion | Bob | 2026-02-14 | Done |
| Add alert for connection pool utilization > 80% | Carol | 2026-02-14 | Done |
| Add connection pool size to Grafana dashboard | Carol | 2026-02-17 | Not started |
| Review all HTTP client code for similar leak patterns | Dave | 2026-02-21 | Not started |

## Lessons Learned

### What went well

- Alert fired within 2 minutes of impact
- On-call responded within 2 minutes
- Root cause identified within 16 minutes
- Pod restart was an effective short-term mitigation

### What could be improved

- Connection pool metrics should have an alert threshold
- Integration tests should cover timeout and resource exhaustion scenarios
- The `finally` pattern should be enforced via a custom linter rule or code review checklist
