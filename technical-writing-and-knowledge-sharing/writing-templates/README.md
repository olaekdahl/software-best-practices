# Demo 03 - Technical Writing: BLUF, ADRs, READMEs, Runbooks

## Purpose

Demonstrate the most important technical writing formats developers use day-to-day. Each file is a standalone example that can be used as a starting template.

## Instructor Notes

- Open each markdown file and walk through its structure
- For BLUF: show both the bad (bottom-up) and good (top-down) versions side by side
- For ADRs: emphasize that the real value is in "Alternatives Considered" and "Consequences"
- For the README: point out how it serves both "one-minute skimmers" and "deep-divers"
- For the runbook: have a student role-play following the steps during a simulated incident
- For the incident report: discuss why blameless language matters

## Files

| File | What It Demonstrates |
|------|---------------------|
| `bluf-communication.md` | BLUF (Bottom Line Up Front) writing with side-by-side comparison |
| `adr-0001-use-postgresql.md` | ADR (Architecture Decision Record) for a database choice |
| `adr-0002-event-driven-architecture.md` | ADR for adopting event-driven patterns |
| `project-readme.md` | Well-structured project README template |
| `runbook-high-error-rate.md` | On-call runbook with step-by-step investigation |
| `incident-report-2026-01-15.md` | Blameless postmortem / incident report |
| `api-changelog.md` | Changelog following conventional commit format |

## Key Takeaways

1. **BLUF** - Lead with the conclusion, not the journey. Respect the reader's time.
2. **ADRs** - Record WHY decisions were made. Future you will thank present you.
3. **READMEs** - Serve both skimmers (Quick Start) and deep-divers (Architecture, Config).
4. **Runbooks** - Step-by-step with copy-pasteable commands. No ambiguity during an incident.
5. **Keep docs next to code** - Same repo, same PR, same review process.
6. **Review docs like code** - Style, accuracy, completeness, and freshness.
