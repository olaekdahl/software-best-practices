# Exploratory Testing Notes

Goal: uncover issues that scripted tests may miss.

- Charter: Explore ingestion edge cases (missing fields, extra columns, non-UTF8).
- Start points:
  - Modify data files under data-engineering-and-ml-pipelines/ingestion-and-transformation/data/
  - Try empty CSV rows, negative amounts, huge numbers.
- Heuristics:
  - CRUD, boundaries, interrupts (Ctrl+C during streaming), logs.
- Risks:
  - Silent data loss, incorrect rounding, timezone shifts.
- Exit:
  - 30–45 minutes or 3 significant findings.
