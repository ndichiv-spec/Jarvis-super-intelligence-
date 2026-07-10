from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

from jarvis_tools.models import ToolDefinition, ToolMetadata, ToolStatus


@dataclass(slots=True)
class InMemoryToolRegistry:
    _tools: dict[str, ToolMetadata] = field(default_factory=dict)

    def register(self, definition: ToolDefinition) -> ToolMetadata:
        now = datetime.now(UTC)
        meta = ToolMetadata(
            identifier=definition.identifier,
            definition=definition,
            registered_at=now,
            updated_at=now,
        )
        self._tools[definition.identifier] = meta
        return meta

    def update(self, metadata: ToolMetadata) -> None:
        if metadata.identifier not in self._tools:
            msg = f"Tool not registered: {metadata.identifier}"
            raise KeyError(msg)
        now = datetime.now(UTC)
        updated = ToolMetadata(
            identifier=metadata.identifier,
            definition=metadata.definition,
            registered_at=self._tools[metadata.identifier].registered_at,
            updated_at=now,
        )
        self._tools[metadata.identifier] = updated

    def get(self, identifier: str) -> ToolMetadata | None:
        return self._tools.get(identifier)

    def list(self) -> tuple[ToolMetadata, ...]:
        return tuple(self._tools.values())

    def list_by_status(self, status: ToolStatus) -> tuple[ToolMetadata, ...]:
        return tuple(m for m in self._tools.values() if m.definition.status == status)

    def deregister(self, identifier: str) -> None:
        self._tools.pop(identifier, None)
