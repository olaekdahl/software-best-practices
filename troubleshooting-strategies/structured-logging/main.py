"""
Demo 02 - Structured Logging
===============================
Demonstrates structured logging with correlation IDs for traceability.

Instructor talking points:
- Structured logs (JSON) vs unstructured text
- Correlation IDs thread requests across services
- Log levels: DEBUG, INFO, WARNING, ERROR
- Include context: who, what, when, how long
- Sensitive data masking

Run: python main.py
"""

from __future__ import annotations

import json
import logging
import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any


# ============================================================================
# Level 1: Unstructured logging (anti-pattern)
# ============================================================================

def demo_unstructured():
    """Show why unstructured logs are hard to query."""
    print("--- Unstructured Logging (Hard to Parse) ---\n")
    messages = [
        "2025-01-15 10:23:45 INFO User alice logged in",
        "2025-01-15 10:23:45 INFO Processing order 12345",
        "2025-01-15 10:23:46 ERROR Failed to charge card for order 12345",
        "2025-01-15 10:23:46 INFO User bob logged in",
        "2025-01-15 10:23:47 ERROR Connection timeout to payment service",
        "2025-01-15 10:23:47 INFO Retrying payment for order 12345",
    ]
    for msg in messages:
        print(f"  {msg}")
    print()
    print("  Problem: Which error belongs to which request?")
    print("  Problem: Can't filter by user, order, or service.")
    print()


# ============================================================================
# Level 2: Structured JSON logger
# ============================================================================

class StructuredLogger:
    """JSON-based structured logger with context binding."""

    def __init__(self, service: str, default_context: dict | None = None):
        self.service = service
        self._context: dict[str, Any] = default_context or {}
        self._entries: list[dict] = []

    def bind(self, **kwargs: Any) -> StructuredLogger:
        """Create a child logger with additional context."""
        new_context = {**self._context, **kwargs}
        child = StructuredLogger(self.service, new_context)
        child._entries = self._entries  # Share log store
        return child

    def _log(self, level: str, event: str, **kwargs: Any) -> None:
        entry = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "level": level,
            "service": self.service,
            "event": event,
            **self._context,
            **kwargs,
        }
        # Mask sensitive fields
        for key in ("password", "token", "secret", "card_number"):
            if key in entry:
                entry[key] = "***MASKED***"

        self._entries.append(entry)
        formatted = json.dumps(entry, default=str)
        print(f"  {formatted}")

    def info(self, event: str, **kwargs: Any) -> None:
        self._log("INFO", event, **kwargs)

    def warning(self, event: str, **kwargs: Any) -> None:
        self._log("WARNING", event, **kwargs)

    def error(self, event: str, **kwargs: Any) -> None:
        self._log("ERROR", event, **kwargs)

    def debug(self, event: str, **kwargs: Any) -> None:
        self._log("DEBUG", event, **kwargs)

    @contextmanager
    def timed(self, event: str, **kwargs: Any):
        """Context manager to log operation duration."""
        start = time.perf_counter()
        self.info(f"{event}.started", **kwargs)
        try:
            yield
        except Exception as e:
            elapsed = time.perf_counter() - start
            self.error(f"{event}.failed", error=str(e), duration_ms=round(elapsed * 1000))
            raise
        else:
            elapsed = time.perf_counter() - start
            self.info(f"{event}.completed", duration_ms=round(elapsed * 1000), **kwargs)


# ============================================================================
# Level 3: Correlation ID middleware
# ============================================================================

@dataclass
class RequestContext:
    """Carries correlation ID and metadata through a request lifecycle."""
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    user_id: str | None = None
    method: str = ""
    path: str = ""

    def to_dict(self) -> dict:
        return {
            "correlation_id": self.correlation_id,
            "user_id": self.user_id,
            "method": self.method,
            "path": self.path,
        }


class OrderService:
    """Simulated service demonstrating correlated logging."""

    def __init__(self, logger: StructuredLogger):
        self.logger = logger

    def process_order(self, ctx: RequestContext, order_data: dict) -> dict:
        log = self.logger.bind(**ctx.to_dict())

        with log.timed("order.process", order_id=order_data.get("id")):
            # Step 1: Validate
            log.info("order.validate", items=len(order_data.get("items", [])))
            time.sleep(0.01)

            # Step 2: Check inventory
            log.info("inventory.check", sku_count=len(order_data.get("items", [])))
            time.sleep(0.02)

            # Step 3: Charge payment
            log.info("payment.charge",
                     amount=order_data.get("total"),
                     card_number="4111-1111-1111-1111")  # Will be masked
            time.sleep(0.01)

            # Step 4: Create shipment
            log.info("shipment.create", address=order_data.get("address", "N/A"))

            return {"status": "confirmed", "order_id": order_data["id"]}


# ============================================================================
# Level 4: Log analysis
# ============================================================================

def analyze_logs(entries: list[dict]) -> None:
    """Show how structured logs enable analysis."""
    print("\n--- Log Analysis ---\n")

    # Count by level
    levels = {}
    for e in entries:
        level = e.get("level", "UNKNOWN")
        levels[level] = levels.get(level, 0) + 1
    print(f"  Events by level: {levels}")

    # Find slow operations
    slow_ops = [
        e for e in entries
        if e.get("duration_ms", 0) > 20
    ]
    if slow_ops:
        print(f"  Slow operations (>20ms): {len(slow_ops)}")
        for op in slow_ops:
            print(f"    - {op['event']}: {op.get('duration_ms')}ms "
                  f"[{op.get('correlation_id', 'N/A')}]")

    # Group by correlation ID
    by_corr = {}
    for e in entries:
        cid = e.get("correlation_id", "N/A")
        by_corr.setdefault(cid, []).append(e)
    print(f"  Distinct requests: {len(by_corr)}")

    # Check for masked fields
    masked = [
        e for e in entries
        if any(v == "***MASKED***" for v in e.values())
    ]
    print(f"  Entries with masked sensitive data: {len(masked)}")


# ============================================================================
# Main demo
# ============================================================================

def main():
    print("=== Demo: Structured Logging ===\n")

    # Level 1: Show the problem
    demo_unstructured()

    # Level 2: Structured logging
    print("--- Structured Logging (Machine-Parseable) ---\n")
    logger = StructuredLogger("order-service")

    # Level 3: With correlation IDs
    print("--- Request 1: Successful Order ---\n")
    ctx1 = RequestContext(user_id="alice", method="POST", path="/orders")
    svc = OrderService(logger)
    result = svc.process_order(ctx1, {
        "id": "ORD-001",
        "items": ["SKU-A", "SKU-B"],
        "total": 99.99,
        "address": "123 Main St",
    })

    print(f"\n  Result: {result}\n")

    print("--- Request 2: Another User ---\n")
    ctx2 = RequestContext(user_id="bob", method="POST", path="/orders")
    result2 = svc.process_order(ctx2, {
        "id": "ORD-002",
        "items": ["SKU-C"],
        "total": 49.99,
        "address": "456 Oak Ave",
    })

    # Level 4: Analysis
    analyze_logs(logger._entries)

    print("\n--- Structured Logging Best Practices ---")
    print("1. Use JSON format for machine parsing")
    print("2. Include correlation_id in every log entry")
    print("3. Bind context once, use throughout request")
    print("4. Mask sensitive data (passwords, tokens, PII)")
    print("5. Log durations for performance tracking")
    print("6. Use consistent event naming (service.action.status)")


if __name__ == "__main__":
    main()
