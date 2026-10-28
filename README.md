# campus-model

[![CI](https://github.com/nyjc-computing/campus-model/actions/workflows/ci.yml/badge.svg)](https://github.com/nyjc-computing/campus-model/actions/workflows/ci.yml)

`campus.model` — the domain vocabulary of the Campus platform: dataclass
entities (User, Client, Question, Timetable, OAuthToken, ...) with no
business logic. Every service and downstream app speaks in these types.

It ships as a **PEP 420 namespace portion**: the wheel contains
`campus/model/…` with no `campus/__init__.py`, so it merges seamlessly
with the rest of the `campus` namespace installed alongside it. Runtime
dependencies: **the Python standard library + campus-common only** —
pure dataclasses, flask-free even at call time (OTP email rendering
lives in campus-suite's `campus.api.emailotp_templates`). The one
third-party module a plain `import campus.model` loads is bcrypt, via
`credentials`' use of `campus.common.utils.secret`.

Requires Python 3.11–3.13 (3.14 tested, unofficial).

## Installation

Consumed as a version-pinned release wheel (GitHub release asset):

```toml
[tool.poetry.dependencies]
campus-model = {url = "https://github.com/nyjc-computing/campus-model/releases/download/v0.1.0/campus_model-0.1.0-py3-none-any.whl"}
```

or directly with pip:

```bash
pip install https://github.com/nyjc-computing/campus-model/releases/download/v0.1.0/campus_model-0.1.0-py3-none-any.whl
```

PyPI publishing is planned; until then, releases live on GitHub and
consumers pin them by URL. Declare `campus-model` directly only if you
import `campus.model` yourself — campus-suite already depends on it
transitively.

## Usage

Import through the shared `campus` namespace as usual — this
distribution provides the `campus.model` portion:

```python
import campus.model
from campus.model import User, Client
from campus.model.base import Model
from campus.model.constraints import UNIQUE
```

| Area | Provides |
|---|---|
| flat `campus.model` | all entity classes re-exported (38 symbols, `__all__`-declared) |
| `base` | `Model` / `InternalModel` dataclass bases |
| `constraints` | storage constraint constants (`unique`, ...) |
| `http` | `HttpHeader` value classes (stdlib-only; restored from campus.webauth in #982) |
| `audit` | `TraceSpan`, `APIKey`, rate-limit buckets |
| `classroom` | `Question`, `Assignment`, `Submission`, `ClassroomLink`, ... |
| `credentials` / `grant` / `device_code` / `session` / `login` | auth vocabulary: `OAuthToken`, `UserCredentials`, `AppCredentials`, `AccessGrant`, `AuthSession`, ... |
| `user` / `circle` / `booking` / `timetable` / `integration` / `vault` / `emailotp` | domain entities |

## Public interface

The interface is two-tier and CI-enforced:

- **Module tree** — importing submodules
  (`from campus.model.base import Model`) is supported; storage
  backends and downstream apps rely on it.
- **Symbols** — public if and only if listed in the containing
  package's `__all__` (closed-world tested). Anything
  underscore-prefixed is private.

The full declared surface is snapshotted in
[`tests/interface_manifest.json`](tests/interface_manifest.json). Any
interface change is a deliberate commit: regenerate the manifest
(`python scripts/generate_interface_manifest.py`), add a CHANGELOG
entry, and bump the version per the rules below.

## Versioning

Strict 0.x, same policy as campus-common:

- `0.1.x`-style patches: fixes + purely additive interface growth.
- `0.2.0`-style minors: **breaking changes allowed** (until 1.0).
  Breaking changes surface at consumers' next upgrade; deprecations
  carry a `DeprecationWarning` for one minor cycle.
- `1.0.0` = interface-stability promise; standard SemVer thereafter.

campus.model is the *churny* layer of the namespace — entity shapes
evolve with product needs — so consumers relock deliberately on
release wheels rather than floating on a branch. Release history:
[CHANGELOG.md](CHANGELOG.md).

## Rules (CI-enforced)

- Runtime dependencies: stdlib + campus-common only; no third-party
  import anywhere, even lazily (`tests/unit/test_boundaries.py`).
- No imports of sibling `campus.*` packages other than campus.common —
  campus-core (storage/webauth/services) and the service layers depend
  on model, never the reverse.
- `import campus.model` stays flask-free at runtime
  (`tests/unit/model/test_import_weight.py`).
- Wheels stay init-less: `poetry build` +
  `python scripts/audit_wheel_namespace.py`.

## Development

```bash
poetry install
poetry run python -m unittest discover -s tests -t .
poetry run ruff check .
poetry build && poetry run python scripts/audit_wheel_namespace.py
poetry run python scripts/generate_interface_manifest.py --check
```
