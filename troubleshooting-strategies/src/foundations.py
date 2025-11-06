from __future__ import annotations

"""Foundations of Troubleshooting Demo

Shows a systematic approach:
1. Reproduce
2. Isolate
3. Identify root cause
4. Fix
5. Verify

Also highlights common pitfalls: confirmation bias, skipping steps, tool overuse.
"""

import time
from dataclasses import dataclass

# Simulated buggy function: occasionally mis-computes due to hidden state mutation.
_state = {"offset": 0}


def buggy_compute(values: list[int]) -> int:
    # Symptom: sometimes result is larger than expected.
    total = 0
    for v in values:
        total += v
    # Hidden fault: offset should be 0 but can leak from previous runs.
    return total + _state["offset"]


def reproduce():
    print("[reproduce] Running scenario to see failure...")
    runs = []
    for i in range(5):
        vals = list(range(10))
        result = buggy_compute(vals)
        runs.append(result)
    print("Results:", runs)
    if len(set(runs)) > 1:
        print("Symptom observed: inconsistent totals")
    else:
        print("Intermittent issue not reproduced yet; try more iterations or different input size")


def isolate():
    print("[isolate] Checking if global state influences outcome...")
    # Experiment: reset state between runs
    isolated_runs = []
    for _ in range(5):
        _state["offset"] = 0  # reset
        vals = list(range(10))
        isolated_runs.append(buggy_compute(vals))
    print("Isolated results (with reset):", isolated_runs)
    print("Observation: now stable -> state leakage suspected")


def identify_root_cause():
    print("[identify] Inspecting code for mutation of _state...")
    # Simulate discovery step
    print("Found: _state['offset'] is never reset after experimental change earlier (root cause: lingering offset)")


def fix():
    print("[fix] Implementing correction: ensure offset reset before computation")
    def fixed_compute(values: list[int]) -> int:
        local_offset = 0  # guarantee clean
        return sum(values) + local_offset
    return fixed_compute


def verify(fixed_fn):
    print("[verify] Re-run tests to confirm stability")
    results = [fixed_fn(list(range(10))) for _ in range(5)]
    print("Post-fix results:", results)
    assert len(set(results)) == 1, "Fix did not stabilize results"
    print("Verification passed: consistent output")


@dataclass
class Pitfall:
    name: str
    description: str


PITFALLS = [
    Pitfall("Confirmation Bias", "Assuming the first hypothesis is correct and ignoring contrary evidence."),
    Pitfall("Skipping Steps", "Jumping to code changes without isolating the problem."),
    Pitfall("Over-Fixating on Tools", "Relying solely on tooling instead of forming/testable hypotheses."),
]


def pitfalls():
    print("[pitfalls] Common pitfalls to avoid:")
    for p in PITFALLS:
        print(f" - {p.name}: {p.description}")


def main():
    reproduce()
    isolate()
    identify_root_cause()
    fixed = fix()
    verify(fixed)
    pitfalls()


if __name__ == "__main__":
    main()
