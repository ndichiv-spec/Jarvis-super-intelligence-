from dataclasses import dataclass
from typing import Protocol

from jarvis_core.domain.shared.events import DomainEvent
from jarvis_core.domain.shared.models import AggregateRoot
from jarvis_core.domain.shared.value_objects import Version


@dataclass(frozen=True, slots=True)
class Compatibility:
    minimum_core_version: Version


@dataclass(frozen=True, slots=True)
class Extension:
    name: str


@dataclass(frozen=True, slots=True)
class Manifest:
    name: str
    permissions: tuple[str, ...]


@dataclass(slots=True)
class Plugin(AggregateRoot):
    manifest: Manifest
    version: Version
    compatibility: Compatibility
    extensions: tuple[Extension, ...]


class PluginRepository(Protocol):
    def save(self, plugin: Plugin) -> None: ...


class PluginPermissionPort(Protocol):
    def validate(self, permissions: tuple[str, ...]) -> bool: ...


@dataclass(frozen=True, slots=True)
class PluginInstalled(DomainEvent):
    plugin_name: str
