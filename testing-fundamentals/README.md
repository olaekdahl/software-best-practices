# Testing Fundamentals

Hands-on demos for core testing concepts. The examples use plain Python and pytest for an easy start.

## What’s inside

- Types of testing: unit, integration, system, acceptance, regression, exploratory
- Test pyramid: many fast unit tests, fewer integration/UI tests
- TDD: write a failing test, then code until it passes
- BDD: Given–When–Then scenarios in business-readable language

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

## Folders

- src/ – small demo code (calculator, fizzbuzz)
- tests/unit/ – fast tests for functions/classes
- tests/integration/ – tests working across modules
- tests/system/ – run a script end-to-end and assert results
- tests/acceptance/ – Given–When–Then scenarios
- tests/regression/ – snapshot tests to catch unintentional changes
- tests/exploratory/ – checklist/notes for exploratory sessions
- tdd/ – red/green/refactor example (fizzbuzz)
- bdd/ – minimal BDD runner for feature files (no external deps)

## Test Pyramid

- Prefer many small, fast unit tests for quick feedback.
- Add a moderate layer of integration tests to cover interactions.
- Keep system/UI tests targeted, they can be slow and brittle.

## TDD quick taste

1) Write a failing test in tdd/test_fizzbuzz.py.
2) Implement the smallest code to pass it in src/fizzbuzz.py.
3) Refactor safely with tests green.

## BDD quick taste

- Define behavior in bdd/features/calculator.feature with Given–When–Then.
- Run bdd/run_bdd.py to execute step definitions in bdd/steps/.
