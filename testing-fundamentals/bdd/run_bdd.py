from __future__ import annotations

"""Tiny BDD runner (no external dependencies).

Parses a simple .feature file with Given/When/Then lines and dispatches to
step functions defined in bdd/steps/*.py.

Usage:
  python3 testing-fundamentals/bdd/run_bdd.py
"""

from pathlib import Path
import importlib.util
import re

ROOT = Path(__file__).resolve().parents[1]
FEATURE = ROOT / "bdd" / "features" / "calculator.feature"
STEPS = ROOT / "bdd" / "steps" / "calculator_steps.py"

# Load step module
spec = importlib.util.spec_from_file_location("steps", STEPS)
assert spec and spec.loader
steps = importlib.util.module_from_spec(spec)
spec.loader.exec_module(steps)  # type: ignore[attr-defined]

# Map patterns to functions
patterns = [
    (re.compile(r"^Given numbers (\S+) and (\S+)$"), steps.given_numbers),
    (re.compile(r"^When I add them$"), steps.when_add),
    (re.compile(r"^When I divide them$"), steps.when_divide),
    (re.compile(r"^Then the result is (\S+)$"), steps.then_result_is),
    (re.compile(r"^Then an error is raised$"), steps.then_error_is_raised),
]


def run_feature(feature_path: Path) -> None:
    lines = feature_path.read_text(encoding="utf-8").splitlines()
    for raw in lines:
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if any(line.startswith(prefix) for prefix in ("Feature:", "As ", "I want", "So that", "Scenario:")):
            print(line)
            continue
        matched = False
        for pat, func in patterns:
            m = pat.match(line)
            if m:
                print(" →", line)
                func(*m.groups())
                matched = True
                break
        if not matched:
            print("(skipped)", line)


if __name__ == "__main__":
    run_feature(FEATURE)
