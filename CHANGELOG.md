# Changelog

## 0.1.5 — 2026-11-07

`TimetableEntry.label` is persisted (campus-model#5): the `storage: False`
metadata is dropped, so each entry stores its group's label at creation and
historical allocations stay self-describing after `LessonGroup` rows are
reused across timetable versions by campus.api (label-anchored reuse,
campus#1080 — the #592 stable lessongroup identity ruling). The
`LessonGroup` and module-allocation docstrings now state the identity rule:
`id` is the stable cross-version identity, `timetable_id` tracks the
timetable the group *currently* belongs to and is updated in place on
reuse. No storage migration: collections are schemaless and `from_storage`
falls back to the field default, so legacy records deserialize with label
None. No interface change (patch).

## 0.1.4 — 2026-11-05

New model: `HostedApp` (campus-classroom#81) — a single-file HTML app published to Campus app hosting. Slug is the stable hosting/reference address (immutable, unique); bytes are content-addressed under `content_hash` (opaque sha256 key, serve-time integrity check); `name` is display-only; `status` hooks approval gating. Served by the new `campus.api.hostedapps` resource and the SDK's `client.api.hostedapps` client.

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
