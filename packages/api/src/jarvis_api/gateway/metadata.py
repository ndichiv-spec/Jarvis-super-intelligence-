from __future__ import annotations

from dataclasses import dataclass, field

from jarvis_api.gateway.errors import GatewayException
from jarvis_api.gateway.types import ProtocolName, SubsystemName


@dataclass(frozen=True, slots=True)
class ApiMetadata:
    identifier: str
    version: str
    protocol: ProtocolName
    subsystem: SubsystemName
    capabilities: tuple[str, ...] = field(default_factory=tuple)
    workspace_visibility: tuple[str, ...] = field(default_factory=lambda: ("public",))
    authorization_requirements: tuple[str, ...] = field(default_factory=tuple)
    documentation_references: tuple[str, ...] = field(default_factory=tuple)


class ApiMetadataRegistry:
    def __init__(self) -> None:
        self._metadata: dict[str, ApiMetadata] = {}

    def register(self, metadata: ApiMetadata) -> None:
        if metadata.identifier in self._metadata:
            raise GatewayException.validation(
                f"API metadata '{metadata.identifier}' is already registered",
                details={"identifier": metadata.identifier},
            )
        self._metadata[metadata.identifier] = metadata

    def resolve(self, identifier: str) -> ApiMetadata | None:
        return self._metadata.get(identifier)

    def list_all(self) -> tuple[ApiMetadata, ...]:
        return tuple(sorted(self._metadata.values(), key=lambda entry: entry.identifier))
