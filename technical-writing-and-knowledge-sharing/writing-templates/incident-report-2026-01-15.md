# Incident Report: Payment Processing Failure

**Incident ID:** INC-2026-0115
**Date:** 2026-01-15
**Duration:** 47 minutes (14:23 UTC - 15:10 UTC)
**Severity:** SEV1
**Status:** Resolved
**Author:** Alice Chen (on-call engineer)

---

## Summary

For 47 minutes on January 15, 2026, customers were unable to complete order payments. Approximately 1,200 orders failed during this window. The root cause was a database connection pool exhaustion triggered by a long-running analytics query that held connections open.

## Impact

- **Users affected:** Approximately 3,400 customers experienced payment failures
- **Orders lost:** 1,200 orders failed (estimated $84,000 in revenue at risk)
- **Recovery rate:** 78% of affected customers retried successfully after resolution
- **SLO breach:** Availability dropped to 94.2% (SLO target: 99.9%)

## Timeline

All times in UTC.

| Time | Event |
|------|-------|
| 14:15 | Analytics team runs a large report query against the production order database |
| 14:23 | `order_service_error_rate_high` alert fires (5xx rate > 5%) |
| 14:25 | On-call engineer (Alice) acknowledges the alert |
| 14:28 | Alice checks deployment history - no recent deploys |
| 14:32 | Alice checks database connections - connection pool at 100% utilization |
| 14:35 | Alice identifies a long-running query from the analytics service holding 15 connections |
| 14:38 | Alice terminates the analytics query |
| 14:40 | Connection pool begins recovering, error rate drops to 3% |
| 14:42 | Alice restarts 2 order-service pods to reset their connection pools |
| 14:45 | Error rate drops below 1% |
| 14:50 | All pods healthy, error rate at normal levels |
| 15:10 | Alice confirms sustained recovery, closes the incident |

## Root Cause

The analytics team ran a report query that performed a sequential scan across the entire `orders` table (12M rows) with multiple JOINs. This query:

1. Acquired 15 database connections from the shared connection pool
2. Held each connection for over 8 minutes (the pool timeout is 30 seconds for application queries)
3. Exhausted the remaining connections available to the order service
4. Caused all new order and payment requests to fail with "connection pool exhausted" errors

The analytics query was run against the primary database because the read replica was not configured for the analytics service.

## Contributing Factors

- The analytics service connects to the primary database instead of a read replica
- No per-service connection limits - all services share one connection pool
- The long-running query did not have a statement timeout configured
- No alerting on connection pool utilization (only on HTTP error rates)

## Resolution

Immediate:

1. Terminated the long-running analytics query
2. Restarted order service pods to reset connection pools

Follow-up actions:

| Action Item | Owner | Due Date | Status |
|-------------|-------|----------|--------|
| Configure analytics service to use read replica | Bob (DBA) | 2026-01-22 | Done |
| Set `statement_timeout = 60s` for analytics DB role | Bob (DBA) | 2026-01-22 | Done |
| Add per-service connection pool limits (max 20 per service) | Alice (Platform) | 2026-01-29 | In progress |
| Add Prometheus alert for connection pool utilization > 80% | Carol (SRE) | 2026-01-29 | Done |
| Document runbook for connection pool exhaustion | Alice (Platform) | 2026-02-05 | Not started |

## Five Whys

1. **Why did orders fail?** Because the database connection pool was exhausted.
2. **Why was the pool exhausted?** Because a long-running analytics query held 15 connections for 8+ minutes.
3. **Why did the analytics query use the primary database?** Because the analytics service was never configured to use the read replica.
4. **Why wasn't there a query timeout?** Because statement timeouts were not configured for any database role.
5. **Why didn't we detect the pool exhaustion earlier?** Because we only alerted on HTTP error rates, not on connection pool utilization.

## Lessons Learned

### What went well

- Alert fired within 2 minutes of impact starting
- On-call engineer responded and began investigation within 5 minutes
- Root cause was identified within 10 minutes
- Total time to resolution was 47 minutes (target for SEV1: < 60 minutes)

### What could be improved

- We should have detected the connection pool issue before it caused customer-facing errors
- Read replica configuration should be part of our service onboarding checklist
- Statement timeouts should be a default configuration, not something teams opt into

## References

- [Incident Slack thread](https://acme.slack.com/archives/C0123/p1705325000)
- [Grafana dashboard during incident](https://grafana.acme.com/d/order-svc?from=1705323780&to=1705328400)
- [PostgreSQL connection pooling docs](https://www.postgresql.org/docs/16/runtime-config-connection.html)
