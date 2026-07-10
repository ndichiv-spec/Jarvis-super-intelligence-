# Versioning Strategy

## Overview

The Knowledge Platform uses a monotonically increasing version number for knowledge documents. Each update creates a new version in the history.

## Version Model

```python
@dataclass(frozen=True, slots=True)
class KnowledgeVersion:
    version_id: str          # Unique identifier
    document_id: str         # Parent document
    number: int              # Monotonically increasing
    changed_by: str          # User/agent identifier
    change_summary: str      # Human-readable description
    changed_at: datetime     # Timestamp
    compatible_with: tuple[int, ...]  # Compatible version numbers
    deprecated: bool         # Deprecation flag
    supersedes_version: int | None  # Previous version number
```

## Version Rules

1. **Initial version**: Starts at 1 (set in `KnowledgeMetadata.version`)
2. **Increment**: Each call to `record_version()` increments `number` by 1
3. **History**: All versions are preserved in an ordered sequence
4. **Compatibility**: Tracked via `compatible_with` tuple of version numbers
5. **Deprecation**: Versions can be marked as deprecated without removal
6. **Supersession**: Links to the version being replaced

## Document Updates

When `document.with_update()` is called:

1. A new `KnowledgeMetadata` is created with `version + 1`
2. `updated_at` is set to the current timestamp
3. The `KnowledgeVersionManager.record_version()` creates the version record
4. The document is validated before the update is persisted

## Compatibility Checking

```python
def is_compatible(document_id: str, required_version: int) -> bool:
    current = self.current_version(document_id)
    if current is None:
        return False
    return required_version in current.compatible_with
```

## History Retrieval

```python
def history(document_id: str) -> tuple[KnowledgeVersion, ...]:
    # Returns all versions in chronological order
    return self._history.get(document_id, ())
```
