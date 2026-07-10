from __future__ import annotations

from dataclasses import dataclass, field

from jarvis_agents.arbitration import ConflictArbitrator
from jarvis_agents.capabilities import InMemoryCapabilityManager
from jarvis_agents.communication import InMemoryCommunicationBus
from jarvis_agents.context import SharedContext
from jarvis_agents.coordinator import InMemoryAgentCoordinator
from jarvis_agents.delegation import TaskDelegator
from jarvis_agents.discovery import InMemoryAgentDiscovery
from jarvis_agents.events import EventSystem
from jarvis_agents.goals import InMemoryGoalManager
from jarvis_agents.health import InMemoryHealthMonitor
from jarvis_agents.kernel import AgentKernel
from jarvis_agents.knowledge import InMemoryKnowledgeInterface
from jarvis_agents.lifecycle import InMemoryLifecycleManager
from jarvis_agents.memory import InMemoryMemoryInterface
from jarvis_agents.metrics import MetricsCollector
from jarvis_agents.models import (
    AgentCapability,
    AgentDefinition,
    AgentMetadata,
    AgentPolicy,
    AgentPolicyScope,
    AgentStatus,
    AgentTask,
    AgentTaskResult,
    TaskPriority,
)
from jarvis_agents.permissions import InMemoryPermissionManager
from jarvis_agents.policy import DefaultPolicyEngine
from jarvis_agents.registry import InMemoryAgentRegistry
from jarvis_agents.routing import MessageRouter
from jarvis_agents.scheduler import InMemoryAgentScheduler
from jarvis_agents.supervisor import AgentSupervisor
from jarvis_agents.tasks import InMemoryTaskManager
from jarvis_agents.tools import InMemoryToolInterface


@dataclass(slots=True)
class AgentManager:
    kernel: AgentKernel | None = None
    registry: InMemoryAgentRegistry = field(default_factory=InMemoryAgentRegistry)
    lifecycle: InMemoryLifecycleManager = field(default_factory=InMemoryLifecycleManager)
    capabilities: InMemoryCapabilityManager = field(default_factory=InMemoryCapabilityManager)
    permissions: InMemoryPermissionManager = field(default_factory=InMemoryPermissionManager)
    goals: InMemoryGoalManager = field(default_factory=InMemoryGoalManager)
    tasks: InMemoryTaskManager = field(default_factory=InMemoryTaskManager)
    communication: InMemoryCommunicationBus = field(default_factory=InMemoryCommunicationBus)
    memory: InMemoryMemoryInterface = field(default_factory=InMemoryMemoryInterface)
    knowledge: InMemoryKnowledgeInterface = field(default_factory=InMemoryKnowledgeInterface)
    health: InMemoryHealthMonitor = field(default_factory=InMemoryHealthMonitor)
    policy: DefaultPolicyEngine = field(default_factory=DefaultPolicyEngine)
    tools: InMemoryToolInterface = field(default_factory=InMemoryToolInterface)

    discovery: InMemoryAgentDiscovery = field(default_factory=lambda: InMemoryAgentDiscovery(InMemoryAgentRegistry()))
    supervisor: AgentSupervisor = field(default_factory=lambda: AgentSupervisor(
        InMemoryAgentRegistry(), InMemoryHealthMonitor(), InMemoryLifecycleManager(),
    ))
    coordinator: InMemoryAgentCoordinator = field(default_factory=lambda: InMemoryAgentCoordinator(
        InMemoryAgentRegistry(), InMemoryTaskManager(),
    ))
    delegator: TaskDelegator = field(default_factory=lambda: TaskDelegator(
        InMemoryAgentRegistry(), InMemoryTaskManager(),
    ))
    router: MessageRouter = field(default_factory=lambda: MessageRouter(InMemoryAgentRegistry()))
    arbitrator: ConflictArbitrator = field(default_factory=lambda: ConflictArbitrator(InMemoryAgentRegistry()))
    scheduler: InMemoryAgentScheduler = field(default_factory=InMemoryAgentScheduler)
    context: SharedContext = field(default_factory=SharedContext)
    events: EventSystem = field(default_factory=EventSystem)
    metrics: MetricsCollector = field(default_factory=MetricsCollector)

    def __post_init__(self) -> None:
        self.kernel = AgentKernel(
            registry=self.registry,
            lifecycle=self.lifecycle,
            capability_manager=self.capabilities,
            permission_manager=self.permissions,
            goal_manager=self.goals,
            task_manager=self.tasks,
            communication_bus=self.communication,
            memory_interface=self.memory,
            knowledge_interface=self.knowledge,
            health_monitor=self.health,
            policy_engine=self.policy,
        )
        self._link_subsystems()

    def _link_subsystems(self) -> None:
        self.discovery = InMemoryAgentDiscovery(self.registry)
        self.supervisor = AgentSupervisor(self.registry, self.health, self.lifecycle)
        self.coordinator = InMemoryAgentCoordinator(self.registry, self.tasks)
        self.delegator = TaskDelegator(self.registry, self.tasks)
        self.router = MessageRouter(self.registry)
        self.arbitrator = ConflictArbitrator(self.registry)

    def register_agent(
        self,
        definition: AgentDefinition,
        *,
        agent_id: str | None = None,
        name: str | None = None,
        owner: str,
        workspace: str,
        policy_scope: AgentPolicyScope | None = None,
        policy: AgentPolicy | None = None,
    ) -> AgentMetadata:
        agent = self.kernel.register_agent(
            definition,
            agent_id=agent_id,
            name=name,
            owner=owner,
            workspace=workspace,
            policy_scope=policy_scope,
            policy=policy,
        )
        self.discovery.build_index()
        self.metrics.record(agent.identifier, "agent_registered", 1.0)
        return agent

    def activate_agent(self, identifier: str) -> AgentMetadata:
        agent = self.kernel.activate_agent(identifier)
        self.metrics.record(identifier, "agent_activated", 1.0)
        return agent

    def suspend_agent(self, identifier: str) -> AgentMetadata:
        return self.kernel.suspend_agent(identifier)

    def deactivate_agent(self, identifier: str) -> AgentMetadata:
        return self.kernel.deactivate_agent(identifier)

    def retire_agent(self, identifier: str) -> AgentMetadata:
        return self.kernel.retire_agent(identifier)

    def recover_agent(self, identifier: str) -> AgentMetadata | None:
        result = self.supervisor.attempt_restart(identifier)
        if result:
            return self.registry.get(identifier)
        return None

    def get_agent(self, identifier: str) -> AgentMetadata | None:
        return self.kernel.get_agent(identifier)

    def list_agents(self) -> tuple[AgentMetadata, ...]:
        return self.kernel.list_agents()

    def list_ready_agents(self) -> tuple[AgentMetadata, ...]:
        return self.kernel.list_ready_agents()

    def find_agents_by_capability(self, capability_name: str) -> tuple[AgentMetadata, ...]:
        return self.discovery.find_by_capability(capability_name)

    def find_agents_by_multiple_capabilities(
        self,
        capabilities: set[str],
        require_all: bool = True,
    ):
        return self.discovery.find_by_multiple_capabilities(capabilities, require_all=require_all)

    def execute_task(self, task: AgentTask) -> AgentTaskResult:
        self.tasks.create_task(task)
        self.tasks.assign_task(task.task_id, task.assigned_agent_id)
        result = AgentTaskResult(success=True, output=f"Task {task.task_id} executed by {task.assigned_agent_id}")
        self.tasks.complete_task(task.task_id, result)
        self.metrics.record_task_success(task.assigned_agent_id)
        return result

    def create_context(self) -> str:
        return self.context.create_context()

    def health_summary(self) -> dict[str, object]:
        return self.supervisor.health_summary()

    def metrics_summary(self) -> dict[str, dict[str, object]]:
        return self.metrics.agent_summaries()

    def get_system_status(self) -> dict[str, object]:
        agents = self.list_agents()
        ready = self.list_ready_agents()
        return {
            "total_agents": len(agents),
            "ready_agents": len(ready),
            "contexts": len(self.context.list_contexts()),
            "events_processed": self.events.count(),
            "scheduled_tasks": len(self.scheduler.list_tasks()),
            "active_delegations": len(self.delegator.list_delegations()),
            "pending_conflicts": len(self.arbitrator.pending_conflicts()),
            "metrics_records": len(self.metrics.query()),
            "workflows": len(self.coordinator.list_workflows()),
        }
