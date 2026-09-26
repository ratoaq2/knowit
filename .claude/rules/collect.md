---
paths:
  - "knowit/collect.py"
  - "scripts/analyze_collect.py"
---

# Collect: a capture must stay readable

- A change to the record layout must increase `COLLECT_VERSION` in `knowit/collect.py`.
- A capture must not hold a title, a file name, or a real path. It uses the redaction of `knowit/bugreport.py`.
- The format, resume, parts, and the analysis are in `docs/collect.md`.
