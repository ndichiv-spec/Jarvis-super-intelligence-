from __future__ import annotations

from dataclasses import dataclass, field
from uuid import uuid4

from jarvis_agents.models import AgentMetadata, AgentStatus
from jarvis_agents.registry import InMemoryAgentRegistry


@dataclass(frozen=True, slots=True)
class RoutingRule:
    rule_id: str
    name: str
    source_pattern: str
    target_role: str
    priority: int = 0


@dataclass(slots=True)
class MessageRouter:
    _registry: InMemoryAgentRegistry
    _rules: list[RoutingRule] = field(default_factory=list)
    _routing_table: dict[str, str] = field(default_factory=dict)

    def add_rule(self, name: str, source_pattern: str, target_role: str, priority: int = 0) -> RoutingRule:
        rule = RoutingRule(
            rule_id=f"rule-{uuid4().hex[:8]}",
            name=name,
            source_pattern=source_pattern,
            target_role=target_role,
            priority=priority,
        )
        self._rules.append(rule)
        self._rules.sort(key=lambda r: r.priority, reverse=True)
        return rule

    def remove_rule(self, rule_id: str) -> bool:
        for i, r in enumerate(self._rules):
            if r.rule_id == rule_id:
                self._rules.pop(i)
                return True
        return False

    def route(self, message_type: str) -> AgentMetadata | None:
        for rule in self._rules:
            if rule.source_pattern in message_type or message_type in rule.source_pattern:
                target = self._find_agent_by_role(rule.target_role)
                if target is not None:
                    return target
        return None

    def route_to_specific(self, agent_id: str, message_type: str) -> str | None:
        target = self._routing_table.get(agent_id)
        if target is not None:
            return target
        agent = self._registry.get(agent_id)
        if agent is not None:
            self._routing_table[agent_id] = agent.identifier
            return agent.identifier
        return None

    def set_routing(self, agent_id: str, target_id: str) -> None:
        self._routing_table[agent_id] = target_id

    def clear_routing(self, agent_id: str) -> None:
        self._routing_table.pop(agent_id, None)

    def _find_agent_by_role(self, role: str) -> AgentMetadata | None:
        agents = self._registry.list_by_status(AgentStatus.READY)
        for a in agents:
            if a.role == role:
                return a
        agents = self._registry.list()
        for a in agents:
            if a.role == role:
                return a
        return None

    def list_rules(self) -> tuple[RoutingRule, ...]:
        return tuple(self._rules)

    def routing_table(self) -> Mapping[str, str]:
        return dict(self._routing_table)
