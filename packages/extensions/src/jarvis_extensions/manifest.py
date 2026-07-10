from __future__ import annotations

from jarvis_extensions.models import (
    CompatibilityIssue,
    CompatibilityLevel,
    CompatibilityReport,
    ExtensionManifest,
    VersionInfo,
)


class InMemoryManifestValidator:
    def validate(self, manifest: ExtensionManifest) -> tuple[CompatibilityIssue, ...]:
        issues: list[CompatibilityIssue] = []
        if not manifest.extension_id.strip():
            issues.append(
                CompatibilityIssue(
                    code="EMPTY_ID",
                    message="Extension ID must not be empty",
                    severity=CompatibilityLevel.INCOMPATIBLE,
                ),
            )
        if not manifest.name.strip():
            issues.append(
                CompatibilityIssue(
                    code="EMPTY_NAME",
                    message="Extension name must not be empty",
                    severity=CompatibilityLevel.INCOMPATIBLE,
                ),
            )
        if (
            manifest.version.major == 0
            and manifest.version.minor == 0
            and manifest.version.patch == 0
        ):
            issues.append(
                CompatibilityIssue(
                    code="INVALID_VERSION",
                    message="Extension version must be specified",
                    severity=CompatibilityLevel.INCOMPATIBLE,
                ),
            )
        seen_ids: set[str] = set()
        for cap in manifest.capabilities:
            if cap.identifier in seen_ids:
                issues.append(
                    CompatibilityIssue(
                        code="DUPLICATE_CAPABILITY",
                        message=f"Duplicate capability: {cap.identifier}",
                        severity=CompatibilityLevel.INCOMPATIBLE,
                    ),
                )
            seen_ids.add(cap.identifier)
        return tuple(issues)

    def validate_platform_compatibility(
        self,
        manifest: ExtensionManifest,
        platform_version: VersionInfo,
    ) -> CompatibilityReport:
        issues: list[CompatibilityIssue] = []
        if platform_version < manifest.min_platform_version:
            issues.append(
                CompatibilityIssue(
                    code="PLATFORM_TOO_OLD",
                    message=(
                        f"Platform version {platform_version} is older than "
                        f"required minimum {manifest.min_platform_version}"
                    ),
                    severity=CompatibilityLevel.INCOMPATIBLE,
                ),
            )
        if manifest.max_platform_version is not None:
            if platform_version > manifest.max_platform_version:
                issues.append(
                    CompatibilityIssue(
                        code="PLATFORM_TOO_NEW",
                        message=(
                            f"Platform version {platform_version} is newer than "
                            f"maximum supported {manifest.max_platform_version}"
                        ),
                        severity=CompatibilityLevel.INCOMPATIBLE,
                    ),
                )
        if any(dep.version_constraint.startswith("==") for dep in manifest.dependencies):
            issues.append(
                CompatibilityIssue(
                    code="PINNED_DEPENDENCY",
                    message="Pinned dependency versions may cause compatibility issues",
                    severity=CompatibilityLevel.DEPRECATED,
                ),
            )
        level = CompatibilityLevel.COMPATIBLE
        for issue in issues:
            if issue.severity == CompatibilityLevel.INCOMPATIBLE:
                level = CompatibilityLevel.INCOMPATIBLE
                break
            if (
                issue.severity == CompatibilityLevel.REQUIRES_UPDATE
                and level != CompatibilityLevel.INCOMPATIBLE
            ):
                level = CompatibilityLevel.REQUIRES_UPDATE
            if issue.severity == CompatibilityLevel.DEPRECATED and level not in (
                CompatibilityLevel.INCOMPATIBLE,
                CompatibilityLevel.REQUIRES_UPDATE,
            ):
                level = CompatibilityLevel.DEPRECATED
        return CompatibilityReport(
            level=level,
            issues=tuple(issues),
            is_compatible=level != CompatibilityLevel.INCOMPATIBLE,
        )
