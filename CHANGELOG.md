# Changelog

## 0.1.0 — 2026-10-28

Initial release: `campus.model` carved verbatim from the campus
monorepo (#970 phase 3, dist 2 of 5). PEP 420 namespace portion;
stdlib + campus-common only; flask-free even at call time.

Interface locked from day one: closed-world `__all__` tests plus a
checked-in manifest (`tests/interface_manifest.json`) — an interface
change is a deliberate commit with a CHANGELOG entry and the version
bump the diff dictates.
