"""
Demo 05 - Incident Response: Playbooks and Postmortems
=========================================================
Demonstrates runbook-driven incident response and blameless postmortems.

Instructor talking points:
- Playbooks reduce MTTR by removing guesswork
- Severity classification drives escalation
- Blameless postmortems focus on systems, not individuals
- Action items must be tracked and completed
- Practice incident response before you need it

Run: python main.py
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any


# ============================================================================
# Severity classification
# ============================================================================

class Severity(Enum):
    SEV1 = "SEV1"  # Total outage, revenue impact
    SEV2 = "SEV2"  # Major feature degraded
    SEV3 = "SEV3"  # Minor feature impacted
    SEV4 = "SEV4"  # Cosmetic / low impact


SEVERITY_THRESHOLDS = {
    Severity.SEV1: {"error_rate": 0.10, "latency_p99_ms": 5000, "availability": 0.95},
    Severity.SEV2: {"error_rate": 0.05, "latency_p99_ms": 2000, "availability": 0.99},
    Severity.SEV3: {"error_rate": 0.01, "latency_p99_ms": 1000, "availability": 0.999},
}


def classify_severity(error_rate: float, latency_p99: float, availability: float) -> Severity:
    """Classify incident severity based on impact metrics."""
    for sev, thresholds in SEVERITY_THRESHOLDS.items():
        if (error_rate >= thresholds["error_rate"]
                or latency_p99 >= thresholds["latency_p99_ms"]
                or availability <= thresholds["availability"]):
            return sev
    return Severity.SEV4


# ============================================================================
# Playbook / Runbook engine
# ============================================================================

@dataclass
class PlaybookStep:
    """A single step in a troubleshooting playbook."""
    id: int
    action: str
    expected_result: str
    escalation: str | None = None
    completed: bool = False
    result: str = ""
    duration_seconds: int = 0


@dataclass
class Playbook:
    """A troubleshooting playbook (runbook) for a specific scenario."""
    name: str
    trigger: str
    severity: Severity
    steps: list[PlaybookStep] = field(default_factory=list)
    started_at: str = ""
    completed_at: str = ""

    def execute(self, simulated_results: list[str] | None = None) -> None:
        """Execute playbook steps (simulated for demo)."""
        self.started_at = datetime.now().isoformat()
        print(f"\n  Executing playbook: {self.name}")
        print(f"  Trigger: {self.trigger}")
        print(f"  Severity: {self.severity.value}")
        print(f"  Steps: {len(self.steps)}")
        print()

        for i, step in enumerate(self.steps):
            step_start = time.perf_counter()
            print(f"    Step {step.id}: {step.action}")
            print(f"      Expected: {step.expected_result}")

            # Simulate execution
            time.sleep(0.01)
            if simulated_results and i < len(simulated_results):
                step.result = simulated_results[i]
            else:
                step.result = "Checked - OK"
            step.completed = True
            step.duration_seconds = max(1, int((time.perf_counter() - step_start) * 100))

            print(f"      Result:   {step.result}")
            if step.escalation and "FAIL" in step.result.upper():
                print(f"      ESCALATE: {step.escalation}")
            print()

        self.completed_at = datetime.now().isoformat()

    def summary(self) -> dict:
        return {
            "playbook": self.name,
            "severity": self.severity.value,
            "steps_total": len(self.steps),
            "steps_completed": sum(1 for s in self.steps if s.completed),
            "total_duration_s": sum(s.duration_seconds for s in self.steps),
        }


# ============================================================================
# Incident timeline
# ============================================================================

@dataclass
class TimelineEntry:
    timestamp: str
    actor: str
    action: str
    details: str = ""


@dataclass
class Incident:
    """Incident record for tracking and postmortem."""
    id: str
    title: str
    severity: Severity
    description: str
    impact: str
    timeline: list[TimelineEntry] = field(default_factory=list)
    root_cause: str = ""
    resolution: str = ""
    action_items: list[dict] = field(default_factory=list)
    detection_time: str = ""
    mitigation_time: str = ""
    resolution_time: str = ""

    def add_event(self, actor: str, action: str, details: str = "") -> None:
        self.timeline.append(TimelineEntry(
            timestamp=datetime.now().isoformat(),
            actor=actor,
            action=action,
            details=details,
        ))

    @property
    def time_to_detect(self) -> str:
        if not self.detection_time:
            return "N/A"
        return self.detection_time

    @property
    def time_to_mitigate(self) -> str:
        if not self.mitigation_time:
            return "N/A"
        return self.mitigation_time


# ============================================================================
# Postmortem generator
# ============================================================================

def generate_postmortem(incident: Incident) -> str:
    """Generate a blameless postmortem document."""
    lines = [
        f"# Postmortem: {incident.title}",
        f"",
        f"**Incident ID:** {incident.id}",
        f"**Severity:** {incident.severity.value}",
        f"**Date:** {datetime.now().strftime('%Y-%m-%d')}",
        f"**Status:** Resolved",
        f"",
        f"## Summary",
        f"",
        f"{incident.description}",
        f"",
        f"## Impact",
        f"",
        f"{incident.impact}",
        f"",
        f"## Timeline",
        f"",
    ]

    for entry in incident.timeline:
        lines.append(f"- **{entry.timestamp}** [{entry.actor}] {entry.action}")
        if entry.details:
            lines.append(f"  - {entry.details}")

    lines.extend([
        f"",
        f"## Root Cause",
        f"",
        f"{incident.root_cause}",
        f"",
        f"## Resolution",
        f"",
        f"{incident.resolution}",
        f"",
        f"## Key Metrics",
        f"",
        f"- Time to detect: {incident.time_to_detect}",
        f"- Time to mitigate: {incident.time_to_mitigate}",
        f"",
        f"## Action Items",
        f"",
    ])

    for item in incident.action_items:
        lines.append(f"- [{item.get('priority', 'P2')}] {item['action']} "
                      f"(Owner: {item.get('owner', 'TBD')}, "
                      f"Due: {item.get('due', 'TBD')})")

    lines.extend([
        f"",
        f"## Lessons Learned",
        f"",
        f"### What went well",
        f"- Playbook was followed, reducing resolution time",
        f"- Communication was clear across teams",
        f"",
        f"### What could be improved",
        f"- Detection was delayed due to missing alerts",
        f"- Playbook needs an additional step for this scenario",
        f"",
        f"## Five Whys",
        f"",
        f"1. Why did the service go down?",
        f"   -> Database connection pool was exhausted",
        f"2. Why was the pool exhausted?",
        f"   -> A slow query held connections for too long",
        f"3. Why was the query slow?",
        f"   -> Missing index on a frequently queried column",
        f"4. Why was the index missing?",
        f"   -> Migration was written but not applied in production",
        f"5. Why was the migration not applied?",
        f"   -> No automated migration check in the deploy pipeline",
    ])

    return "\n".join(lines)


# ============================================================================
# Main demo
# ============================================================================

def main():
    print("=== Demo: Incident Response and Postmortems ===\n")

    # --- Step 1: Classify severity ---
    print("--- Step 1: Severity Classification ---\n")
    scenarios = [
        ("Payment API down", 0.15, 6000, 0.92),
        ("Search slow", 0.02, 1500, 0.995),
        ("Dark mode broken", 0.001, 200, 0.9999),
    ]
    for name, err, lat, avail in scenarios:
        sev = classify_severity(err, lat, avail)
        print(f"  {name}: err={err:.1%}, p99={lat}ms, avail={avail:.2%} -> {sev.value}")
    print()

    # --- Step 2: Execute playbook ---
    print("--- Step 2: Execute Playbook ---")
    playbook = Playbook(
        name="Database Connection Pool Exhaustion",
        trigger="Error rate >5% AND db_connections utilization >90%",
        severity=Severity.SEV2,
        steps=[
            PlaybookStep(1, "Check DB connection pool metrics",
                         "Utilization <80%, queue depth 0",
                         escalation="Page DBA on-call"),
            PlaybookStep(2, "Check for long-running queries",
                         "No queries >30s",
                         escalation="Identify and kill blocking query"),
            PlaybookStep(3, "Check recent deployments",
                         "No deploys in last 2 hours"),
            PlaybookStep(4, "Increase pool size (temporary)",
                         "Pool increased, connections stabilize"),
            PlaybookStep(5, "Verify error rates recovering",
                         "Error rate <1% within 5 minutes"),
        ],
    )

    playbook.execute([
        "FAIL: Utilization 94%, queue depth 23",
        "FAIL: Query on orders table running 120s",
        "Deploy v2.3.1 at 14:30 - added new report query",
        "Pool increased from 50 to 100",
        "Error rate dropped to 0.3%",
    ])

    print(f"  Playbook summary: {playbook.summary()}")
    print()

    # --- Step 3: Build incident record ---
    print("--- Step 3: Incident Timeline ---\n")
    incident = Incident(
        id="INC-2025-042",
        title="Payment Service Degradation Due to DB Pool Exhaustion",
        severity=Severity.SEV2,
        description=(
            "Payment service experienced elevated error rates (12%) "
            "due to database connection pool exhaustion. A new reporting "
            "query introduced in v2.3.1 held connections for >120 seconds, "
            "starving the pool."
        ),
        impact=(
            "12% of payment requests failed for 45 minutes. "
            "Estimated 340 failed transactions affecting ~280 customers."
        ),
    )

    # Build timeline
    incident.add_event("AlertManager", "Alert fired",
                       "payment_error_rate > 5% for 5 minutes")
    incident.detection_time = "5 minutes"
    incident.add_event("On-call (Jane)", "Acknowledged alert")
    incident.add_event("On-call (Jane)", "Started playbook: DB Pool Exhaustion")
    incident.add_event("On-call (Jane)", "Identified slow query from v2.3.1 deploy")
    incident.add_event("On-call (Jane)", "Killed blocking query")
    incident.add_event("DBA (Mike)", "Increased pool size 50 -> 100")
    incident.mitigation_time = "25 minutes"
    incident.add_event("On-call (Jane)", "Error rates recovered to <1%")
    incident.add_event("Dev (Alex)", "Added missing index on orders.created_at")
    incident.resolution_time = "2 hours"

    incident.root_cause = (
        "A new reporting query added in v2.3.1 performed a full table scan "
        "on orders.created_at (missing index). Each query held a connection "
        "for 120+ seconds, exhausting the pool of 50 connections."
    )
    incident.resolution = (
        "1) Killed the blocking queries. "
        "2) Increased pool size temporarily. "
        "3) Added index on orders.created_at. "
        "4) Added query timeout of 30s."
    )
    incident.action_items = [
        {"action": "Add migration check to CI/CD pipeline",
         "owner": "Platform Team", "due": "2025-02-01", "priority": "P1"},
        {"action": "Add query timeout (30s) to all DB connections",
         "owner": "Backend Team", "due": "2025-01-25", "priority": "P1"},
        {"action": "Add DB pool saturation alert",
         "owner": "SRE Team", "due": "2025-01-22", "priority": "P2"},
        {"action": "Review all queries in v2.3.1 for missing indexes",
         "owner": "Backend Team", "due": "2025-01-28", "priority": "P2"},
    ]

    for entry in incident.timeline:
        print(f"    [{entry.actor}] {entry.action}")
        if entry.details:
            print(f"      -> {entry.details}")
    print()

    # --- Step 4: Generate postmortem ---
    print("--- Step 4: Blameless Postmortem ---\n")
    postmortem = generate_postmortem(incident)
    # Print first 40 lines
    for line in postmortem.split("\n")[:40]:
        print(f"  {line}")
    print("  ...")
    print(f"\n  (Full postmortem: {len(postmortem.split(chr(10)))} lines)")

    print("\n--- Incident Response Best Practices ---")
    print("1. Classify severity immediately (drives response level)")
    print("2. Follow playbooks - don't improvise under pressure")
    print("3. Communicate status updates at regular intervals")
    print("4. Focus on mitigation first, root cause second")
    print("5. Blameless postmortems: fix systems, not people")
    print("6. Track action items to completion")
    print("7. Practice incident response before you need it")


if __name__ == "__main__":
    main()
