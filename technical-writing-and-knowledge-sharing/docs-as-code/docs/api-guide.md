API Guide

This document describes the Order Service API endpoints.    

## Authentication

All endpoints require a valid JWT token in the Authorization header.
See https://jwt.io for more info on JWT tokens.

##Endpoints

### Create Order

```
POST /v1/orders
```

TODO: Add request body schema

### List Orders

```
GET /v1/orders
```

Returns a paginated list of orders. Supports cursor-based pagination.

### Get Order

```
GET /v1/orders/{id}
```

Returns a single order by ID. Returns 404 if the order does not exist. This is a very long line that exceeds the recommended line length for markdown documentation files which should generally be kept under 120 characters for readability.

### Submit Order

```
POST /v1/orders/{id}/submit
```

Submits an order for payment processing. The order must be in DRAFT status. If the order has already been submitted or cancelled, a 409 Conflict response is returned with a RFC 7807 problem detail.

### Cancel Order

```
POST /v1/orders/{id}/cancel
```

Cancels an order. Only allowed within 1 hour of confirmation. See the order service configuraiton for timeout settings.

## Error Handling

All errors follow the RFC 7807 Problem Detail format:

```json
{
  "type": "https://api.acme.com/problems/order-not-found",
  "title": "Order Not Found",
  "status": 404,
  "detail": "Order ord-123 does not exist"
}
```

## Rate Limits

API rate limits are enforced per API key:

| Plan | Requests/min |
|------|-------------|
| Free | 60 |
| Pro | 600 |
| Enterprise | 6000 |
