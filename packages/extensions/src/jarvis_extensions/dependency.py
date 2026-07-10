from __future__ import annotations

from jarvis_extensions.models import (
    CompatibilityIssue,
    CompatibilityLevel,
    DependencyDefinition,
    DependencyType,
)
from jarvis_extensions.protocols import ExtensionRegistry


class InMemoryDependencyManager:
    def resolve(
        self,
        extension_id: str,
        dependencies: tuple[DependencyDefinition, ...],
        registry: ExtensionRegistry,
    ) -> tuple[CompatibilityIssue, ...]:
        issues: list[CompatibilityIssue] = []
        for dep in dependencies:
            dep_ext = registry.get(dep.extension_id)
            if dep_ext is None:
                if dep.dependency_type == DependencyType.REQUIRED:
                    issues.append(
                        CompatibilityIssue(
                            code="MISSING_DEPENDENCY",
                            message=f"Required dependency not found: {dep.extension_id}",
                            severity=CompatibilityLevel.INCOMPATIBLE,
                        ),
                    )
                continue
            if not dep_ext.manifest.version.satisfies(dep.version_constraint):
                issues.append(
                    CompatibilityIssue(
                        code="VERSION_MISMATCH",
                        message=(
                            f"Dependency {dep.extension_id} version "
                            f"{dep_ext.manifest.version} does not satisfy "
                            f"constraint {dep.version_constraint}"
                        ),
                        severity=CompatibilityLevel.INCOMPATIBLE
                        if dep.dependency_type == DependencyType.REQUIRED
                        else CompatibilityLevel.DEPRECATED,
                    ),
                )
        return tuple(issues)

    def validate_circular(
        self,
        extension_id: str,
        dependencies: tuple[DependencyDefinition, ...],
        registry: ExtensionRegistry,
    ) -> tuple[CompatibilityIssue, ...]:
        issues: list[CompatibilityIssue] = []

        def _check_chain(current_id: str, visited: set[str]) -> None:
            if current_id in visited:
                issues.append(
                    CompatibilityIssue(
                        code="CIRCULAR_DEPENDENCY",
                        message=f"Circular dependency detected involving: {current_id}",
                        severity=CompatibilityLevel.INCOMPATIBLE,
                    ),
                )
                return
            visited.add(current_id)
            ext = registry.get(current_id)
            if ext is not None:
                for dep in ext.manifest.dependencies:
                    _check_chain(dep.extension_id, visited.copy())

        _check_chain(extension_id, set())
        return tuple(issues)
