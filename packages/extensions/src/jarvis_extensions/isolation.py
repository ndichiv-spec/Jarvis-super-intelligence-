from __future__ import annotations

from dataclasses import dataclass, field

from jarvis_extensions.models import CapabilityType, IsolationPolicy


@dataclass(slots=True)
class InMemoryIsolationManager:
    _policies: dict[str, IsolationPolicy] = field(default_factory=dict)

    def set_policy(self, extension_id: str, policy: IsolationPolicy) -> None:
        self._policies[extension_id] = policy

    def get_policy(self, extension_id: str) -> IsolationPolicy | None:
        return self._policies.get(extension_id)

    def check_capability_allowed(
        self,
        extension_id: str,
        capability_type: CapabilityType,
    ) -> bool:
        policy = self._policies.get(extension_id)
        if policy is None:
            return True
        if capability_type in policy.denied_capabilities:
            return False
        if policy.allowed_capabilities and capability_type not in policy.allowed_capabilities:
            return False
        return True

    def remove_policy(self, extension_id: str) -> None:
        self._policies.pop(extension_id, None)
