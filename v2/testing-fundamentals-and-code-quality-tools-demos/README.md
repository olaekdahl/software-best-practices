# Testing Fundamentals and Code Quality Tools - Demos

Progressive demos from basic pytest to a full quality pipeline.

| Demo | Topic | Complexity |
|------|-------|-----------|
| demo01_basic_testing | Simple pytest assertions | Naive |
| demo02_tdd_workflow | TDD red-green-refactor cycle | Intermediate |
| demo03_fixtures_parametrize | Fixtures, parametrize, markers | Intermediate |
| demo04_property_based | Hypothesis property-based testing | Advanced |
| demo05_quality_pipeline | Ruff, mypy, coverage, pre-commit | Real-world |

## Setup

```bash
pip install pytest pytest-cov hypothesis ruff mypy
```

## Running

```bash
cd demo01_basic_testing
pytest -v
```
