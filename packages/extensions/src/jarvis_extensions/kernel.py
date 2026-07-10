from __future__ import annotations

from dataclasses import dataclass, field

from jarvis_extensions.capabilities import InMemoryCapabilityRegistry
from jarvis_extensions.compatibility import InMemoryCompatibilityEngine
from jarvis_extensions.dependency import InMemoryDependencyManager
from jarvis_extensions.events import InMemoryEventIntegration
from jarvis_extensions.health import InMemoryHealthMonitor
from jarvis_extensions.isolation import InMemoryIsolationManager
from jarvis_extensions.lifecycle import InMemoryLifecycleManager
from jarvis_extensions.manifest import InMemoryManifestValidator
from jarvis_extensions.models import (
    CompatibilityLevel,
    ExtensionHealth,
    ExtensionManifest,
    ExtensionMetadata,
    ExtensionStatus,
    VersionInfo,
)
from jarvis_extensions.permissions import InMemoryPermissionManager
from jarvis_extensions.registry import InMemoryExtensionRegistry
from jarvis_extensions.version import InMemoryVersionManager


@dataclass(slots=True)
class ExtensionKernel:
    registry: InMemoryExtensionRegistry = field(default_factory=InMemoryExtensionRegistry)
    manifest_validator: InMemoryManifestValidator = field(default_factory=InMemoryManifestValidator)
    dependency_manager: InMemoryDependencyManager = field(default_factory=InMemoryDependencyManager)
    compatibility_engine: InMemoryCompatibilityEngine = field(
        default_factory=InMemoryCompatibilityEngine,
    )
    capability_registry: InMemoryCapabilityRegistry = field(
        default_factory=InMemoryCapabilityRegistry,
    )
    lifecycle: InMemoryLifecycleManager = field(default_factory=InMemoryLifecycleManager)
    permissions: InMemoryPermissionManager = field(default_factory=InMemoryPermissionManager)
    isolation: InMemoryIsolationManager = field(default_factory=InMemoryIsolationManager)
    version_manager: InMemoryVersionManager = field(default_factory=InMemoryVersionManager)
    health_monitor: InMemoryHealthMonitor = field(default_factory=InMemoryHealthMonitor)
    event_integration: InMemoryEventIntegration = field(default_factory=InMemoryEventIntegration)

    _platform_version: VersionInfo = field(default_factory=lambda: VersionInfo(11, 0, 0))

    def discover(self, manifest: ExtensionManifest) -> ExtensionMetadata:
        issues = self.manifest_validator.validate(manifest)
        for issue in issues:
            if issue.severity == CompatibilityLevel.INCOMPATIBLE:
                meta = self.registry.register(manifest)
                self.registry.update(meta.with_status(ExtensionStatus.FAILED))
                self.health_monitor.record_failure(
                    manifest.extension_id,
                    issue.message,
                )
                failed = self.registry.get(manifest.extension_id)
                return failed if failed is not None else meta
        meta = self.registry.register(manifest)
        self.health_monitor.record_activation(manifest.extension_id)
        return meta

    def install(self, extension_id: str) -> ExtensionMetadata:
        meta = self.registry.get(extension_id)
        if meta is None:
            msg = f"Extension not found: {extension_id}"
            raise ValueError(msg)
        if not self.lifecycle.can_transition(meta.status, ExtensionStatus.INSTALLED):
            msg = f"Cannot install extension in state {meta.status}"
            raise ValueError(msg)

        dep_issues = self.dependency_manager.resolve(
            extension_id,
            meta.manifest.dependencies,
            self.registry,
        )
        circular = self.dependency_manager.validate_circular(
            extension_id,
            meta.manifest.dependencies,
            self.registry,
        )
        all_issues = list(dep_issues) + list(circular)
        incompatible = any(i.severity == CompatibilityLevel.INCOMPATIBLE for i in all_issues)

        comp_report = self.compatibility_engine.check_extension_compatibility(
            meta.manifest,
            self._platform_version,
        )

        meta = self.lifecycle.transition(meta, ExtensionStatus.INSTALLED)
        meta = ExtensionMetadata(
            extension_id=meta.extension_id,
            manifest=meta.manifest,
            status=meta.status,
            installed_version=meta.manifest.version,
            dependencies_resolved=not incompatible,
            compatibility=comp_report,
            isolation_policy=meta.isolation_policy,
            created_at=meta.created_at,
            updated_at=meta.updated_at,
            metadata=meta.metadata,
        )
        self.registry.update(meta)
        if incompatible:
            self.health_monitor.record_failure(
                extension_id,
                "Dependency resolution failed",
            )
        return meta

    def activate(self, extension_id: str) -> ExtensionMetadata:
        meta = self.registry.get(extension_id)
        if meta is None:
            msg = f"Extension not found: {extension_id}"
            raise ValueError(msg)
        meta = self.lifecycle.transition(meta, ExtensionStatus.ACTIVATED)
        self.registry.update(meta)
        for cap in meta.manifest.capabilities:
            self.capability_registry.register_capability(extension_id, cap)
        for perm in meta.manifest.permissions:
            self.permissions.grant(extension_id, perm)
        self.health_monitor.record_activation(extension_id)
        return meta

    def deactivate(self, extension_id: str) -> ExtensionMetadata:
        meta = self.registry.get(extension_id)
        if meta is None:
            msg = f"Extension not found: {extension_id}"
            raise ValueError(msg)
        meta = self.lifecycle.transition(meta, ExtensionStatus.PAUSED)
        self.registry.update(meta)
        self.capability_registry.clear_extension(extension_id)
        return meta

    def disable(self, extension_id: str) -> ExtensionMetadata:
        meta = self.registry.get(extension_id)
        if meta is None:
            msg = f"Extension not found: {extension_id}"
            raise ValueError(msg)
        meta = self.lifecycle.transition(meta, ExtensionStatus.DISABLED)
        self.registry.update(meta)
        self.capability_registry.clear_extension(extension_id)
        self.permissions.revoke_all(extension_id)
        self.event_integration.unsubscribe_all(extension_id)
        return meta

    def enable(self, extension_id: str) -> ExtensionMetadata:
        meta = self.registry.get(extension_id)
        if meta is None:
            msg = f"Extension not found: {extension_id}"
            raise ValueError(msg)
        meta = self.lifecycle.transition(meta, ExtensionStatus.ACTIVATED)
        self.registry.update(meta)
        for cap in meta.manifest.capabilities:
            self.capability_registry.register_capability(extension_id, cap)
        return meta

    def remove(self, extension_id: str) -> ExtensionMetadata | None:
        meta = self.registry.get(extension_id)
        if meta is None:
            return None
        removed = self.lifecycle.transition(meta, ExtensionStatus.REMOVED)
        self.capability_registry.clear_extension(extension_id)
        self.permissions.revoke_all(extension_id)
        self.event_integration.unsubscribe_all(extension_id)
        self.isolation.remove_policy(extension_id)
        self.health_monitor.reset_health(extension_id)
        self.registry.remove(extension_id)
        return removed

    def update(
        self,
        extension_id: str,
        new_manifest: ExtensionManifest,
    ) -> ExtensionMetadata:
        meta = self.registry.get(extension_id)
        if meta is None:
            msg = f"Extension not found: {extension_id}"
            raise ValueError(msg)
        meta = self.lifecycle.transition(meta, ExtensionStatus.UPDATING)
        self.registry.update(meta)
        comp_report = self.compatibility_engine.check_extension_compatibility(
            new_manifest,
            self._platform_version,
        )
        updated = ExtensionMetadata(
            extension_id=extension_id,
            manifest=new_manifest,
            status=ExtensionStatus.VERIFIED,
            installed_version=new_manifest.version,
            compatibility=comp_report,
            isolation_policy=meta.isolation_policy,
            created_at=meta.created_at,
            updated_at=meta.updated_at,
            metadata=meta.metadata,
        )
        self.registry.update(updated)
        return updated

    def get_metadata(self, extension_id: str) -> ExtensionMetadata | None:
        return self.registry.get(extension_id)

    def list_extensions(
        self,
        status: ExtensionStatus | None = None,
    ) -> tuple[ExtensionMetadata, ...]:
        if status is not None:
            return self.registry.list_by_status(status)
        return self.registry.list()

    def get_health(self, extension_id: str) -> ExtensionHealth | None:
        return self.health_monitor.get_health(extension_id)
