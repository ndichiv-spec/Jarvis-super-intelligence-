from __future__ import annotations

from dataclasses import dataclass, field

from jarvis_api.gateway.errors import GatewayException
from jarvis_api.gateway.types import ProtocolName, SubsystemName


@dataclass(frozen=True, slots=True)
class RouteDefinition:
    identifier: str
    subsystem: SubsystemName
    path_prefix: str
    supported_protocols: tuple[ProtocolName, ...] = field(default_factory=tuple)
    workspace_visibility: tuple[str, ...] = field(default_factory=lambda: ("public",))
    authorization_requirements: tuple[str, ...] = field(default_factory=tuple)
    capabilities: tuple[str, ...] = field(default_factory=tuple)
    documentation_references: tuple[str, ...] = field(default_factory=tuple)


class RoutingEngine:
    def __init__(self) -> None:
        self._routes: dict[str, RouteDefinition] = {}

    def register_route(self, route: RouteDefinition) -> None:
        if route.identifier in self._routes:
            raise GatewayException.validation(
                f"Route '{route.identifier}' is already registered",
                details={"route": route.identifier},
            )
        self._routes[route.identifier] = route

    def resolve(self, path: str, *, protocol: ProtocolName | None = None) -> RouteDefinition:
        if not path.startswith("/"):
            path = f"/{path}"

        candidates = [
            route
            for route in self._routes.values()
            if path.startswith(route.path_prefix)
            and (
                protocol is None
                or not route.supported_protocols
                or protocol in route.supported_protocols
            )
        ]
        if not candidates:
            raise GatewayException.validation(
                f"No route registered for path '{path}'",
                details={"path": path, "protocol": protocol},
            )
        return max(candidates, key=lambda route: len(route.path_prefix))

    def list_routes(self) -> tuple[RouteDefinition, ...]:
        return tuple(sorted(self._routes.values(), key=lambda route: route.identifier))
