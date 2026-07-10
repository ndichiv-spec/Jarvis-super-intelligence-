# Phase 14 API Versioning Guide

## Semantic Version Policy

- Gateway versions follow `MAJOR.MINOR.PATCH`.
- `ApiVersionManager` validates format and resolves compatibility.
- Major version mismatch is rejected.

## Deprecation

- Versions can be flagged as deprecated.
- Deprecation notice and migration guidance are propagated in response metadata.
- Replacement version can be attached to deprecated records.

## Compatibility Resolution

1. Exact match is preferred.
2. If absent, the highest compatible same-major version is selected.
3. Unsupported majors are rejected as policy violations.
