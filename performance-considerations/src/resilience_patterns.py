"""
Demo 05 - Resilience Patterns: Retry, Circuit Breaker, Timeout, Bulkhead
===========================================================================
Production-grade resilience patterns for protecting services.

Instructor talking points:
- Timeouts: never wait forever
- Retries: exponential backoff + jitter for idempotent ops
- Circuit Breaker: stop calling failing services
- Bulkhead: isolate failures to prevent cascade
- Combine patterns for layered resilience

Run: python main.py
"""

from __future__ import annotations

import random
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable


# ============================================================================
# Pattern 1: Retry with Exponential Backoff and Jitter
# ============================================================================

class RetryExhausted(Exception):
    """All retry attempts failed."""
    pass


@dataclass
class RetryConfig:
    max_attempts: int = 3
    base_delay: float = 0.1    # seconds
    max_delay: float = 2.0
    jitter: bool = True
    retryable_exceptions: tuple = (Exception,)


def retry_with_backoff(
    func: Callable,
    config: RetryConfig = RetryConfig(),
    *args: Any,
    **kwargs: Any,
) -> Any:
    """Execute function with exponential backoff retry."""
    last_exception = None

    for attempt in range(1, config.max_attempts + 1):
        try:
            result = func(*args, **kwargs)
            if attempt > 1:
                print(f"    Succeeded on attempt {attempt}")
            return result
        except config.retryable_exceptions as e:
            last_exception = e
            if attempt == config.max_attempts:
                break

            # Exponential backoff
            delay = min(config.base_delay * (2 ** (attempt - 1)), config.max_delay)
            if config.jitter:
                delay = delay * (0.5 + random.random())

            print(f"    Attempt {attempt} failed: {e}. "
                  f"Retrying in {delay:.3f}s...")
            time.sleep(delay)

    raise RetryExhausted(
        f"All {config.max_attempts} attempts failed. "
        f"Last error: {last_exception}"
    )


# ============================================================================
# Pattern 2: Circuit Breaker
# ============================================================================

class CircuitState(Enum):
    CLOSED = "CLOSED"        # Normal operation
    OPEN = "OPEN"            # Failing, reject requests
    HALF_OPEN = "HALF_OPEN"  # Testing recovery


class CircuitOpenError(Exception):
    """Circuit breaker is open, rejecting request."""
    pass


@dataclass
class CircuitBreaker:
    """Circuit breaker to protect against cascading failures.

    States:
    - CLOSED: Normal. Track failures. Open if threshold exceeded.
    - OPEN: Reject all requests. After timeout, move to HALF_OPEN.
    - HALF_OPEN: Allow one test request. Success -> CLOSED, Failure -> OPEN.
    """
    failure_threshold: int = 5
    recovery_timeout: float = 10.0  # seconds
    _state: CircuitState = field(default=CircuitState.CLOSED, init=False)
    _failure_count: int = field(default=0, init=False)
    _last_failure_time: float = field(default=0.0, init=False)
    _success_count: int = field(default=0, init=False)

    @property
    def state(self) -> CircuitState:
        if self._state == CircuitState.OPEN:
            if time.time() - self._last_failure_time > self.recovery_timeout:
                self._state = CircuitState.HALF_OPEN
        return self._state

    def call(self, func: Callable, *args: Any, **kwargs: Any) -> Any:
        """Execute function through circuit breaker."""
        current_state = self.state

        if current_state == CircuitState.OPEN:
            raise CircuitOpenError(
                f"Circuit is OPEN. Retry after "
                f"{self.recovery_timeout - (time.time() - self._last_failure_time):.1f}s"
            )

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise

    def _on_success(self) -> None:
        self._failure_count = 0
        self._success_count += 1
        if self._state == CircuitState.HALF_OPEN:
            self._state = CircuitState.CLOSED
            print(f"    [CB] Circuit CLOSED (recovered)")

    def _on_failure(self) -> None:
        self._failure_count += 1
        self._last_failure_time = time.time()
        if self._failure_count >= self.failure_threshold:
            self._state = CircuitState.OPEN
            print(f"    [CB] Circuit OPENED after {self._failure_count} failures")

    @property
    def stats(self) -> dict:
        return {
            "state": self.state.value,
            "failures": self._failure_count,
            "successes": self._success_count,
        }


# ============================================================================
# Pattern 3: Timeout
# ============================================================================

class TimeoutError(Exception):
    pass


def with_timeout(func: Callable, timeout: float, *args: Any, **kwargs: Any) -> Any:
    """Execute function with a timeout (simplified - uses thread for demo)."""
    import threading

    result = [None]
    exception = [None]

    def target():
        try:
            result[0] = func(*args, **kwargs)
        except Exception as e:
            exception[0] = e

    thread = threading.Thread(target=target)
    thread.start()
    thread.join(timeout=timeout)

    if thread.is_alive():
        raise TimeoutError(f"Operation timed out after {timeout}s")
    if exception[0]:
        raise exception[0]
    return result[0]


# ============================================================================
# Pattern 4: Bulkhead (isolate failure domains)
# ============================================================================

class BulkheadFull(Exception):
    pass


class Bulkhead:
    """Limits concurrent access to a resource to contain failures."""

    def __init__(self, name: str, max_concurrent: int = 10):
        self.name = name
        self.max_concurrent = max_concurrent
        self._active = 0
        self._rejected = 0

    def acquire(self) -> bool:
        if self._active >= self.max_concurrent:
            self._rejected += 1
            raise BulkheadFull(
                f"Bulkhead '{self.name}' full: {self._active}/{self.max_concurrent}"
            )
        self._active += 1
        return True

    def release(self) -> None:
        self._active = max(0, self._active - 1)

    def call(self, func: Callable, *args: Any, **kwargs: Any) -> Any:
        self.acquire()
        try:
            return func(*args, **kwargs)
        finally:
            self.release()

    @property
    def stats(self) -> dict:
        return {
            "name": self.name,
            "active": self._active,
            "max": self.max_concurrent,
            "rejected": self._rejected,
        }


# ============================================================================
# Simulated external service
# ============================================================================

class ExternalService:
    """Simulated flaky external service for testing patterns."""

    def __init__(self, failure_rate: float = 0.0, latency: float = 0.05):
        self.failure_rate = failure_rate
        self.latency = latency
        self.call_count = 0

    def call(self, request: str) -> str:
        self.call_count += 1
        time.sleep(self.latency)
        if random.random() < self.failure_rate:
            raise ConnectionError(f"Service unavailable (call #{self.call_count})")
        return f"ok:{request}"


# ============================================================================
# Main demo
# ============================================================================

def main():
    print("=== Demo: Resilience Patterns ===\n")
    random.seed(42)

    # --- Pattern 1: Retry ---
    print("--- Pattern 1: Retry with Backoff ---")
    flaky = ExternalService(failure_rate=0.6, latency=0.01)
    config = RetryConfig(max_attempts=5, base_delay=0.05, max_delay=0.5)

    for i in range(3):
        try:
            result = retry_with_backoff(flaky.call, config, f"request-{i}")
            print(f"  Request {i}: {result}")
        except RetryExhausted as e:
            print(f"  Request {i}: FAILED - {e}")
    print()

    # --- Pattern 2: Circuit Breaker ---
    print("--- Pattern 2: Circuit Breaker ---")
    failing_service = ExternalService(failure_rate=0.9, latency=0.01)
    cb = CircuitBreaker(failure_threshold=3, recovery_timeout=1.0)

    for i in range(8):
        try:
            result = cb.call(failing_service.call, f"req-{i}")
            print(f"  Call {i}: {result}")
        except CircuitOpenError as e:
            print(f"  Call {i}: REJECTED (circuit open)")
        except ConnectionError as e:
            print(f"  Call {i}: FAILED - {e}")

    print(f"  Circuit state: {cb.stats}")
    print()

    # Wait for recovery
    print("  Waiting for recovery timeout...")
    time.sleep(1.1)
    good_service = ExternalService(failure_rate=0.0, latency=0.01)
    try:
        result = cb.call(good_service.call, "recovery-test")
        print(f"  Recovery test: {result}")
        print(f"  Circuit state: {cb.stats}")
    except Exception as e:
        print(f"  Recovery failed: {e}")
    print()

    # --- Pattern 3: Timeout ---
    print("--- Pattern 3: Timeout ---")
    slow_service = ExternalService(failure_rate=0.0, latency=0.5)

    try:
        result = with_timeout(slow_service.call, 0.2, "fast-timeout")
        print(f"  Result: {result}")
    except TimeoutError as e:
        print(f"  Timed out: {e}")

    fast_service = ExternalService(failure_rate=0.0, latency=0.05)
    try:
        result = with_timeout(fast_service.call, 0.2, "ok-timeout")
        print(f"  Result: {result}")
    except TimeoutError as e:
        print(f"  Timed out: {e}")
    print()

    # --- Pattern 4: Bulkhead ---
    print("--- Pattern 4: Bulkhead ---")
    db_bulkhead = Bulkhead("database", max_concurrent=3)
    service = ExternalService(failure_rate=0.0, latency=0.01)

    # Fill the bulkhead
    for i in range(3):
        db_bulkhead.acquire()
    print(f"  Bulkhead stats: {db_bulkhead.stats}")

    # Next request should be rejected
    try:
        db_bulkhead.call(service.call, "overflow")
    except BulkheadFull as e:
        print(f"  Rejected: {e}")

    # Release and retry
    db_bulkhead.release()
    result = db_bulkhead.call(service.call, "after-release")
    print(f"  After release: {result}")
    print(f"  Final stats: {db_bulkhead.stats}")

    print("\n--- Resilience Pattern Summary ---")
    print("1. Retry: Backoff + jitter for transient failures (idempotent ops only)")
    print("2. Circuit Breaker: Stop calling failing services (prevent cascade)")
    print("3. Timeout: Never wait forever (bound worst-case latency)")
    print("4. Bulkhead: Isolate resources (contain blast radius)")
    print("5. Combine: Timeout -> Retry -> Circuit Breaker for layered protection")


if __name__ == "__main__":
    main()
