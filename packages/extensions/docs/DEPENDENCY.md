# Dependency Model

## Overview

Extensions may declare dependencies on other extensions. The `InMemoryDependencyManager` resolves these dependencies and detects circular dependency chains.

## DependencyDefinition

```python
@dataclass(frozen=True, slots=True)
class DependencyDefinition:
    extension_id: str                       # ID of the required extension
    version_constraint: str = ">=0.0.0"    # Semver constraint
    dependency_type: DependencyType = DependencyType.REQUIRED
```

### Dependency Types

| Type | Behavior |
|------|----------|
| `REQUIRED` | Missing dependency → `INCOMPATIBLE` issue; unresolved dependencies → install continues with `dependencies_resolved=False` |
| `OPTIONAL` | Missing dependency is silently ignored; version mismatch produces `DEPRECATED` warning |

## Resolution Process

`InMemoryDependencyManager.resolve()` performs two checks per dependency:

1. **Existence**: Is the dependency extension registered in the registry?
2. **Version**: Does the dependency's version satisfy the declared version constraint?

Issue codes:
- `MISSING_DEPENDENCY` — Required dependency not found → `INCOMPATIBLE`
- `VERSION_MISMATCH` — Version constraint not satisfied → `INCOMPATIBLE` for REQUIRED, `DEPRECATED` for OPTIONAL

## Circular Dependency Detection

`InMemoryDependencyManager.validate_circular()` performs a DFS traversal starting from the given extension, following its dependency chain transitively. If the traversal encounters an already-visited extension ID, a `CIRCULAR_DEPENDENCY` issue (`INCOMPATIBLE`) is produced.

### Example

```
A depends on B
B depends on A
validate_circular("A") → CIRCULAR_DEPENDENCY involving: A
```

## Kernel Integration

During `ExtensionKernel.install()`, both `resolve()` and `validate_circular()` are called. If any `INCOMPATIBLE` issue is found, `dependencies_resolved` is set to `False` but installation proceeds — the extension is still installed, allowing the user to resolve dependencies later.

## Edge Cases

- Circular dependency detection copies the `visited` set at each recursion level to produce accurate per-chain results.
- If multiple circular dependencies exist, each is reported as a separate issue.
- Self-referential dependencies (A depends on A) are caught as circular.
