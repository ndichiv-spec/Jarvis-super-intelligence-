from __future__ import annotations

from jarvis_extensions.models import VersionInfo


class InMemoryVersionManager:
    def compare(self, a: VersionInfo, b: VersionInfo) -> int:
        if a.major != b.major:
            return -1 if a.major < b.major else 1
        if a.minor != b.minor:
            return -1 if a.minor < b.minor else 1
        if a.patch != b.patch:
            return -1 if a.patch < b.patch else 1
        return 0

    def is_compatible(self, version: VersionInfo, constraint: str) -> bool:
        return version.satisfies(constraint)

    def suggest_upgrade(
        self,
        current: VersionInfo,
        available: tuple[VersionInfo, ...],
    ) -> VersionInfo | None:
        viable = [v for v in available if v > current]
        if not viable:
            return None
        return max(viable)

    def is_deprecated(
        self,
        version: VersionInfo,
        deprecation_map: dict[int, VersionInfo],
    ) -> bool:
        min_version = deprecation_map.get(version.major)
        if min_version is not None:
            return version < min_version
        return False
