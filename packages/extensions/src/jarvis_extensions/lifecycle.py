from __future__ import annotations

from datetime import UTC, datetime

from jarvis_extensions.models import ExtensionMetadata, ExtensionStatus

_D = ExtensionStatus.DISCOVERED
_I = ExtensionStatus.INSTALLED
_V = ExtensionStatus.VERIFIED
_A = ExtensionStatus.ACTIVATED
_P = ExtensionStatus.PAUSED
_Dis = ExtensionStatus.DISABLED
_U = ExtensionStatus.UPDATING
_F = ExtensionStatus.FAILED
_R = ExtensionStatus.REMOVED

_TRANSITIONS: dict[ExtensionStatus, set[ExtensionStatus]] = {
    _D: {_I, _R},
    _I: {_V, _A, _Dis, _U, _R},
    _V: {_A, _Dis, _R},
    _A: {_P, _Dis, _U, _R},
    _P: {_A, _Dis, _R},
    _Dis: {_A, _U, _R},
    _U: {_V, _F, _Dis},
    _F: {_Dis, _R},
    _R: set(),
}


class InMemoryLifecycleManager:
    def transition(
        self,
        metadata: ExtensionMetadata,
        target: ExtensionStatus,
    ) -> ExtensionMetadata:
        if not self.can_transition(metadata.status, target):
            msg = (
                f"Cannot transition from {metadata.status} to {target} "
                f"for extension {metadata.extension_id}"
            )
            raise ValueError(msg)
        return ExtensionMetadata(
            extension_id=metadata.extension_id,
            manifest=metadata.manifest,
            status=target,
            installed_version=metadata.installed_version,
            available_update=metadata.available_update,
            dependencies_resolved=metadata.dependencies_resolved,
            compatibility=metadata.compatibility,
            isolation_policy=metadata.isolation_policy,
            created_at=metadata.created_at,
            updated_at=datetime.now(UTC),
            metadata=metadata.metadata,
        )

    def can_transition(self, current: ExtensionStatus, target: ExtensionStatus) -> bool:
        allowed = _TRANSITIONS.get(current)
        if allowed is None:
            return False
        return target in allowed

    def valid_transitions(self, current: ExtensionStatus) -> tuple[ExtensionStatus, ...]:
        allowed = _TRANSITIONS.get(current)
        if allowed is None:
            return ()
        return tuple(sorted(allowed, key=lambda s: s.name))
