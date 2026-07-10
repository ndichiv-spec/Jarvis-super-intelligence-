from __future__ import annotations

from jarvis_extensions.models import (
    CapabilityDefinition,
    CompatibilityIssue,
    CompatibilityLevel,
    CompatibilityReport,
    ExtensionManifest,
    VersionInfo,
)


class InMemoryCompatibilityEngine:
    def check_extension_compatibility(
        self,
        manifest: ExtensionManifest,
        platform_version: VersionInfo,
    ) -> CompatibilityReport:
        issues: list[CompatibilityIssue] = []
        if platform_version < manifest.min_platform_version:
            issues.append(
                CompatibilityIssue(
                    code="PLATFORM_VERSION_LOW",
                    message=(
                        f"Platform {platform_version} below minimum {manifest.min_platform_version}"
                    ),
                    severity=CompatibilityLevel.INCOMPATIBLE,
                ),
            )
        if manifest.max_platform_version is not None:
            if platform_version > manifest.max_platform_version:
                issues.append(
                    CompatibilityIssue(
                        code="PLATFORM_VERSION_HIGH",
                        message=(
                            f"Platform {platform_version} above maximum "
                            f"{manifest.max_platform_version}"
                        ),
                        severity=CompatibilityLevel.INCOMPATIBLE,
                    ),
                )
        level = CompatibilityLevel.COMPATIBLE
        for issue in issues:
            if issue.severity == CompatibilityLevel.INCOMPATIBLE:
                level = CompatibilityLevel.INCOMPATIBLE
        is_ok = level != CompatibilityLevel.INCOMPATIBLE
        return CompatibilityReport(
            level=level,
            issues=tuple(issues),
            is_compatible=is_ok,
        )

    def check_version_compatibility(
        self,
        version: VersionInfo,
        constraint: str,
    ) -> CompatibilityLevel:
        if version.satisfies(constraint):
            return CompatibilityLevel.COMPATIBLE
        return CompatibilityLevel.INCOMPATIBLE

    def check_contract_compatibility(
        self,
        provided: CapabilityDefinition,
        expected: CapabilityDefinition,
    ) -> CompatibilityLevel:
        if provided.capability_type != expected.capability_type:
            return CompatibilityLevel.INCOMPATIBLE
        if provided.identifier != expected.identifier:
            return CompatibilityLevel.INCOMPATIBLE
        if not provided.version.satisfies(f">={expected.version.major}.0.0"):
            return CompatibilityLevel.REQUIRES_UPDATE
        return CompatibilityLevel.COMPATIBLE
