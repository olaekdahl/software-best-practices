# Playbook: High Error Rate

**Service:** order-service
**Alert:** `order_service_error_rate_high`
**Trigger:** 5xx error rate > 5% for 5 minutes

---

## Quick Assessment

```bash
# 1. Verify the alert
curl -s http://order-service:8000/health | jq .

# 2. Check pods
kubectl get pods -l app=order-service -n marketplace

# 3. Check recent deploys
kubectl rollout history deployment/order-service -n marketplace | tail -5
```

## Decision Tree

```
Error rate > 5%?
  |
  +-- Recent deploy (< 30 min)?
  |     YES -> Rollback: kubectl rollout undo deployment/order-service
  |     NO  -> Continue
  |
  +-- Health endpoint returns "unhealthy"?
  |     YES -> Check dependency health (Step 2)
  |     NO  -> Check application logs (Step 3)
  |
  +-- Is it a dependency issue?
  |     DB down    -> Restart pods, check connection pool
  |     Redis down -> Non-critical, monitor
  |     Stripe down -> Enable maintenance mode
  |     RabbitMQ   -> Events delayed, not blocking
  |
  +-- Is it a traffic spike?
        Legitimate -> Scale up: kubectl scale --replicas=6
        Attack     -> Enable rate limiting at gateway
```

## Step 1: Check Recent Deploys

```bash
kubectl rollout history deployment/order-service -n marketplace

# If deployed within last 30 min, rollback:
kubectl rollout undo deployment/order-service -n marketplace
kubectl rollout status deployment/order-service -n marketplace
```

## Step 2: Check Dependencies

```bash
# Database
kubectl exec deploy/order-service -n marketplace -- \
  python -c "from app.db import engine; print(engine.connect().execute('SELECT 1').scalar())"

# Redis
kubectl exec deploy/order-service -n marketplace -- \
  python -c "import redis; print(redis.Redis().ping())"

# Check connection pool
curl -s http://order-service:8000/metrics | grep -E "pool_size|pool_checked"
```

## Step 3: Check Logs

```bash
# Recent errors
kubectl logs deploy/order-service -n marketplace --since=15m | \
  grep '"level":"ERROR"' | tail -20

# Connection/timeout errors
kubectl logs deploy/order-service -n marketplace --since=15m | \
  grep -iE "connection|timeout|refused|deadlock" | tail -10

# OOM events
kubectl get events -n marketplace --sort-by='.lastTimestamp' | \
  grep -i "oom\|killed"
```

## Step 4: Mitigate

| Cause | Action |
|-------|--------|
| Bad deploy | `kubectl rollout undo deployment/order-service` |
| DB pool exhaustion | Restart pods, check for long queries |
| Dependency down | Enable circuit breaker fallback |
| Memory pressure | Increase limits, investigate leak |
| Traffic spike | `kubectl scale deployment/order-service --replicas=6` |

## Step 5: Escalate if Needed

| Severity | Action |
|----------|--------|
| SEV1 (>10% errors, >100 users/min) | Page manager, update status page |
| SEV2 (5-10% errors) | Notify team lead in Slack |
| SEV3 (<5% errors) | Post in #incidents channel |
