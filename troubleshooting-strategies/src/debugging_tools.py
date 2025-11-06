from __future__ import annotations

"""Debugging Tools Demo

Shows:
- Logging levels
- Assertions
- Optional breakpoint hook (set DEMO_DEBUG=1)
- Guidance for VS Code debugger
"""

import logging
import os
import sys


def configure_logging():
    logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")


def compute(x: int) -> int:
    logging.debug("compute() entered with x=%s", x)
    assert x >= 0, "x must be non-negative"  # assertion usage
    return x * x


def maybe_breakpoint():
    if os.environ.get("DEMO_DEBUG") == "1":
        # Avoid pdb.set_trace() if running non-interactively; simulate pause.
        print("[debug] Breakpoint hook triggered (set real breakpoint in VS Code here)")


def main():
    configure_logging()
    maybe_breakpoint()  # Set a VS Code breakpoint on this line for demo
    for i in range(3):
        val = compute(i)
        logging.info("result=%s", val)
    try:
        compute(-1)
    except AssertionError as e:
        logging.error("Assertion triggered: %s", e)
        logging.info("Use debugger to inspect call stack and local variables.")


if __name__ == "__main__":
    main()
