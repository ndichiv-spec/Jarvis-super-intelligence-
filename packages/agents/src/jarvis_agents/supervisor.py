from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

from jarvis_agents.health import InMemoryHealthMonitor
from jarvis_agents.lifecycle import InMemoryLifecycleManager
from jarvis_agents.models import AgentHealthReport, AgentMetadata, AgentStatus
from jarvis_agents.registry import InMemoryAgentRegistry


@dataclass(slots=True)
class EscalationPolicy:
    max_failures_before_escalation: int = 3
    escalation_contact: str = "admin"
    auto_restart_enabled: bool = True
    max_restart_attempts: int = 5
    restart_cooldown_seconds: int = 60


@dataclass(slots=True)
class AgentSupervisor:
    _registry: InMemoryAgentRegistry
    _health: InMemoryHealthMonitor
    _lifecycle: InMemoryLifecycleManager
    _escalation_policies: dict[str, EscalationPolicy] = field(default_factory=dict)
    _restart_counts: dict[str, int] = field(default_factory=dict)
    _last_restart: dict[str, datetime] = field(default_factory=dict)

    def set_escalation_policy(self, agent_id: str, policy: EscalationPolicy) -> None:
        self._escalation_policies[agent_id] = policy

    def get_policy(self, agent_id: str) -> EscalationPolicy:
        return self._escalation_policies.get(agent_id, EscalationPolicy())

    def check_health(self, agent_id: str) -> AgentHealthReport | None:
        return self._health.get_report(agent_id)

    def all_reports(self) -> tuple[AgentHealthReport, ...]:
        return self._health.list_reports()

    def unhealthy_agents(self) -> tuple[AgentHealthReport, ...]:
        return self._health.list_unhealthy()

    def attempt_restart(self, agent_id: str) -> bool:
        policy = self.get_policy(agent_id)
        if not policy.auto_restart_enabled:
            return False
        current_count = self._restart_counts.get(agent_id, 0)
        if current_count >= policy.max_restart_attempts:
            return False
        last = self._last_restart.get(agent_id)
        if last is not None:
            elapsed = (datetime.now(UTC) - last).total_seconds()
            if elapsed < policy.restart_cooldown_seconds:
                return False
        current_status = self._lifecycle.current(agent_id)
        if current_status is None:
            return False
        if current_status in (AgentStatus.RECOVERING, AgentStatus.READY):
            self._health.record_heartbeat(agent_id, AgentStatus.READY)
            self._restart_counts[agent_id] = current_count + 1
            self._last_restart[agent_id] = datetime.now(UTC)
            return True
        try:
            self._lifecycle.transition(agent_id, AgentStatus.RECOVERING)
            self._lifecycle.transition(agent_id, AgentStatus.READY)
            self._restart_counts[agent_id] = current_count + 1
            self._last_restart[agent_id] = datetime.now(UTC)
            self._health.record_heartbeat(agent_id, AgentStatus.READY)
            agent = self._registry.get(agent_id)
            if agent is not None:
                updated = agent.with_status(AgentStatus.READY)
                self._registry.update(updated)
            return True
        except (KeyError, ValueError):
            return False

    def record_failure(self, agent_id: str, error_message: str) -> AgentHealthReport:
        report = self._health.record_failure(agent_id, error_message)
        policy = self.get_policy(agent_id)
        if report.failure_count >= policy.max_failures_before_escalation:
            self._escalate(agent_id, report)
        return report

    def reset_restart_count(self, agent_id: str) -> None:
        self._restart_counts.pop(agent_id, None)
        self._last_restart.pop(agent_id, None)

    def _escalate(self, agent_id: str, report: AgentHealthReport) -> None:
        policy = self.get_policy(agent_id)
        if policy.auto_restart_enabled:
            self.attempt_restart(agent_id)

    def supervise_all(self) -> tuple[str, ...]:
        restarted: list[str] = []
        for report in self._health.list_unhealthy():
            if report.status == AgentStatus.FAILED:
                if self.attempt_restart(report.agent_id):
                    restarted.append(report.agent_id)
        return tuple(restarted)

    def health_summary(self) -> dict[str, object]:
        reports = self._health.list_reports()
        total = len(reports)
        healthy = sum(1 for r in reports if r.available)
        unhealthy = total - healthy
        failed = sum(1 for r in reports if r.status == AgentStatus.FAILED)
        return {
            "total": total,
            "healthy": healthy,
            "unhealthy": unhealthy,
            "failed": failed,
            "restart_counts": dict(self._restart_counts),
        }
