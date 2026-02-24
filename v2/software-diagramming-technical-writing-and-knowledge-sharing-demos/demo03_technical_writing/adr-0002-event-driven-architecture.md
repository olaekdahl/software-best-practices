# ADR-0002: Adopt Event-Driven Architecture for Inter-Service Communication

**Date:** 2026-01-22
**Status:** Accepted
**Deciders:** Backend team, Architecture board, SRE team
**Supersedes:** ADR-0000 (synchronous REST between all services)

## Context

Our marketplace has grown to 6 microservices that communicate via synchronous REST calls. We are experiencing:

- **Cascading failures:** When the payment service is slow, the order service times out, which causes the API gateway to return 504s to customers
- **Tight coupling:** Adding a new notification channel (SMS, push) requires modifying the order service code
- **Scaling bottlenecks:** The notification service cannot keep up with order volume during flash sales, causing email delays of 15+ minutes
- **Deployment dependencies:** We cannot deploy the order service without also testing its integration with payment, inventory, and notification services

## Decision

Adopt an event-driven architecture using RabbitMQ as the message broker for inter-service communication. Services will publish domain events (e.g., `OrderConfirmed`, `PaymentFailed`) and other services will subscribe to events they care about.

Synchronous REST will remain for:

- Client-to-gateway communication
- Queries that require immediate responses (e.g., "get order status")
- Health checks and service discovery

The outbox pattern will be used to ensure reliable event publishing (write event to DB in the same transaction as the state change, then publish from the outbox asynchronously).

## Alternatives Considered

### Apache Kafka

Pros:

- Higher throughput (millions of messages/sec)
- Built-in event replay from offset
- Durable log retention for event sourcing

Cons:

- Significant operational complexity (ZooKeeper/KRaft, partition management)
- Overkill for our current volume (approximately 1,000 events/sec peak)
- Steeper learning curve for the team
- Ordering guarantees require careful partition key design

### AWS SNS/SQS

Pros:

- Fully managed, no infrastructure to operate
- Native dead-letter queue support
- Pay-per-message pricing

Cons:

- Vendor lock-in to AWS
- Message size limits (256KB) may be restrictive for rich events
- No local development without LocalStack
- Limited routing flexibility compared to RabbitMQ exchanges

### Keep Synchronous REST (Status Quo)

Pros:

- Simple mental model, team is experienced
- Easy to debug with standard HTTP tooling
- No message broker infrastructure to maintain

Cons:

- Cascading failure risk remains and will worsen as we add services
- Tight coupling prevents independent deployment
- Cannot absorb traffic spikes without over-provisioning all services

## Consequences

### Positive

- Services are decoupled - the order service publishes `OrderConfirmed` without knowing who consumes it
- New consumers (analytics, fraud detection) can subscribe without modifying the publisher
- Traffic spikes are absorbed by the queue - consumers process at their own pace
- Partial system degradation is possible (email delays are better than order failures)

### Negative

- Eventual consistency - notifications may arrive seconds after the order is confirmed
- Debugging distributed flows requires correlation IDs and distributed tracing
- Message ordering is not guaranteed across queues (must design for idempotency)
- Team needs to learn RabbitMQ operations (monitoring, dead-letter handling, cluster management)
- Outbox pattern adds complexity to the write path

### Risks

- If the RabbitMQ cluster goes down, events are delayed (mitigated by clustering and disk-based persistence)
- Poison messages can block a queue (mitigated by dead-letter queues and retry limits)

## References

- [RabbitMQ Documentation](https://www.rabbitmq.com/docs)
- [Enterprise Integration Patterns](https://www.enterpriseintegrationpatterns.com/)
- [Transactional Outbox Pattern](https://microservices.io/patterns/data/transactional-outbox.html)
- Martin Fowler, ["What do you mean by Event-Driven?"](https://martinfowler.com/articles/201701-event-driven.html)
- Gregor Hohpe, *Enterprise Integration Patterns* (Addison-Wesley, 2003)
