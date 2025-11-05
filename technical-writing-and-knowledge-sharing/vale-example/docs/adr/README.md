# Architecture Decision Records (ADRs)

This folder contains ADRs written using the MADR format (<https://adr.github.io/madr/>).

## Index

- [ADR 0001: Adopt FastAPI and Redocly for API and Docs](0001-adopt-fastapi-and-redocly.md)
- [ADR 0002: Adopt Idempotency-Key header for POST /jobs](0002-adopt-idempotency-key-header.md)

## Template (MADR-style)

Copy this into a new file `NNNN-title.md` to create a new ADR.

```markdown
# ADR NNNN: Title

- Status: Proposed | Accepted | Deprecated | Superseded by NNNN
- Deciders: <names/roles>
- Date: YYYY-MM-DD

## Context and Problem Statement

What is the issue that we're seeing that is motivating this decision or change?

## Decision Drivers

- Driver 1
- Driver 2

## Considered Options

- Option A
- Option B
- Option C

## Decision Outcome

Chosen option: <option name>, because <reasons>.

### Positive Consequences

- Consequence A
- Consequence B

### Negative Consequences

- Consequence C

## Pros and Cons of the Options

### Option A
- Pros:
- Cons:

### Option B
- Pros:
- Cons:

### Option C
- Pros:
- Cons:

## Links

- Related ADRs: NNNN
- References: links
```
