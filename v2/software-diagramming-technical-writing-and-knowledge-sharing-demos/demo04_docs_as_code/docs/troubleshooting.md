# Troubleshooting

Common issues and their solutions for the Order Service.

## Application Won't Start

### Port already in use

```
ERROR: [Errno 98] Address already in use
```

**Solution:** Another process is using port 8000. Find and stop it:

```bash
# Find the process
lsof -i :8000

# Kill it
kill -9 <PID>

# Or use a different port
uvicorn app.main:app --port 8001
```

### Database connection refused

```
sqlalchemy.exc.OperationalError: could not connect to server: Connection refused
```

**Solution:** Ensure PostgreSQL is running:

```bash
# Check if Docker containers are up
docker compose ps

# Restart if needed
docker compose down && docker compose up -d

# Verify the connection string
echo $DATABASE_URL
```

### Redis connection error

```
redis.exceptions.ConnectionError: Error connecting to localhost:6379
```

**Solution:** Ensure Redis is running via Docker Compose. If you do not need caching during development, set `REDIS_ENABLED=false` in your `.env` file.

## API Errors

### 401 Unauthorized

Your JWT token is missing, expired, or invalid.

```bash
# Check token expiration
python -c "import jwt; print(jwt.decode('YOUR_TOKEN', options={'verify_signature': False}))"

# Generate a new token
curl -X POST http://localhost:8000/v1/auth/token \
  -d '{"username": "admin", "password": "admin"}'
```

### 422 Unprocessable Entity

Request body validation failed. Check the error response for details:

```json
{
  "detail": [
    {
      "loc": ["body", "items", 0, "quantity"],
      "msg": "ensure this value is greater than 0",
      "type": "value_error.number.not_gt"
    }
  ]
}
```

### 429 Too Many Requests

You have exceeded the rate limit. Wait and retry, or request a higher rate limit.

## Performance Issues

### Slow order listing

If `/v1/orders` is slow, check:

1. **Missing index:** Run `alembic upgrade head` to ensure all migrations are applied
2. **Large result set:** Use pagination parameters (`cursor` and `limit`)
3. **Cache miss:** Check Redis connectivity - cache reduces DB load significantly

### High memory usage

Check for connection leaks:

```bash
# Check active DB connections
kubectl exec -it deploy/order-service -- python -c "
from app.infrastructure.database import engine
print('Pool size:', engine.pool.size())
print('Checked out:', engine.pool.checkedout())
"
```

## Getting Help

- **Slack:** #order-service-dev
- **On-call:** Check [PagerDuty](https://acme.pagerduty.com) for the current on-call engineer
- **Docs:** [Internal wiki](https://wiki.acme.com/order-service)
