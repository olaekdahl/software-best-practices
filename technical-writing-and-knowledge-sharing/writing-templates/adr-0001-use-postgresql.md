# ADR-0001: Use PostgreSQL for Order Service Data Store

**Date:** 2026-01-10
**Status:** Accepted
**Deciders:** Backend team, Architecture board

## Context

The order service needs a persistent data store. Our requirements are:

- ACID transactions for order state management (orders move through a state machine and must not end up in inconsistent states)
- Complex queries for reporting (order history, analytics, revenue dashboards)
- The team must be able to operate and maintain it in production
- Must support at least 500 writes/sec and 2,000 reads/sec at launch

We currently run PostgreSQL 16 for three other services (user, product, inventory), so the team has existing operational experience with it.

## Decision

Use PostgreSQL 16 as the primary data store for the order service. Use SQLAlchemy as the ORM with Alembic for schema migrations.

## Alternatives Considered

### MongoDB

Pros:

- Flexible schema - easy to evolve order document structure
- Built-in horizontal scaling with sharding
- JSON-native storage aligns with our API payloads

Cons:

- No multi-document ACID transactions for cross-collection writes (critical for order + payment atomicity)
- Team has no production MongoDB experience
- Schema flexibility can lead to inconsistent data over time without strict validation

### DynamoDB

Pros:

- Fully managed - no database administration overhead
- Consistent single-digit-millisecond latency at any scale
- Pay-per-request pricing model fits unpredictable traffic patterns

Cons:

- Limited query flexibility - requires designing access patterns upfront
- Complex data modeling for relational data (orders + items + payments)
- Vendor lock-in to AWS
- No local development environment without LocalStack

### SQLite (for early stage)

Pros:

- Zero operational overhead
- Embedded, no network latency
- Perfect for prototyping

Cons:

- Single-writer concurrency model does not scale
- No network access for multiple service instances
- Migration to PostgreSQL later would be a disruptive change

## Consequences

- Team needs PostgreSQL operational knowledge (already present)
- Schema migrations required for data model changes (Alembic handles this)
- ACID transactions simplify order state management
- Rich query support enables reporting without a separate analytics system
- Connection pool sizing becomes a capacity planning concern (use PgBouncer if needed)
- We accept the operational cost of running PostgreSQL vs. a fully managed option

## References

- [PostgreSQL 16 Release Notes](https://www.postgresql.org/docs/16/release-16.html)
- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/20/)
- [Alembic Migration Tool](https://alembic.sqlalchemy.org/)
- [ADR GitHub Organization](https://adr.github.io/)
- Michael Nygard, ["Documenting Architecture Decisions"](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions)
