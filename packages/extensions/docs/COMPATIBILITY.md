# Compatibility Model

## Overview

The compatibility engine validates that an extension can run on the current platform version and that its capabilities are compatible with consumers. Three types of compatibility are checked:

1. **Platform compatibility** — extension's platform version bounds vs. current platform version
2. **Version compatibility** — whether a version satisfies a semver constraint
3. **Capability contract compatibility** — whether a provided capability meets consumer expectations

## Compatibility Levels

| Level | Description |
|-------|-------------|
| `COMPATIBLE` | Fully compatible |
| `INCOMPATIBLE` | Cannot be used (breaks the `is_compatible` flag) |
| `DEPRECATED` | Compatible but deprecated (e.g., pinned dependencies) |
| `REQUIRES_UPDATE` | Compatible only after an update |

## CompatibilityReport

```python
@dataclass(frozen=True, slots=True)
class CompatibilityReport:
    level: CompatibilityLevel              # Overall level (lowest across all issues)
    issues: tuple[CompatibilityIssue, ...] = ()
    is_compatible: bool = True             # False if any issue is INCOMPATIBLE
```

```python
@dataclass(frozen=True, slots=True)
class CompatibilityIssue:
    code: str                              # Machine-readable error code
    message: str                           # Human-readable description
    severity: CompatibilityLevel           # Issue severity
```

## Platform Compatibility

Checked via `InMemoryCompatibilityEngine.check_extension_compatibility(manifest, platform_version)`:

```
platform_version < manifest.min_platform_version → INCOMPATIBLE (code: PLATFORM_VERSION_LOW)
platform_version > manifest.max_platform_version → INCOMPATIBLE (code: PLATFORM_VERSION_HIGH)
```

## Version Constraint Compatibility

Checked via `InMemoryCompatibilityEngine.check_version_compatibility(version, constraint)`.

Supported constraint operators:

| Operator | Example | Behavior |
|----------|---------|----------|
| `>=` | `>=1.0.0` | Version must be >= the given version (same major, else check major/ minor/patch) |
| `^` | `^1.0.0` | Compatible with same major, >= minor/patch (semver caret) |
| `~` | `~1.2.0` | Same major & minor, patch >= given (semver tilde) |
| `==` | `==1.0.0` | Exact match |
| `>` | `>1.0.0` | Strictly greater |
| `<` | `<2.0.0` | Strictly less |
| `<=` | `<=1.5.0` | Less than or equal |
| *(none)* | `1.0.0` | Exact match (same as `==`) |

## Capability Contract Compatibility

Checked via `InMemoryCompatibilityEngine.check_contract_compatibility(provided, expected)`:

```
type mismatch        → INCOMPATIBLE
identifier mismatch  → INCOMPATIBLE
version too low      → REQUIRES_UPDATE
otherwise            → COMPATIBLE
```

## Manifest Validator Platform Checks

The `InMemoryManifestValidator.validate_platform_compatibility()` performs equivalent platform version checks plus additional warnings:

- **PINNED_DEPENDENCY** — `DEPRECATED` severity when any dependency uses `==` constraint (pinned versions may cause issues).

## Edge Cases

- If `max_platform_version` is `None`, no upper bound is enforced.
- Platform compatibility is checked at install time by the kernel; extensions with incompatible platform requirements proceed to INSTALLED state but flagged with the report.
