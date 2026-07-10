from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

from jarvis_extensions.models import (
    CompatibilityLevel,
    CompatibilityReport,
    ExtensionManifest,
    ExtensionMetadata,
    ExtensionStatus,
    ExtensionType,
    IsolationPolicy,
)


@dataclass(slots=True)
class InMemoryExtensionRegistry:
    _extensions: dict[str, ExtensionMetadata] = field(default_factory=dict)

    def register(self, manifest: ExtensionManifest) -> ExtensionMetadata:
        existing = self._extensions.get(manifest.extension_id)
        if existing is not None:
            return existing
        now = datetime.now(UTC)
        meta = ExtensionMetadata(
            extension_id=manifest.extension_id,
            manifest=manifest,
            status=ExtensionStatus.DISCOVERED,
            installed_version=manifest.version,
            dependencies_resolved=False,
            compatibility=CompatibilityReport(
                level=CompatibilityLevel.COMPATIBLE,
                is_compatible=True,
            ),
            isolation_policy=IsolationPolicy(),
            created_at=now,
            updated_at=now,
        )
        self._extensions[manifest.extension_id] = meta
        return meta

    def get(self, extension_id: str) -> ExtensionMetadata | None:
        return self._extensions.get(extension_id)

    def list(self) -> tuple[ExtensionMetadata, ...]:
        return tuple(self._extensions.values())

    def list_by_status(self, status: ExtensionStatus) -> tuple[ExtensionMetadata, ...]:
        return tuple(m for m in self._extensions.values() if m.status == status)

    def list_by_type(self, ext_type: ExtensionType) -> tuple[ExtensionMetadata, ...]:
        return tuple(m for m in self._extensions.values() if m.manifest.extension_type == ext_type)

    def update(self, metadata: ExtensionMetadata) -> None:
        now = datetime.now(UTC)
        updated = ExtensionMetadata(
            extension_id=metadata.extension_id,
            manifest=metadata.manifest,
            status=metadata.status,
            installed_version=metadata.installed_version,
            available_update=metadata.available_update,
            dependencies_resolved=metadata.dependencies_resolved,
            compatibility=metadata.compatibility,
            isolation_policy=metadata.isolation_policy,
            created_at=self._extensions[metadata.extension_id].created_at
            if metadata.extension_id in self._extensions
            else now,
            updated_at=now,
            metadata=metadata.metadata,
        )
        self._extensions[metadata.extension_id] = updated

    def remove(self, extension_id: str) -> None:
        self._extensions.pop(extension_id, None)

    def contains(self, extension_id: str) -> bool:
        return extension_id in self._extensions
