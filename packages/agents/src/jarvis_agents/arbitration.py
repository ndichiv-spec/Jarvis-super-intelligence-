from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import uuid4

from jarvis_agents.models import TaskPriority
from jarvis_agents.registry import InMemoryAgentRegistry


@dataclass(frozen=True, slots=True)
class ResourceLock:
    resource_id: str
    holder_id: str
    acquired_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    ttl_seconds: float | None = None

    def is_expired(self) -> bool:
        if self.ttl_seconds is None:
            return False
        elapsed = (datetime.now(UTC) - self.acquired_at).total_seconds()
        return elapsed > self.ttl_seconds


@dataclass(frozen=True, slots=True)
class ConflictRecord:
    conflict_id: str
    agent_a_id: str
    agent_b_id: str
    resource: str
    reason: str
    resolved: bool = False
    resolution: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    resolved_at: datetime | None = None


@dataclass(slots=True)
class ConflictArbitrator:
    _registry: InMemoryAgentRegistry
    _locks: dict[str, ResourceLock] = field(default_factory=dict)
    _conflicts: list[ConflictRecord] = field(default_factory=list)
    _priority_map: dict[str, TaskPriority] = field(default_factory=dict)

    def acquire_lock(
        self,
        resource_id: str,
        agent_id: str,
        ttl_seconds: float | None = None,
    ) -> bool:
        existing = self._locks.get(resource_id)
        if existing is None or existing.is_expired():
            self._locks[resource_id] = ResourceLock(
                resource_id=resource_id,
                holder_id=agent_id,
                ttl_seconds=ttl_seconds,
            )
            return True
        return False

    def release_lock(self, resource_id: str, agent_id: str) -> bool:
        lock = self._locks.get(resource_id)
        if lock is None:
            return False
        if lock.holder_id != agent_id:
            return False
        self._locks.pop(resource_id, None)
        return True

    def get_lock(self, resource_id: str) -> ResourceLock | None:
        lock = self._locks.get(resource_id)
        if lock is None:
            return None
        if lock.is_expired():
            self._locks.pop(resource_id, None)
            return None
        return lock

    def set_priority(self, agent_id: str, priority: TaskPriority) -> None:
        self._priority_map[agent_id] = priority

    def get_priority(self, agent_id: str) -> TaskPriority:
        return self._priority_map.get(agent_id, TaskPriority.MEDIUM)

    def register_conflict(
        self,
        agent_a_id: str,
        agent_b_id: str,
        resource: str,
        reason: str,
    ) -> ConflictRecord:
        existing = self._find_active_conflict(agent_a_id, agent_b_id, resource)
        if existing is not None:
            return existing
        conflict = ConflictRecord(
            conflict_id=f"conf-{uuid4().hex[:8]}",
            agent_a_id=agent_a_id,
            agent_b_id=agent_b_id,
            resource=resource,
            reason=reason,
        )
        self._conflicts.append(conflict)
        return conflict

    def resolve_conflict(self, conflict_id: str, resolution: str) -> bool:
        for conflict in self._conflicts:
            if conflict.conflict_id == conflict_id and not conflict.resolved:
                updated = ConflictRecord(
                    conflict_id=conflict.conflict_id,
                    agent_a_id=conflict.agent_a_id,
                    agent_b_id=conflict.agent_b_id,
                    resource=conflict.resource,
                    reason=conflict.reason,
                    resolved=True,
                    resolution=resolution,
                    created_at=conflict.created_at,
                    resolved_at=datetime.now(UTC),
                )
                self._conflicts.remove(conflict)
                self._conflicts.append(updated)
                return True
        return False

    def arbitrate(self, agent_a_id: str, agent_b_id: str) -> str | None:
        priority_a = self.get_priority(agent_a_id)
        priority_b = self.get_priority(agent_b_id)
        level_a = _priority_level(priority_a)
        level_b = _priority_level(priority_b)
        if level_a > level_b:
            return agent_a_id
        if level_b > level_a:
            return agent_b_id
        return None


    def pending_conflicts(self) -> tuple[ConflictRecord, ...]:
        return tuple(c for c in self._conflicts if not c.resolved)

    def resolved_conflicts(self) -> tuple[ConflictRecord, ...]:
        return tuple(c for c in self._conflicts if c.resolved)

    def list_conflicts(self) -> tuple[ConflictRecord, ...]:
        return tuple(self._conflicts)

    def clear_expired_locks(self) -> int:
        expired = [rid for rid, lock in self._locks.items() if lock.is_expired()]
        for rid in expired:
            self._locks.pop(rid, None)
        return len(expired)

    def _find_active_conflict(self, a: str, b: str, resource: str) -> ConflictRecord | None:
        for c in self._conflicts:
            if c.resolved:
                continue
            if {c.agent_a_id, c.agent_b_id} == {a, b} and c.resource == resource:
                return c
        return None


def _priority_level(p: TaskPriority) -> int:
    levels = {
        TaskPriority.LOW: 0,
        TaskPriority.MEDIUM: 1,
        TaskPriority.HIGH: 2,
        TaskPriority.CRITICAL: 3,
    }
    return levels.get(p, 1)
