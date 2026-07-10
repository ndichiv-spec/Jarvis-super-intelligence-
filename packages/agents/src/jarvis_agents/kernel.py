from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from jarvis_agents.capabilities import InMemoryCapabilityManager
from jarvis_agents.communication import InMemoryCommunicationBus
from jarvis_agents.goals import InMemoryGoalManager
from jarvis_agents.health import InMemoryHealthMonitor
from jarvis_agents.knowledge import InMemoryKnowledgeInterface
from jarvis_agents.lifecycle import InMemoryLifecycleManager
from jarvis_agents.memory import InMemoryMemoryInterface
from jarvis_agents.models import (
    AgentCapability,
    AgentCommunicationRequest,
    AgentCommunicationResponse,
    AgentDefinition,
    AgentEvent,
    AgentGoal,
    AgentHealthReport,
    AgentMetadata,
    AgentPermission,
    AgentPolicy,
    AgentPolicyScope,
    AgentStatus,
    AgentTask,
    AgentTaskResult,
    GoalStatus,
    TaskPriority,
)
from jarvis_agents.permissions import InMemoryPermissionManager
from jarvis_agents.policy import DefaultPolicyEngine
from jarvis_agents.protocols import (
    CapabilityManager,
    CommunicationBus,
    GoalManager,
    HealthMonitor,
    KnowledgeInterface,
    LifecycleManager,
    MemoryInterface,
    PermissionManager,
    PolicyEngine,
    TaskManager,
)
from jarvis_agents.registry import InMemoryAgentRegistry
from jarvis_agents.tasks import InMemoryTaskManager


class AgentKernel:
    def __init__(
        self,
        *,
        registry: InMemoryAgentRegistry | None = None,
        lifecycle: LifecycleManager | None = None,
        capability_manager: CapabilityManager | None = None,
        permission_manager: PermissionManager | None = None,
        goal_manager: GoalManager | None = None,
        task_manager: TaskManager | None = None,
        communication_bus: CommunicationBus | None = None,
        memory_interface: MemoryInterface | None = None,
        knowledge_interface: KnowledgeInterface | None = None,
        health_monitor: HealthMonitor | None = None,
        policy_engine: PolicyEngine | None = None,
    ) -> None:
        self._registry = registry or InMemoryAgentRegistry()
        self._lifecycle = lifecycle or InMemoryLifecycleManager()
        self._capability_manager = capability_manager or InMemoryCapabilityManager()
        self._permission_manager = permission_manager or InMemoryPermissionManager()
        self._goal_manager = goal_manager or InMemoryGoalManager()
        self._task_manager = task_manager or InMemoryTaskManager()
        self._communication_bus = communication_bus or InMemoryCommunicationBus()
        self._memory_interface = memory_interface or InMemoryMemoryInterface()
        self._knowledge_interface = knowledge_interface or InMemoryKnowledgeInterface()
        self._health_monitor = health_monitor or InMemoryHealthMonitor()
        self._policy_engine = policy_engine or DefaultPolicyEngine()

    # -- Agent Registration --

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
        agent_id = agent_id or f"agent-{uuid4().hex[:8]}"
        permissions = tuple(
            AgentPermission(
                resource=p.resource,
                access=p.access,
                scope=workspace,
            )
            for p in definition.permissions
        )
        now = datetime.now(UTC)
        agent = AgentMetadata(
            identifier=agent_id,
            name=name or definition.role,
            description=definition.description,
            role=definition.role,
            capabilities=definition.capabilities,
            permissions=permissions,
            version=definition.version,
            status=AgentStatus.CREATED,
            owner=owner,
            workspace=workspace,
            policy_references=(definition.default_policy_id,),
            created_at=now,
            updated_at=now,
        )
        self._registry.register(agent)
        self._lifecycle.initialize(agent_id)

        if policy_scope is not None and policy is not None:
            self._policy_engine.register_policy(policy_scope, policy)

        return agent

    def deregister_agent(self, identifier: str) -> None:
        self._registry.deregister(identifier)

    # -- Activation --

    def _agent(self, identifier: str) -> AgentMetadata:
        agent = self._registry.get(identifier)
        if agent is None:
            msg = f"Agent not found: {identifier}"
            raise KeyError(msg)
        return agent

    def _transition_path(
        self,
        identifier: str,
        *targets: AgentStatus,
    ) -> None:
        for target in targets:
            self._lifecycle.transition(identifier, target)

    def activate_agent(self, identifier: str) -> AgentMetadata:
        self._transition_path(identifier, AgentStatus.INITIALIZING, AgentStatus.READY)
        agent = self._agent(identifier)
        updated = agent.with_status(AgentStatus.READY)
        self._registry.update(updated)
        self._health_monitor.record_heartbeat(identifier, AgentStatus.READY)
        return updated

    def suspend_agent(self, identifier: str) -> AgentMetadata:
        self._lifecycle.transition(identifier, AgentStatus.SUSPENDED)
        agent = self._agent(identifier)
        updated = agent.with_status(AgentStatus.SUSPENDED)
        self._registry.update(updated)
        self._health_monitor.record_heartbeat(identifier, AgentStatus.SUSPENDED)
        return updated

    def deactivate_agent(self, identifier: str) -> AgentMetadata:
        self._lifecycle.transition(identifier, AgentStatus.RETIRED)
        agent = self._agent(identifier)
        updated = agent.with_status(AgentStatus.RETIRED)
        self._registry.update(updated)
        self._health_monitor.record_heartbeat(identifier, AgentStatus.RETIRED)
        return updated

    def retire_agent(self, identifier: str) -> AgentMetadata:
        return self.deactivate_agent(identifier)

    def recover_agent(self, identifier: str) -> AgentMetadata:
        self._lifecycle.transition(identifier, AgentStatus.RECOVERING)
        agent = self._agent(identifier)
        updated = agent.with_status(AgentStatus.RECOVERING)
        self._registry.update(updated)
        self._health_monitor.record_heartbeat(identifier, AgentStatus.RECOVERING)
        return updated

    # -- Capability Discovery --

    def find_agents_by_capability(self, capability_name: str) -> tuple[AgentMetadata, ...]:
        all_agents = self._registry.list_by_status(AgentStatus.READY)
        return self._capability_manager.find_agents_with_capability(all_agents, capability_name)

    def discover_capabilities(self, identifier: str) -> tuple[AgentCapability, ...]:
        agent = self._registry.get(identifier)
        if agent is None:
            msg = f"Agent not found: {identifier}"
            raise KeyError(msg)
        return agent.capabilities

    # -- Permission Evaluation --

    def check_permission(
        self,
        identifier: str,
        resource: str,
        access: str,
        scope: str | None = None,
    ) -> bool:
        agent = self._registry.get(identifier)
        if agent is None:
            return False
        effective_scope = scope if scope is not None else agent.workspace
        return self._permission_manager.check_permission(agent, resource, access, effective_scope)

    # -- Goal Management --

    def create_goal(
        self,
        description: str,
        priority: TaskPriority = TaskPriority.MEDIUM,
        dependencies: tuple[str, ...] = (),
    ) -> AgentGoal:
        goal = AgentGoal(
            goal_id=f"goal-{uuid4().hex[:8]}",
            description=description,
            priority=priority,
            dependencies=dependencies,
        )
        return self._goal_manager.create_goal(goal)

    def update_goal_progress(self, goal_id: str, progress: float) -> AgentGoal:
        return self._goal_manager.update_progress(goal_id, progress)

    def complete_goal(self, goal_id: str) -> AgentGoal:
        return self._goal_manager.update_status(goal_id, GoalStatus.COMPLETED.value)

    def list_goals(self) -> tuple[AgentGoal, ...]:
        return self._goal_manager.list_goals()

    # -- Task Management --

    def create_task(
        self,
        description: str,
        assigned_agent_id: str,
        priority: TaskPriority = TaskPriority.MEDIUM,
        dependencies: tuple[str, ...] = (),
    ) -> AgentTask:
        task = AgentTask(
            task_id=f"task-{uuid4().hex[:8]}",
            description=description,
            assigned_agent_id=assigned_agent_id,
            priority=priority,
            dependencies=dependencies,
        )
        return self._task_manager.create_task(task)

    def assign_task(self, task_id: str, agent_id: str) -> AgentTask:
        return self._task_manager.assign_task(task_id, agent_id)

    def complete_task(self, task_id: str, result: AgentTaskResult) -> AgentTask:
        return self._task_manager.complete_task(task_id, result)

    def fail_task(self, task_id: str, error: str) -> AgentTask:
        return self._task_manager.fail_task(task_id, error)

    def list_tasks_by_agent(self, agent_id: str) -> tuple[AgentTask, ...]:
        return self._task_manager.list_tasks_by_agent(agent_id)

    # -- Communication --

    def send_request(
        self,
        source_agent_id: str,
        target_agent_id: str,
        message_type: str,
        payload: str,
    ) -> str:
        correlation_id = f"corr-{uuid4().hex[:8]}"
        request = AgentCommunicationRequest(
            source_agent_id=source_agent_id,
            target_agent_id=target_agent_id,
            message_type=message_type,
            payload=payload,
            correlation_id=correlation_id,
        )
        self._communication_bus.send_request(request)
        return correlation_id

    def send_response(
        self,
        correlation_id: str,
        source_agent_id: str,
        target_agent_id: str,
        payload: str,
        success: bool = True,
        error_message: str | None = None,
    ) -> None:
        response = AgentCommunicationResponse(
            correlation_id=correlation_id,
            source_agent_id=source_agent_id,
            target_agent_id=target_agent_id,
            payload=payload,
            success=success,
            error_message=error_message,
        )
        self._communication_bus.send_response(response)

    def publish_event(
        self,
        source_agent_id: str,
        event_type: str,
        payload: str,
        broadcast: bool = False,
    ) -> None:
        event = AgentEvent(
            event_id=f"evt-{uuid4().hex[:8]}",
            source_agent_id=source_agent_id,
            event_type=event_type,
            payload=payload,
            broadcast=broadcast,
        )
        self._communication_bus.publish_event(event)

    def pending_requests(self, agent_id: str) -> tuple[AgentCommunicationRequest, ...]:
        return self._communication_bus.pending_requests(agent_id)

    def pending_responses(self, correlation_id: str) -> tuple[AgentCommunicationResponse, ...]:
        return self._communication_bus.pending_responses(correlation_id)

    def pending_events(self, agent_id: str) -> tuple[AgentEvent, ...]:
        return self._communication_bus.pending_events(agent_id)

    # -- Memory --

    def store_memory(self, agent_id: str, key: str, value: str) -> None:
        if not self.check_permission(agent_id, "memory", "write"):
            msg = f"Agent {agent_id} does not have memory write permission"
            raise PermissionError(msg)
        self._memory_interface.store(agent_id, key, value)

    def retrieve_memory(self, agent_id: str, key: str) -> str | None:
        if not self.check_permission(agent_id, "memory", "read"):
            msg = f"Agent {agent_id} does not have memory read permission"
            raise PermissionError(msg)
        return self._memory_interface.retrieve(agent_id, key)

    # -- Knowledge --

    def query_knowledge(self, agent_id: str, query: str) -> tuple[str, ...]:
        if not self.check_permission(agent_id, "knowledge", "read"):
            msg = f"Agent {agent_id} does not have knowledge read permission"
            raise PermissionError(msg)
        agent = self._agent(agent_id)
        return self._knowledge_interface.search(agent_id, query, agent.workspace)

    # -- Health --

    def record_heartbeat(
        self,
        agent_id: str,
        status: AgentStatus,
        metadata: dict[str, str] | None = None,
    ) -> AgentHealthReport:
        return self._health_monitor.record_heartbeat(agent_id, status, metadata)

    def record_failure(self, agent_id: str, error_message: str) -> AgentHealthReport:
        return self._health_monitor.record_failure(agent_id, error_message)

    def get_health(self, agent_id: str) -> AgentHealthReport | None:
        return self._health_monitor.get_report(agent_id)

    def list_unhealthy_agents(self) -> tuple[AgentHealthReport, ...]:
        return self._health_monitor.list_unhealthy()

    # -- Policy --

    def register_policy(self, scope: AgentPolicyScope, policy: AgentPolicy) -> None:
        self._policy_engine.register_policy(scope, policy)

    def evaluate_policy(self, identifier: str) -> tuple[str, ...]:
        agent = self._registry.get(identifier)
        if agent is None:
            msg = f"Agent not found: {identifier}"
            raise KeyError(msg)
        scope = AgentPolicyScope(
            owner=agent.owner,
            workspace=agent.workspace,
        )
        policy = self._policy_engine.resolve(scope)
        return self._policy_engine.evaluate(agent=agent, policy=policy)

    # -- Access --

    def get_agent(self, identifier: str) -> AgentMetadata | None:
        return self._registry.get(identifier)

    def list_agents(self) -> tuple[AgentMetadata, ...]:
        return self._registry.list()

    def list_agents_by_status(self, status: AgentStatus) -> tuple[AgentMetadata, ...]:
        return self._registry.list_by_status(status)

    def list_ready_agents(self) -> tuple[AgentMetadata, ...]:
        return self._registry.list_by_status(AgentStatus.READY)
