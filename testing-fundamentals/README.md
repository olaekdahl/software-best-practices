# Testing Fundamentals

Hands-on demos for core testing concepts. The examples use plain Python and pytest for an easy start.

## What’s inside

- Types of testing: unit, integration, system, acceptance, regression, exploratory
- Test pyramid: many fast unit tests, fewer integration/UI tests
- TDD: write a failing test, then code until it passes
- BDD: Given-When-Then scenarios in business-readable language

## Setup

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install pytest
```

## Run tests

```bash
# From repo root
pytest testing-fundamentals -q
```

### Use and interpret the tests/ results

- Structure:
	- `tests/unit/` — tiny, fast checks for individual functions/classes. Failures here usually point to a single function’s behavior or edge case.
	- `tests/integration/` — exercises multiple modules together. Failures often indicate wiring/contract mismatches between components.
	- `tests/system/` — runs a script end-to-end and inspects outputs. Great for “does the whole flow still work?”
	- `tests/acceptance/` — Given‑When‑Then business scenarios. Read them like a story to see expected user‑visible outcomes.
	- `tests/regression/` — catch unintended changes (e.g., snapshot/file outputs). Update snapshots only when the change is intended.
	- `tests/exploratory/` — non‑automated notes/checklists to guide manual exploration; not executed by pytest.

- Running subsets:
	- Only unit tests: `pytest testing-fundamentals/tests/unit -q`
	- Filter by keyword: `pytest testing-fundamentals/tests -k "acceptance and total" -q`
	- Single file / single test: `pytest testing-fundamentals/tests/acceptance/test_acceptance_shopper_total.py::test_shopper_total_acceptance -q`
	- More verbosity for names and assertions: `pytest -v`

- Reading pytest output:
	- PASSED — the assertion met expectations.
	- FAILED — look at the traceback and the assertion diff. The last lines show expected vs actual (e.g., `assert 64.92 == 64.88`).
	- SKIPPED/XFAILED — test skipped or known to fail (documented with markers). These do not break the run by default.
	- Exit code `0` means success; non‑zero (e.g., `1`) means there were failures or errors. In a TDD “red” step, a non‑zero code is expected until you implement the fix.

- Interpreting acceptance tests (example):
	- See `tests/acceptance/test_acceptance_shopper_total.py`. The test is written as a scenario with comments `Given/When/Then` and computes a shopper’s total with tax.
	- If it fails, check the rounding and arithmetic in the underlying functions (`src/calculator.py`) used via `add/multiply`.
	- Acceptance tests express outcomes in user language; if they fail, think “what would a user see wrong?” and trace down to the lower‑level unit/integration tests.

- Useful options:
	- Stop on first failure: `-x` or `--maxfail=1`
	- Show print/logs: `-s`
	- Seed/flaky help: `pytest-rerunfailures` or `pytest-randomly` (optional; not required here)
	- Coverage (optional if `coverage` or `pytest-cov` installed): `pytest --cov=testing-fundamentals/src --cov-report=term-missing`

## Folders

- src/ - small demo code (calculator, fizzbuzz)
- tests/unit/ - fast tests for functions/classes
- tests/integration/ - tests working across modules
- tests/system/ - run a script end-to-end and assert results
- tests/acceptance/ - Given-When-Then scenarios
- tests/regression/ - snapshot tests to catch unintentional changes
- tests/exploratory/ - checklist/notes for exploratory sessions
- tdd/ - red/green/refactor example (fizzbuzz)
- bdd/ - minimal BDD runner for feature files (no external deps)

## Test Pyramid

- Prefer many small, fast unit tests for quick feedback.
- Add a moderate layer of integration tests to cover interactions.
- Keep system/UI tests targeted, they can be slow and brittle.

## TDD quick taste

1) Write a failing test in tdd/test_fizzbuzz.py.
2) Implement the smallest code to pass it in src/fizzbuzz.py.
3) Refactor safely with tests green.

## BDD quick taste

- Define behavior in bdd/features/calculator.feature with Given-When-Then.
- Run bdd/run_bdd.py to execute step definitions in bdd/steps/.
