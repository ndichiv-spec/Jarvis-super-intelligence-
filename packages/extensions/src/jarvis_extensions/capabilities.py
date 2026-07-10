from __future__ import annotations

from dataclasses import dataclass, field

from jarvis_extensions.models import CapabilityDefinition, CapabilityType


@dataclass(slots=True)
class InMemoryCapabilityRegistry:
    _capabilities: dict[str, tuple[str, CapabilityDefinition]] = field(default_factory=dict)

    def register_capability(
        self,
        extension_id: str,
        capability: CapabilityDefinition,
    ) -> None:
        self._capabilities[capability.identifier] = (extension_id, capability)

    def unregister_capability(self, extension_id: str, identifier: str) -> None:
        entry = self._capabilities.get(identifier)
        if entry is not None and entry[0] == extension_id:
            del self._capabilities[identifier]

    def get_capability(self, identifier: str) -> CapabilityDefinition | None:
        entry = self._capabilities.get(identifier)
        return entry[1] if entry is not None else None

    def list_capabilities(
        self,
        capability_type: CapabilityType | None = None,
    ) -> tuple[tuple[str, CapabilityDefinition], ...]:
        if capability_type is None:
            return tuple(self._capabilities.values())
        return tuple(
            v for v in self._capabilities.values() if v[1].capability_type == capability_type
        )

    def list_extension_capabilities(
        self,
        extension_id: str,
    ) -> tuple[CapabilityDefinition, ...]:
        return tuple(v[1] for v in self._capabilities.values() if v[0] == extension_id)

    def clear_extension(self, extension_id: str) -> None:
        to_remove = [k for k, v in self._capabilities.items() if v[0] == extension_id]
        for k in to_remove:
            del self._capabilities[k]
