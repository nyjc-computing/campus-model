# Changelog

## 0.1.0 — 2026-10-28

Initial release: `campus.model` carved verbatim from the campus
monorepo (#970 phase 3, dist 2 of 5). PEP 420 namespace portion;
stdlib + campus-common only; flask-free even at call time.

Interface locked from day one: closed-world `__all__` tests plus a
checked-in manifest (`tests/interface_manifest.json`) — an interface
change is a deliberate commit with a CHANGELOG entry and the version
bump the diff dictates.

## 0.1.3 — 2026-11-04

- Dependency rebuild only: campus-common pin moved to the v0.3.1 release wheel
  (which adds `campus.common.protocol`, campus#1041). Poetry direct-URL deps
  bake the exact source URL into wheel metadata, so a campus-common bump
  requires a campus-model rebuild to stay co-installable with consumers that
  pin campus-common 0.3.1 directly. No interface or behavior change (patch).
