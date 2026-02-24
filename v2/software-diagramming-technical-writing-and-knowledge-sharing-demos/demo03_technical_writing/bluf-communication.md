# BLUF Communication: Bottom Line Up Front

BLUF is a military-originated writing technique that puts the most important information first. Engineers reading your messages are busy - respect their time by leading with the conclusion.

---

## Bad Example: Bottom-Up (Traditional)

> **Subject: Caching evaluation update**
>
> Hi team,
>
> Over the past quarter we've been evaluating several caching solutions for our order service. The team reviewed Redis, Memcached, and Hazelcast across criteria including performance, operational complexity, ecosystem support, and cost.
>
> We started by benchmarking Memcached. It showed impressive raw throughput for simple key/value operations - about 15% faster than Redis for GET/SET operations. However, our workload requires sorted sets for leaderboards, pub/sub for cache invalidation, and Lua scripting for atomic operations that Memcached does not support.
>
> Next we evaluated Hazelcast. The distributed computing features are powerful, particularly the near-cache pattern that reduces network hops. However, the JVM dependency adds operational complexity and the team has no existing JVM expertise. License costs for the enterprise features we'd need run $45K/year.
>
> Finally, we benchmarked Redis. It delivered sub-millisecond p99 latency under our production workload simulation (10K ops/sec). The rich data structure support covers all our use cases. Three team members already have production Redis experience from previous roles.
>
> Cost comparison: Redis (open source, self-hosted on existing infra) vs. Hazelcast ($45K/year) vs. Memcached (free but requires custom workarounds for our data structure needs).
>
> Therefore, we recommend Redis as our caching layer for the order service.
>
> Let me know if you have questions.

**Problem:** The reader has to scroll through 4 paragraphs before finding the recommendation. If they are triaging 50 emails, they might not reach the conclusion at all.

---

## Good Example: BLUF (Top-Down)

> **Subject: DECISION: Use Redis as order service caching layer**
>
> **BOTTOM LINE:** We recommend Redis as the caching layer for the order service. Sub-millisecond p99 latency, rich data structures (sorted sets, pub/sub, Lua scripting), and existing team expertise make it the strongest choice.
>
> **What we need from you:** Approve the architecture decision by Friday so we can begin implementation in Sprint 14.
>
> ### Alternatives considered
>
> | Criteria | Redis | Memcached | Hazelcast |
> |----------|-------|-----------|-----------|
> | p99 latency | <1ms | <1ms | ~2ms |
> | Data structures | Rich (sorted sets, pub/sub, Lua) | Key/value only | Rich |
> | Team expertise | 3 engineers experienced | 1 engineer | None |
> | Annual cost | $0 (self-hosted) | $0 (self-hosted) | $45K license |
> | Operational complexity | Low | Low | High (JVM) |
>
> ### Next steps
>
> 1. Approve ADR-0042 (attached) by Friday Feb 28
> 2. Set up Redis cluster in staging - Sprint 14
> 3. Migrate order service cache - Sprint 15
> 4. Monitor and tune - Sprint 16
>
> Full evaluation details: [Confluence page](https://internal.wiki/caching-eval)

**Why this works:**

- Subject line signals the message type (DECISION vs. FYI vs. ACTION REQUIRED)
- First sentence delivers the conclusion
- Second sentence says what action is needed
- Supporting details follow for those who want depth
- Comparison table makes alternatives scannable
- Clear next steps with owners and dates

---

## BLUF Template

```
Subject: [ACTION REQUIRED | DECISION | FYI]: One-line summary

BOTTOM LINE: [One to two sentences with the conclusion or recommendation.]

WHAT YOU NEED TO DO: [Clear action items with deadlines, if applicable.]

BACKGROUND: [Supporting details, data, context - for those who want to go deeper.]

NEXT STEPS: [Numbered list of what happens next, with owners and dates.]
```

---

## When to Use BLUF

- Status updates to leadership
- Architecture decision announcements
- Incident notifications
- Cross-team requests
- Any message where the reader needs the key takeaway fast

## When BLUF Might Not Fit

- Persuasive arguments where you need to build a case first
- Tutorials and guides where context is needed before the punchline
- Sensitive personnel communications
