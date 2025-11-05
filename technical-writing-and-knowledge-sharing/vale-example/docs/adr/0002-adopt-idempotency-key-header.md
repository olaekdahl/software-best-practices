---
status: "accepted"
date: 2025-11-04
decision-makers: [Team]
consulted: []
informed: []
---

# ADR 0002: Adopt Idempotency-Key header for POST /jobs

## Context and Problem Statement

Clients may retry POST /jobs due to network hiccups or timeouts. Without protection, retries can create duplicate jobs and inconsistent state. We need a simple, client-driven idempotency strategy for job submission.

## Decision Drivers

- Safe, repeatable POST semantics to avoid duplicates
- Simple DX for clients and server
- Works with common HTTP tooling and proxies
- Traceable in logs/metrics

## Considered Options

1. Require an Idempotency-Key request header (string token supplied by client)
2. Put an idempotency token in the request body
3. Server-generated tokens with ETag/If-Match or Location-based retries
4. Do nothing (no idempotency for POST)

## Decision Outcome

Chosen option: "Idempotency-Key header", because this is widely adopted in APIs, easy for clients to implement, and straightforward to enforce server-side by storing the first result under the given key.

### Consequences

* Good, because duplicate POSTs with the same key return the original result (200), first request returns 201
* Good, because easy to audit via headers in logs
* Good, because minimal change to request/response bodies
* Bad, because clients must generate and persist keys per logical operation
* Bad, because keys must be unique and sufficiently random to avoid collisions

### Confirmation

* Automated test or curl verification: repeat POST with the same `Idempotency-Key` returns 200 with the same job id.
* OpenAPI linter verifies header presence on POST /jobs.

## Pros and Cons of the Options

### 1. Idempotency-Key header
- Pros:
  - De facto pattern in many public APIs
  - No schema changes; easy cache/trace via headers
  - Server can use a small key→job map with TTL
- Cons:
  - Requires client discipline to generate/store keys

### 2. Token in request body
- Pros:
  - Explicit in schema (visible in OpenAPI and validation)
- Cons:
  - Bloats the body model; still requires identical semantics as a header

### 3. Server-generated tokens (ETag/If-Match or Location follow-ups)
- Pros:
  - Puts less onus on clients for token generation
- Cons:
  - More round-trips and complexity
  - Not as obvious for simple job submission flows

### 4. No idempotency for POST
- Pros:
  - No extra work
- Cons:
  - Duplicate jobs on retry; poor operational safety

## More Information

Implementation: `app.py` (header alias: `Idempotency-Key`)

OpenAPI spec: `api-design/jobs-api.yaml` (header parameter on POST /jobs)

Reference: Stripe’s Idempotency Keys (<https://stripe.com/docs/idempotency>)
