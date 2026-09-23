---
paths:
  - "knowit/api.py"
  - "knowit/__init__.py"
---

# Public API: keep it stable

Other applications (Bazarr, Medusa, subliminal) call knowit as a library. The public names are `know()`,
`dependencies()`, `initialize()`, and `KnowitException`. Do not remove or rename them, and do not change
their signatures, without a major version. The contract is in "Public API" in `docs/architecture.md`.
