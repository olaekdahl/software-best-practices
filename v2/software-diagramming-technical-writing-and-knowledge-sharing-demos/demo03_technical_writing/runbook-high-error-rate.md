# Runbook: High Error Rate - Order Service

**Service:** order-service
**Last Updated:** 2026-02-01
**Owner:** Platform Team (@platform-team)
**Slack Channel:** #order-service-incidents
**PagerDuty Service:** Order Service Production

---

## Symptoms

- Alert `order_service_error_rate_high` fires (>5% 5xx responses for 5 minutes)
- Customer reports: "Payment failed" or "Order could not be placed"
- Grafana: Error rate spike on the Order Service dashboard
- Downstream: Notification Service may also show elevated error rates

## Severity Assessment

| Condition | Severity | Response Time |
|-----------|----------|---------------|
| Error rate >10%, affecting >100 users/min | SEV1 | 5 minutes |
| Error rate 5-10%, some users affected | SEV2 | 15 minutes |
| Error rate 1-5%, intermittent errors | SEV3 | 1 hour |
| Error rate <1%, isolated incidents | SEV4 | Next business day |

---

## Investigation Steps

### Step 1: Verify the alert is real

Check whether the alert is genuine or caused by a monitoring issue.

```bash
# Check current error rate (Prometheus)
curl -s 'http://prometheus:9090/api/v1/query?query=rate(http_requests_total{service="order-service",status=~"5.."}[5m])' | jq '.data.result[0].value[1]'

# Check service health endpoint
curl -s http://order-service:8000/health | jq .

# Check pod status
kubectl get pods -l app=order-service -n marketplace
```

**Expected:** Error rate above threshold. Health endpoint may return `degraded` or `unhealthy` status.

**If alert is false positive:** Acknowledge the alert and investigate the monitoring configuration.

### Step 2: Check recent deployments

A bad deployment is the most common cause of sudden error rate spikes.

```bash
# List recent deployments
kubectl rollout history deployment/order-service -n marketplace

# Check when the last deployment happened
kubectl describe deployment/order-service -n marketplace | grep -A5 "Events:"

# Compare error rate timing with deploy timing
# If errors started within 15 minutes of a deploy -> likely the cause
```

**If caused by a bad deploy:**

```bash
# Rollback immediately
kubectl rollout undo deployment/order-service -n marketplace

# Verify rollback
kubectl rollout status deployment/order-service -n marketplace

# Confirm error rate is dropping
# Wait 2-3 minutes and re-check the dashboard
```

### Step 3: Check database connectivity

Database connection pool exhaustion is a common failure mode.

```bash
# Check if pods can connect to the database
kubectl exec -it deploy/order-service -n marketplace -- python -c "
from app.infrastructure.database import engine
with engine.connect() as conn:
    result = conn.execute('SELECT 1')
    print('DB connection OK:', result.scalar())
"

# Check active connections on PostgreSQL
kubectl exec -it deploy/postgres -n marketplace -- psql -U orders -c "
SELECT count(*) as active, state
FROM pg_stat_activity
WHERE datname = 'orders'
GROUP BY state;
"

# Check connection pool metrics
curl -s http://order-service:8000/metrics | grep pool
```

**If connection pool is exhausted:**

- Restart pods to reset connections: `kubectl rollout restart deployment/order-service -n marketplace`
- Check for long-running queries: `SELECT pid, now() - pg_stat_activity.query_start AS duration, query FROM pg_stat_activity WHERE state = 'active' ORDER BY duration DESC LIMIT 5;`
- Consider increasing pool size if the issue recurs

### Step 4: Check dependencies

```bash
# Redis connectivity
kubectl exec -it deploy/order-service -n marketplace -- python -c "
import redis
r = redis.Redis.from_url('redis://redis:6379/0')
print('Redis PING:', r.ping())
print('Redis INFO memory:', r.info('memory')['used_memory_human'])
"

# RabbitMQ connectivity and queue depth
kubectl exec -it deploy/order-service -n marketplace -- python -c "
import pika
conn = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
channel = conn.channel()
q = channel.queue_declare('order_events', passive=True)
print('Queue depth:', q.method.message_count)
conn.close()
"

# Stripe API health
curl -s https://status.stripe.com/api/v2/status.json | jq '.status.indicator'
```

**If a dependency is down:**

- **Redis down:** Orders still work but will be slower (cache miss). Not usually SEV1.
- **RabbitMQ down:** Events will not publish. Enable circuit breaker fallback. Order creation still works but notifications and downstream processing will be delayed.
- **Stripe down:** Payment processing fails. This is SEV1 if it affects order submission. Check [Stripe Status](https://status.stripe.com/) and enable maintenance mode if prolonged.

### Step 5: Check application logs

```bash
# Recent error logs (last 30 minutes)
kubectl logs deploy/order-service -n marketplace --since=30m | grep '"level":"ERROR"' | tail -20

# Look for specific error patterns
kubectl logs deploy/order-service -n marketplace --since=30m | grep -i "connection\|timeout\|refused\|deadlock" | tail -10

# Check for OOM kills
kubectl get events -n marketplace --sort-by='.lastTimestamp' | grep -i "oom\|kill\|evict"
```

### Step 6: Mitigate

Based on findings, take the appropriate action:

| Root Cause | Mitigation |
|------------|------------|
| Bad deployment | Rollback: `kubectl rollout undo deployment/order-service` |
| DB connection pool exhaustion | Restart pods, investigate long-running queries |
| Dependency (Redis/RabbitMQ) down | Enable circuit breaker, restart dependency |
| Stripe outage | Enable maintenance mode for payments, communicate to customers |
| Memory pressure / OOM | Increase resource limits, investigate memory leak |
| Traffic spike (legitimate) | Scale up: `kubectl scale deployment/order-service --replicas=6` |
| Traffic spike (attack) | Enable rate limiting at API gateway level |

---

## Escalation

| Severity | Action |
|----------|--------|
| SEV1 | Page on-call engineer via PagerDuty. Notify engineering manager. Update status page within 15 minutes. |
| SEV2 | Page on-call engineer. Notify team lead in Slack. |
| SEV3 | Post in #order-service-incidents. Assign to next sprint if not resolved within 1 hour. |
| SEV4 | Create a ticket. Address during normal business hours. |

## Post-Incident

- [ ] Timeline documented in the incident Slack channel
- [ ] Postmortem scheduled within 48 hours
- [ ] Action items created in Jira with owners and due dates
- [ ] Status page updated with resolution
- [ ] Alert thresholds reviewed and adjusted if needed
