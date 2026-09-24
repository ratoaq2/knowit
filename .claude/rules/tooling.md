---
paths:
  - "pyproject.toml"
  - ".python-version"
  - ".pre-commit-config.yaml"
  - ".github/workflows/**"
  - "scripts/**"
---

# Tooling

These files define the commands and checks. When you change one, make sure that the commands in
`CLAUDE.md` and the setup in `CONTRIBUTING.md` are still correct, and that `scripts/test.sh` still runs the
same checks as CI. `.python-version` is the newest version of the CI matrix. `docs/typing.md` explains the mypy settings in `pyproject.toml`.
