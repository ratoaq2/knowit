---
paths:
  - "knowit/bugreport.py"
  - "knowit/environment.py"
  - "knowit/pathcheck.py"
  - "scripts/import_report.py"
  - ".github/ISSUE_TEMPLATE/**"
---

# Bug reports: reproduce without the media

- A reporter never sends the media. The report holds the raw backend output. It must be enough to make
  a test fixture.
- Redaction is on by default. A change must not let a title, a file name, or a tag leak into the report.
- A new file name from a real issue goes into `ADVERSARIAL_NAMES` in `knowit/pathcheck.py`.
- The flow and the limits of `--check-name` are in `docs/bug-reports.md`.
