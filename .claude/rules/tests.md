---
paths:
  - "tests/**"
---

# Tests

- Bug fix: commit a failing test that shows the bug first, then the fix. See `docs/workflow.md`.
- Run with quiet flags: `uv run pytest -q --tb=short tests`.
- No media files in the repo. A fixture is the raw backend output in `tests/data/<provider>/`, next to the
  expected result. See `docs/testing.md`.
- Rule and property cases go in the `tests/test_*.yml` files, not in new test functions.
- A regression test for a user report comes from `scripts/import_report.py`. See `docs/bug-reports.md`.
