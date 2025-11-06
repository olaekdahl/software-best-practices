from __future__ import annotations

"""Logs & Stack Traces Demo

- Configure logging with levels and timestamps
- Generate an exception and show how to read the stack from bottom to top
- Demonstrate capturing a traceback to enrich logs
"""

import logging
import traceback


def configure_logging(level: int = logging.INFO) -> None:
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def deep_call_chain(n: int) -> int:
    if n <= 0:
        return 1
    return 1 + deeper(n - 1)


def deeper(n: int) -> int:
    if n == 3:
        raise ValueError("Boom at depth=3 (simulated root cause)")
    return deep_call_chain(n)


def run_scenario():
    log = logging.getLogger("demo.logs")
    log.info("Starting scenario")
    try:
        deep_call_chain(5)
    except Exception:
        tb = traceback.format_exc()
        log.error("Caught exception. Key steps to interpret stack:")
        log.error("1) Look at the last lines for the originating error (root cause).")
        log.error("2) Walk upward to see how calls propagated.")
        log.error("3) Map frames to source files/lines and inspect variables.")
        log.error("\nStack trace:\n%s", tb)


if __name__ == "__main__":
    configure_logging()
    run_scenario()
