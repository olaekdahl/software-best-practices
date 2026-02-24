"""
Demo 04 - Observability Triage: RED and USE Methods
======================================================
Demonstrates metrics collection and triage using RED/USE frameworks.

Instructor talking points:
- RED: Rate, Errors, Duration (for services)
- USE: Utilization, Saturation, Errors (for resources)
- Golden signals guide troubleshooting order
- Structured dashboards accelerate MTTR
- Alerts on SLIs, not raw metrics

Run: python main.py
"""

from __future__ import annotations

import random
import time
from collections import deque
from dataclasses import dataclass, field
from enum import Enum


# ============================================================================
# Metrics collectors
# ============================================================================

@dataclass
class HistogramBucket:
    le: float  # "less than or equal" boundary
    count: int = 0


class Histogram:
    """Simple histogram for tracking durations."""

    def __init__(self, name: str, buckets: list[float] | None = None):
        self.name = name
        self._values: list[float] = []
        bucket_bounds = buckets or [5, 10, 25, 50, 100, 250, 500, 1000]
        self._buckets = [HistogramBucket(le=b) for b in bucket_bounds]

    def observe(self, value: float) -> None:
        self._values.append(value)
        for bucket in self._buckets:
            if value <= bucket.le:
                bucket.count += 1

    @property
    def count(self) -> int:
        return len(self._values)

    @property
    def p50(self) -> float:
        if not self._values:
            return 0.0
        s = sorted(self._values)
        return s[len(s) // 2]

    @property
    def p95(self) -> float:
        if not self._values:
            return 0.0
        s = sorted(self._values)
        idx = int(len(s) * 0.95)
        return s[min(idx, len(s) - 1)]

    @property
    def p99(self) -> float:
        if not self._values:
            return 0.0
        s = sorted(self._values)
        idx = int(len(s) * 0.99)
        return s[min(idx, len(s) - 1)]


@dataclass
class Counter:
    """Simple counter metric."""
    name: str
    value: int = 0
    labels: dict = field(default_factory=dict)

    def inc(self, amount: int = 1) -> None:
        self.value += amount


@dataclass
class Gauge:
    """Simple gauge metric (can go up or down)."""
    name: str
    value: float = 0.0

    def set(self, val: float) -> None:
        self.value = val

    def inc(self, amount: float = 1.0) -> None:
        self.value += amount

    def dec(self, amount: float = 1.0) -> None:
        self.value -= amount


# ============================================================================
# RED Metrics (Rate, Errors, Duration) - for services
# ============================================================================

class ServiceMetrics:
    """RED metrics for a service endpoint."""

    def __init__(self, service_name: str):
        self.service = service_name
        self.request_count = Counter(f"{service_name}_requests_total")
        self.error_count = Counter(f"{service_name}_errors_total")
        self.duration = Histogram(f"{service_name}_duration_ms")
        self._window: deque[dict] = deque(maxlen=1000)

    def record(self, status: str, duration_ms: float) -> None:
        self.request_count.inc()
        self.duration.observe(duration_ms)
        if status.startswith("5") or status == "error":
            self.error_count.inc()
        self._window.append({
            "time": time.time(),
            "status": status,
            "duration_ms": duration_ms,
        })

    @property
    def error_rate(self) -> float:
        if self.request_count.value == 0:
            return 0.0
        return self.error_count.value / self.request_count.value

    def red_summary(self) -> dict:
        return {
            "service": self.service,
            "rate": self.request_count.value,
            "errors": self.error_count.value,
            "error_rate": f"{self.error_rate:.1%}",
            "duration_p50": f"{self.duration.p50:.1f}ms",
            "duration_p95": f"{self.duration.p95:.1f}ms",
            "duration_p99": f"{self.duration.p99:.1f}ms",
        }


# ============================================================================
# USE Metrics (Utilization, Saturation, Errors) - for resources
# ============================================================================

class ResourceMetrics:
    """USE metrics for a resource (CPU, memory, connections, etc.)."""

    def __init__(self, resource_name: str, capacity: float):
        self.resource = resource_name
        self.capacity = capacity
        self.utilization = Gauge(f"{resource_name}_utilization")
        self.saturation = Gauge(f"{resource_name}_saturation")  # Queue depth
        self.errors = Counter(f"{resource_name}_errors_total")

    def update(self, current_usage: float, queue_depth: int = 0) -> None:
        self.utilization.set(current_usage / self.capacity * 100)
        self.saturation.set(queue_depth)

    def record_error(self) -> None:
        self.errors.inc()

    def use_summary(self) -> dict:
        return {
            "resource": self.resource,
            "utilization": f"{self.utilization.value:.1f}%",
            "saturation": int(self.saturation.value),
            "errors": self.errors.value,
            "status": self._health_status(),
        }

    def _health_status(self) -> str:
        if self.errors.value > 0:
            return "DEGRADED"
        if self.utilization.value > 90:
            return "CRITICAL"
        if self.utilization.value > 75:
            return "WARNING"
        return "HEALTHY"


# ============================================================================
# SLI/SLO tracking
# ============================================================================

@dataclass
class SLO:
    """Service Level Objective."""
    name: str
    target: float   # e.g., 0.999 for 99.9%
    window: str      # e.g., "30d"

    good_events: int = 0
    total_events: int = 0

    def record(self, is_good: bool) -> None:
        self.total_events += 1
        if is_good:
            self.good_events += 1

    @property
    def current_level(self) -> float:
        if self.total_events == 0:
            return 1.0
        return self.good_events / self.total_events

    @property
    def error_budget_remaining(self) -> float:
        """How much error budget is left (0.0 = exhausted, 1.0 = full)."""
        allowed_bad = (1 - self.target) * self.total_events
        actual_bad = self.total_events - self.good_events
        if allowed_bad == 0:
            return 0.0
        return max(0.0, 1.0 - actual_bad / allowed_bad)

    @property
    def is_meeting(self) -> bool:
        return self.current_level >= self.target

    def summary(self) -> dict:
        return {
            "slo": self.name,
            "target": f"{self.target:.1%}",
            "current": f"{self.current_level:.2%}",
            "error_budget": f"{self.error_budget_remaining:.1%}",
            "status": "MEETING" if self.is_meeting else "BREACHING",
        }


# ============================================================================
# Simulated service for generating metrics
# ============================================================================

def simulate_traffic(metrics: ServiceMetrics, slo: SLO, num_requests: int = 200):
    """Simulate mixed traffic patterns."""
    random.seed(42)
    for i in range(num_requests):
        # Normal traffic with occasional issues
        if random.random() < 0.05:
            # 5% server errors
            metrics.record("500", random.uniform(500, 2000))
            slo.record(False)
        elif random.random() < 0.03:
            # 3% slow responses (still successful)
            duration = random.uniform(300, 800)
            metrics.record("200", duration)
            slo.record(duration < 500)  # SLO: <500ms
        else:
            # Normal response
            duration = random.gauss(50, 20)
            duration = max(5, duration)
            metrics.record("200", duration)
            slo.record(True)


# ============================================================================
# Triage dashboard
# ============================================================================

def display_dashboard(
    service_metrics: list[ServiceMetrics],
    resource_metrics: list[ResourceMetrics],
    slos: list[SLO],
):
    """Display a triage dashboard."""
    print("\n" + "=" * 70)
    print("  OBSERVABILITY DASHBOARD")
    print("=" * 70)

    # RED section
    print("\n  --- RED Metrics (Services) ---\n")
    print(f"  {'Service':<20} {'Rate':>6} {'Errors':>7} {'Err%':>6} "
          f"{'p50':>8} {'p95':>8} {'p99':>8}")
    print(f"  {'-' * 20} {'-' * 6} {'-' * 7} {'-' * 6} "
          f"{'-' * 8} {'-' * 8} {'-' * 8}")
    for m in service_metrics:
        s = m.red_summary()
        print(f"  {s['service']:<20} {s['rate']:>6} {s['errors']:>7} "
              f"{s['error_rate']:>6} {s['duration_p50']:>8} "
              f"{s['duration_p95']:>8} {s['duration_p99']:>8}")

    # USE section
    print("\n  --- USE Metrics (Resources) ---\n")
    print(f"  {'Resource':<20} {'Util%':>7} {'Queue':>6} {'Errors':>7} {'Status':>10}")
    print(f"  {'-' * 20} {'-' * 7} {'-' * 6} {'-' * 7} {'-' * 10}")
    for m in resource_metrics:
        s = m.use_summary()
        print(f"  {s['resource']:<20} {s['utilization']:>7} "
              f"{s['saturation']:>6} {s['errors']:>7} {s['status']:>10}")

    # SLO section
    print("\n  --- SLO Status ---\n")
    print(f"  {'SLO':<30} {'Target':>8} {'Current':>8} "
          f"{'Budget':>8} {'Status':>10}")
    print(f"  {'-' * 30} {'-' * 8} {'-' * 8} {'-' * 8} {'-' * 10}")
    for s in slos:
        d = s.summary()
        print(f"  {d['slo']:<30} {d['target']:>8} {d['current']:>8} "
              f"{d['error_budget']:>8} {d['status']:>10}")

    print("\n" + "=" * 70)


# ============================================================================
# Main demo
# ============================================================================

def main():
    print("=== Demo: Observability Triage (RED/USE) ===\n")

    # --- Explain the frameworks ---
    print("--- RED Method (for Services) ---")
    print("  R - Rate:     Requests per second")
    print("  E - Errors:   Failed requests per second")
    print("  D - Duration: Latency distribution (p50, p95, p99)")
    print()
    print("--- USE Method (for Resources) ---")
    print("  U - Utilization: % of capacity in use")
    print("  S - Saturation:  Queue depth / backlog")
    print("  E - Errors:      Resource errors")
    print()

    # --- Create metrics ---
    api_metrics = ServiceMetrics("api-gateway")
    order_metrics = ServiceMetrics("order-service")
    payment_metrics = ServiceMetrics("payment-service")

    # Simulate traffic
    api_slo = SLO("API availability", 0.999, "30d")
    order_slo = SLO("Order latency <500ms", 0.95, "30d")

    simulate_traffic(api_metrics, api_slo, 500)
    simulate_traffic(order_metrics, order_slo, 300)

    # Payment service with higher error rate
    random.seed(99)
    payment_slo = SLO("Payment success rate", 0.999, "30d")
    for _ in range(200):
        if random.random() < 0.12:  # 12% error rate - a problem!
            payment_metrics.record("500", random.uniform(800, 3000))
            payment_slo.record(False)
        else:
            payment_metrics.record("200", random.gauss(100, 30))
            payment_slo.record(True)

    # Resource metrics
    cpu = ResourceMetrics("cpu-pool", capacity=100)
    cpu.update(current_usage=72, queue_depth=0)

    db_conns = ResourceMetrics("db-connections", capacity=100)
    db_conns.update(current_usage=91, queue_depth=15)
    db_conns.record_error()
    db_conns.record_error()

    memory = ResourceMetrics("memory", capacity=16_384)
    memory.update(current_usage=12_500, queue_depth=0)

    # Display dashboard
    display_dashboard(
        [api_metrics, order_metrics, payment_metrics],
        [cpu, db_conns, memory],
        [api_slo, order_slo, payment_slo],
    )

    # --- Triage walkthrough ---
    print("\n--- Triage Walkthrough ---\n")
    print("  1. CHECK SLOs: Payment success rate is BREACHING")
    print("     -> Error budget exhausted, immediate attention needed")
    print()
    print("  2. CHECK RED: Payment service has ~12% error rate")
    print("     -> High p99 latency suggests timeout-related failures")
    print()
    print("  3. CHECK USE: DB connections at 91% utilization")
    print("     -> Saturation (queue=15) indicates connection exhaustion")
    print("     -> 2 connection errors correlate with payment failures")
    print()
    print("  4. HYPOTHESIS: Payment service failing because DB connection")
    print("     pool is saturated, causing timeouts on payment queries")
    print()
    print("  5. ACTION: Increase DB pool size, add connection timeout,")
    print("     investigate slow queries holding connections")


if __name__ == "__main__":
    main()
