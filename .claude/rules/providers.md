---
paths:
  - "knowit/core.py"
  - "knowit/provider.py"
  - "knowit/providers/**"
  - "knowit/properties/**"
  - "knowit/rules/**"
---

# Providers, properties, and rules: bad input is normal

- The raw track data from each backend has no type. A value can be missing, empty, or of an unexpected
  type (issue #219: a `dict` where a string was expected). Handle it, log it, and continue.
- Do not let an error escape from a property or a rule. A provider raises only `ProviderError` or its
  subclasses.
- The data flow and the base classes are in `docs/architecture.md`. The typing rules for raw data are in
  `docs/typing.md`. Read them before you change a signature.
