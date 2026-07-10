from __future__ import annotations

import pytest
from jarvis_agents.capabilities import InMemoryCapabilityManager
from jarvis_agents.communication import InMemoryCommunicationBus
from jarvis_agents.definitions import DEFAULT_AGENT_DEFINITIONS
from jarvis_agents.goals import InMemoryGoalManager
from jarvis_agents.health import InMemoryHealthMonitor
from jarvis_agents.kernel import AgentKernel
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
    AgentMetadata,
    AgentPermission,
    AgentPermissionResource,
    AgentPolicy,
    AgentPolicyScope,
    AgentStatus,
    AgentTask,
    AgentTaskResult,
    GoalStatus,
    PermissionAccess,
    TaskPriority,
    TaskStatus,
)
from jarvis_agents.permissions import InMemoryPermissionManager
from jarvis_agents.policy import DefaultPolicyEngine
from jarvis_agents.registry import InMemoryAgentRegistry
from jarvis_agents.tasks import InMemoryTaskManager
from jarvis_agents.tools import InMemoryToolInterface

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_definition() -> AgentDefinition:
    return AgentDefinition(
        role="test_agent",
        description="A test agent",
        capabilities=(AgentCapability(name="test", description="Test capability"),),
        permissions=(
            AgentPermission(
                resource=AgentPermissionResource.MEMORY,
                access=PermissionAccess.WRITE,
            ),
            AgentPermission(
                resource=AgentPermissionResource.KNOWLEDGE,
                access=PermissionAccess.READ,
            ),
        ),
    )


@pytest.fixture
def sample_agent(sample_definition: AgentDefinition) -> AgentMetadata:
    return AgentMetadata(
        identifier="agent-001",
        name="TestAgent",
        description=sample_definition.description,
        role=sample_definition.role,
        capabilities=sample_definition.capabilities,
        permissions=sample_definition.permissions,
        version="1.0.0",
        status=AgentStatus.CREATED,
        owner="test_owner",
        workspace="test_workspace",
    )


@pytest.fixture
def ready_agent(sample_agent: AgentMetadata) -> AgentMetadata:
    return AgentMetadata(
        identifier=sample_agent.identifier,
        name=sample_agent.name,
        description=sample_agent.description,
        role=sample_agent.role,
        capabilities=sample_agent.capabilities,
        permissions=sample_agent.permissions,
        version=sample_agent.version,
        status=AgentStatus.READY,
        owner=sample_agent.owner,
        workspace=sample_agent.workspace,
    )


@pytest.fixture
def kernel() -> AgentKernel:
    return AgentKernel()


# ---------------------------------------------------------------------------
# InMemoryAgentRegistry
# ---------------------------------------------------------------------------


class TestInMemoryAgentRegistry:
    def test_register_and_get(self, sample_agent: AgentMetadata) -> None:
        registry = InMemoryAgentRegistry()
        registry.register(sample_agent)
        retrieved = registry.get("agent-001")
        assert retrieved is not None
        assert retrieved.identifier == "agent-001"
        assert retrieved.name == "TestAgent"

    def test_register_and_list(self, sample_agent: AgentMetadata) -> None:
        registry = InMemoryAgentRegistry()
        registry.register(sample_agent)
        all_agents = registry.list()
        assert len(all_agents) == 1

    def test_get_nonexistent(self) -> None:
        registry = InMemoryAgentRegistry()
        assert registry.get("nonexistent") is None

    def test_update(self, sample_agent: AgentMetadata) -> None:
        registry = InMemoryAgentRegistry()
        registry.register(sample_agent)
        updated = sample_agent.with_status(AgentStatus.READY)
        registry.update(updated)
        assert registry.get("agent-001") is not None
        assert registry.get("agent-001").status == AgentStatus.READY

    def test_update_nonexistent(self) -> None:
        registry = InMemoryAgentRegistry()
        agent = AgentMetadata(
            identifier="unknown",
            name="nope",
            description="",
            role="",
            capabilities=(),
            permissions=(),
            version="",
            status=AgentStatus.CREATED,
            owner="",
            workspace="",
        )
        with pytest.raises(KeyError):
            registry.update(agent)

    def test_deregister(self, sample_agent: AgentMetadata) -> None:
        registry = InMemoryAgentRegistry()
        registry.register(sample_agent)
        registry.deregister("agent-001")
        assert registry.get("agent-001") is None

    def test_list_by_status(self, sample_agent: AgentMetadata) -> None:
        registry = InMemoryAgentRegistry()
        registry.register(sample_agent)
        ready = AgentMetadata(
            identifier="agent-002",
            name=sample_agent.name,
            description=sample_agent.description,
            role=sample_agent.role,
            capabilities=sample_agent.capabilities,
            permissions=sample_agent.permissions,
            version=sample_agent.version,
            status=AgentStatus.READY,
            owner=sample_agent.owner,
            workspace=sample_agent.workspace,
        )
        registry.register(ready)
        created_list = registry.list_by_status(AgentStatus.CREATED)
        assert len(created_list) == 1
        ready_list = registry.list_by_status(AgentStatus.READY)
        assert len(ready_list) == 1

    def test_list_by_capability(self, sample_agent: AgentMetadata) -> None:
        registry = InMemoryAgentRegistry()
        registry.register(sample_agent)
        result = registry.list_by_capability("test")
        assert len(result) == 1
        result = registry.list_by_capability("nonexistent")
        assert len(result) == 0


# ---------------------------------------------------------------------------
# InMemoryLifecycleManager
# ---------------------------------------------------------------------------


class TestInMemoryLifecycleManager:
    def test_initialize_and_current(self) -> None:
        mgr = InMemoryLifecycleManager()
        mgr.initialize("agent-001")
        assert mgr.current("agent-001") == AgentStatus.CREATED

    def test_current_nonexistent(self) -> None:
        mgr = InMemoryLifecycleManager()
        assert mgr.current("nonexistent") is None

    def test_valid_transition(self) -> None:
        mgr = InMemoryLifecycleManager()
        mgr.initialize("agent-001")
        mgr.transition("agent-001", AgentStatus.INITIALIZING)
        assert mgr.current("agent-001") == AgentStatus.INITIALIZING

    def test_invalid_transition(self) -> None:
        mgr = InMemoryLifecycleManager()
        mgr.initialize("agent-001")
        with pytest.raises(ValueError, match="Cannot transition"):
            mgr.transition("agent-001", AgentStatus.READY)

    def test_transition_nonexistent(self) -> None:
        mgr = InMemoryLifecycleManager()
        with pytest.raises(KeyError):
            mgr.transition("unknown", AgentStatus.INITIALIZING)

    def test_can_transition(self) -> None:
        mgr = InMemoryLifecycleManager()
        assert mgr.can_transition(AgentStatus.CREATED, AgentStatus.INITIALIZING)
        assert not mgr.can_transition(AgentStatus.CREATED, AgentStatus.READY)
        assert mgr.can_transition(AgentStatus.READY, AgentStatus.BUSY)
        assert not mgr.can_transition(AgentStatus.RETIRED, AgentStatus.READY)

    def test_full_lifecycle(self) -> None:
        mgr = InMemoryLifecycleManager()
        mgr.initialize("agent-001")
        mgr.transition("agent-001", AgentStatus.INITIALIZING)
        mgr.transition("agent-001", AgentStatus.READY)
        mgr.transition("agent-001", AgentStatus.BUSY)
        mgr.transition("agent-001", AgentStatus.READY)
        mgr.transition("agent-001", AgentStatus.SUSPENDED)
        mgr.transition("agent-001", AgentStatus.RECOVERING)
        mgr.transition("agent-001", AgentStatus.READY)
        mgr.transition("agent-001", AgentStatus.RETIRED)
        assert mgr.current("agent-001") == AgentStatus.RETIRED


# ---------------------------------------------------------------------------
# InMemoryCapabilityManager
# ---------------------------------------------------------------------------


class TestInMemoryCapabilityManager:
    def test_register_and_get(self) -> None:
        mgr = InMemoryCapabilityManager()
        cap = AgentCapability(name="research", description="Research")
        mgr.register_capability(cap)
        assert mgr.get_capability("research") == cap

    def test_list_capabilities(self) -> None:
        mgr = InMemoryCapabilityManager()
        mgr.register_capability(AgentCapability(name="a", description="A"))
        mgr.register_capability(AgentCapability(name="b", description="B"))
        assert len(mgr.list_capabilities()) == 2

    def test_has_capability(self, sample_agent: AgentMetadata) -> None:
        mgr = InMemoryCapabilityManager()
        assert mgr.has_capability(sample_agent, "test")
        assert not mgr.has_capability(sample_agent, "nonexistent")

    def test_find_agents_with_capability(self, sample_agent: AgentMetadata) -> None:
        mgr = InMemoryCapabilityManager()
        agents = (sample_agent,)
        result = mgr.find_agents_with_capability(agents, "test")
        assert len(result) == 1
        result = mgr.find_agents_with_capability(agents, "other")
        assert len(result) == 0


# ---------------------------------------------------------------------------
# InMemoryPermissionManager
# ---------------------------------------------------------------------------


class TestInMemoryPermissionManager:
    def test_check_permission_from_agent(self, sample_agent: AgentMetadata) -> None:
        mgr = InMemoryPermissionManager()
        assert mgr.check_permission(sample_agent, "memory", "read")
        assert mgr.check_permission(sample_agent, "memory", "write")
        assert not mgr.check_permission(sample_agent, "memory", "admin")

    def test_grant_and_check(self, sample_agent: AgentMetadata) -> None:
        mgr = InMemoryPermissionManager()
        perm = AgentPermission(
            resource=AgentPermissionResource.MEMORY,
            access=PermissionAccess.WRITE,
        )
        mgr.grant_permission(sample_agent.identifier, perm)
        assert mgr.check_permission(sample_agent, "memory", "write")

    def test_revoke_permission(self, sample_agent: AgentMetadata) -> None:
        mgr = InMemoryPermissionManager()
        perm = AgentPermission(
            resource=AgentPermissionResource.TOOL,
            access=PermissionAccess.READ,
        )
        mgr.grant_permission(sample_agent.identifier, perm)
        assert mgr.check_permission(sample_agent, "tool", "read")
        mgr.revoke_permission(sample_agent.identifier, "tool")
        assert not mgr.check_permission(sample_agent, "tool", "read")

    def test_access_hierarchy(self, sample_agent: AgentMetadata) -> None:
        mgr = InMemoryPermissionManager()
        admin_perm = AgentPermission(
            resource=AgentPermissionResource.MEMORY,
            access=PermissionAccess.ADMIN,
        )
        mgr.grant_permission(sample_agent.identifier, admin_perm)
        assert mgr.check_permission(sample_agent, "memory", "read")
        assert mgr.check_permission(sample_agent, "memory", "write")
        assert mgr.check_permission(sample_agent, "memory", "admin")

    def test_scope_check(self, sample_agent: AgentMetadata) -> None:
        mgr = InMemoryPermissionManager()
        scoped = AgentPermission(
            resource=AgentPermissionResource.MEMORY,
            access=PermissionAccess.READ,
            scope="specific_workspace",
        )
        special_agent = AgentMetadata(
            identifier=sample_agent.identifier,
            name=sample_agent.name,
            description=sample_agent.description,
            role=sample_agent.role,
            capabilities=sample_agent.capabilities,
            permissions=(scoped,),
            version=sample_agent.version,
            status=sample_agent.status,
            owner=sample_agent.owner,
            workspace=sample_agent.workspace,
        )
        assert mgr.check_permission(special_agent, "memory", "read", "specific_workspace")
        assert not mgr.check_permission(special_agent, "memory", "read", "other_workspace")


# ---------------------------------------------------------------------------
# InMemoryGoalManager
# ---------------------------------------------------------------------------


class TestInMemoryGoalManager:
    def test_create_goal(self) -> None:
        mgr = InMemoryGoalManager()
        goal = AgentGoal(
            goal_id="goal-001",
            description="Test goal",
            priority=TaskPriority.HIGH,
        )
        created = mgr.create_goal(goal)
        assert created.goal_id == "goal-001"
        assert created.status == GoalStatus.ACTIVE

    def test_create_goal_generates_id(self) -> None:
        mgr = InMemoryGoalManager()
        goal = AgentGoal(
            goal_id="",
            description="Auto ID",
            priority=TaskPriority.LOW,
        )
        created = mgr.create_goal(goal)
        assert created.goal_id

    def test_get_goal(self) -> None:
        mgr = InMemoryGoalManager()
        goal = AgentGoal(goal_id="g-1", description="g1", priority=TaskPriority.MEDIUM)
        mgr.create_goal(goal)
        assert mgr.get_goal("g-1") is not None
        assert mgr.get_goal("unknown") is None

    def test_update_progress(self) -> None:
        mgr = InMemoryGoalManager()
        goal = AgentGoal(goal_id="g-1", description="g1", priority=TaskPriority.MEDIUM)
        mgr.create_goal(goal)
        updated = mgr.update_progress("g-1", 0.5)
        assert updated.progress == 0.5

    def test_update_progress_nonexistent(self) -> None:
        mgr = InMemoryGoalManager()
        with pytest.raises(KeyError):
            mgr.update_progress("unknown", 0.5)

    def test_update_status(self) -> None:
        mgr = InMemoryGoalManager()
        goal = AgentGoal(goal_id="g-1", description="g1", priority=TaskPriority.MEDIUM)
        mgr.create_goal(goal)
        updated = mgr.update_status("g-1", "completed")
        assert updated.status == GoalStatus.COMPLETED

    def test_list_goals(self) -> None:
        mgr = InMemoryGoalManager()
        g1 = AgentGoal(goal_id="g-1", description="g1", priority=TaskPriority.LOW)
        g2 = AgentGoal(goal_id="g-2", description="g2", priority=TaskPriority.HIGH)
        mgr.create_goal(g1)
        mgr.create_goal(g2)
        assert len(mgr.list_goals()) == 2

    def test_list_goals_by_status(self) -> None:
        mgr = InMemoryGoalManager()
        g1 = AgentGoal(goal_id="g-1", description="g1", priority=TaskPriority.LOW)
        mgr.create_goal(g1)
        mgr.update_status("g-1", "completed")
        g2 = AgentGoal(goal_id="g-2", description="g2", priority=TaskPriority.LOW)
        mgr.create_goal(g2)
        assert len(mgr.list_goals_by_status("active")) == 1
        assert len(mgr.list_goals_by_status("completed")) == 1


# ---------------------------------------------------------------------------
# InMemoryTaskManager
# ---------------------------------------------------------------------------


class TestInMemoryTaskManager:
    def test_create_task(self) -> None:
        mgr = InMemoryTaskManager()
        task = AgentTask(
            task_id="task-001",
            description="Test task",
            assigned_agent_id="agent-001",
        )
        created = mgr.create_task(task)
        assert created.task_id == "task-001"
        assert created.status == TaskStatus.PENDING

    def test_create_task_generates_id(self) -> None:
        mgr = InMemoryTaskManager()
        task = AgentTask(
            task_id="",
            description="Auto ID",
            assigned_agent_id="agent-001",
        )
        created = mgr.create_task(task)
        assert created.task_id

    def test_assign_task(self) -> None:
        mgr = InMemoryTaskManager()
        task = AgentTask(
            task_id="task-001",
            description="Test task",
            assigned_agent_id="",
        )
        mgr.create_task(task)
        updated = mgr.assign_task("task-001", "agent-002")
        assert updated.assigned_agent_id == "agent-002"
        assert updated.status == TaskStatus.ASSIGNED

    def test_complete_task(self) -> None:
        mgr = InMemoryTaskManager()
        task = AgentTask(
            task_id="task-001",
            description="Test task",
            assigned_agent_id="agent-001",
        )
        mgr.create_task(task)
        result = AgentTaskResult(success=True, output="Done")
        updated = mgr.complete_task("task-001", result)
        assert updated.status == TaskStatus.COMPLETED
        assert updated.result is not None
        assert updated.result.success

    def test_fail_task_with_retry(self) -> None:
        mgr = InMemoryTaskManager()
        task = AgentTask(
            task_id="task-001",
            description="Test task",
            assigned_agent_id="agent-001",
            max_retries=3,
        )
        mgr.create_task(task)
        updated = mgr.fail_task("task-001", "Error occurred")
        assert updated.status == TaskStatus.RETRY
        assert updated.retry_count == 1

    def test_fail_task_exhausts_retries(self) -> None:
        mgr = InMemoryTaskManager()
        task = AgentTask(
            task_id="task-001",
            description="Test task",
            assigned_agent_id="agent-001",
            max_retries=3,
        )
        mgr.create_task(task)
        for _ in range(3):
            updated = mgr.fail_task("task-001", "Error")
        assert updated.status == TaskStatus.RETRY
        updated = mgr.fail_task("task-001", "Final error")
        assert updated.status == TaskStatus.FAILED

    def test_retry_task(self) -> None:
        mgr = InMemoryTaskManager()
        task = AgentTask(
            task_id="task-001",
            description="Test task",
            assigned_agent_id="agent-001",
        )
        mgr.create_task(task)
        updated = mgr.retry_task("task-001")
        assert updated.status == TaskStatus.PENDING
        assert updated.retry_count == 1

    def test_list_tasks_by_agent(self) -> None:
        mgr = InMemoryTaskManager()
        t1 = AgentTask(task_id="t-1", description="t1", assigned_agent_id="a1")
        t2 = AgentTask(task_id="t-2", description="t2", assigned_agent_id="a1")
        t3 = AgentTask(task_id="t-3", description="t3", assigned_agent_id="a2")
        mgr.create_task(t1)
        mgr.create_task(t2)
        mgr.create_task(t3)
        assert len(mgr.list_tasks_by_agent("a1")) == 2
        assert len(mgr.list_tasks_by_agent("a2")) == 1

    def test_list_tasks_by_status(self) -> None:
        mgr = InMemoryTaskManager()
        t1 = AgentTask(task_id="t-1", description="t1", assigned_agent_id="a1")
        mgr.create_task(t1)
        pending = mgr.list_tasks_by_status("pending")
        assert len(pending) == 1
        completed = mgr.list_tasks_by_status("completed")
        assert len(completed) == 0

    def test_get_task(self) -> None:
        mgr = InMemoryTaskManager()
        t = AgentTask(task_id="t-1", description="t1", assigned_agent_id="a1")
        mgr.create_task(t)
        assert mgr.get_task("t-1") is not None
        assert mgr.get_task("unknown") is None


# ---------------------------------------------------------------------------
# InMemoryCommunicationBus
# ---------------------------------------------------------------------------


class TestInMemoryCommunicationBus:
    def test_send_and_pending_request(self) -> None:
        bus = InMemoryCommunicationBus()
        req = AgentCommunicationRequest(
            source_agent_id="agent-a",
            target_agent_id="agent-b",
            message_type="query",
            payload="hello",
            correlation_id="corr-001",
        )
        bus.send_request(req)
        pending = bus.pending_requests("agent-b")
        assert len(pending) == 1
        assert pending[0].message_type == "query"

    def test_send_and_pending_response(self) -> None:
        bus = InMemoryCommunicationBus()
        resp = AgentCommunicationResponse(
            correlation_id="corr-001",
            source_agent_id="agent-b",
            target_agent_id="agent-a",
            payload="response data",
            success=True,
        )
        bus.send_response(resp)
        pending = bus.pending_responses("corr-001")
        assert len(pending) == 1
        assert pending[0].success

    def test_publish_event(self) -> None:
        bus = InMemoryCommunicationBus()
        evt = AgentEvent(
            event_id="evt-001",
            source_agent_id="agent-a",
            event_type="test_event",
            payload="{}",
        )
        bus.publish_event(evt)
        pending = bus.pending_events("agent-a")
        assert len(pending) == 1
        assert pending[0].event_type == "test_event"

    def test_broadcast_event(self) -> None:
        bus = InMemoryCommunicationBus()
        bus.pending_events("agent-a")
        bus.pending_events("agent-b")
        evt = AgentEvent(
            event_id="evt-002",
            source_agent_id="agent-a",
            event_type="broadcast",
            payload="alert",
            broadcast=True,
        )
        bus.publish_event(evt)
        # Broadcast distributes to all subscribed agents
        assert len(bus.pending_events("agent-a")) == 1
        assert len(bus.pending_events("agent-b")) == 1


# ---------------------------------------------------------------------------
# InMemoryMemoryInterface
# ---------------------------------------------------------------------------


class TestInMemoryMemoryInterface:
    def test_store_and_retrieve(self) -> None:
        mem = InMemoryMemoryInterface()
        mem.store("agent-001", "key1", "value1")
        assert mem.retrieve("agent-001", "key1") == "value1"

    def test_retrieve_nonexistent(self) -> None:
        mem = InMemoryMemoryInterface()
        assert mem.retrieve("agent-001", "unknown") is None

    def test_search(self) -> None:
        mem = InMemoryMemoryInterface()
        mem.store("agent-001", "color", "blue")
        mem.store("agent-001", "size", "large")
        results = mem.search("agent-001", "color")
        assert len(results) == 1
        assert "color" in results[0]

    def test_delete(self) -> None:
        mem = InMemoryMemoryInterface()
        mem.store("agent-001", "key1", "value1")
        mem.delete("agent-001", "key1")
        assert mem.retrieve("agent-001", "key1") is None

    def test_agent_isolation(self) -> None:
        mem = InMemoryMemoryInterface()
        mem.store("agent-a", "secret", "value-a")
        mem.store("agent-b", "secret", "value-b")
        assert mem.retrieve("agent-a", "secret") == "value-a"
        assert mem.retrieve("agent-b", "secret") == "value-b"


# ---------------------------------------------------------------------------
# InMemoryKnowledgeInterface
# ---------------------------------------------------------------------------


class TestInMemoryKnowledgeInterface:
    def test_add_and_get_document(self) -> None:
        ki = InMemoryKnowledgeInterface()
        ki.add_document("doc-001", "The sky is blue")
        assert ki.get_document("agent-001", "doc-001") == "The sky is blue"

    def test_query(self) -> None:
        ki = InMemoryKnowledgeInterface()
        ki.add_document("doc-001", "Python is a programming language")
        ki.add_document("doc-002", "The sky is blue")
        results = ki.query("agent-001", "python")
        assert len(results) == 1
        assert "Python" in results[0]

    def test_search(self) -> None:
        ki = InMemoryKnowledgeInterface()
        ki.add_document("doc-001", "Machine learning is fun")
        results = ki.search("agent-001", "machine", "workspace")
        assert len(results) == 1


# ---------------------------------------------------------------------------
# InMemoryToolInterface
# ---------------------------------------------------------------------------


class TestInMemoryToolInterface:
    def test_register_tool(self) -> None:
        ti = InMemoryToolInterface()
        ti.register_tool("calculator", "Performs calculations")
        assert "calculator" in ti._tools

    def test_grant_and_check_access(self) -> None:
        ti = InMemoryToolInterface()
        ti.register_tool("calculator", "Calc")
        ti.grant_access("agent-001", "calculator")
        assert ti.check_access("agent-001", "calculator")
        assert not ti.check_access("agent-002", "calculator")

    def test_execute(self) -> None:
        ti = InMemoryToolInterface()
        ti.register_tool("calculator", "Calc")
        ti.grant_access("agent-001", "calculator")
        result = ti.execute("agent-001", "calculator", "2+2")
        assert "Executed" in result

    def test_execute_no_access(self) -> None:
        ti = InMemoryToolInterface()
        ti.register_tool("calculator", "Calc")
        with pytest.raises(PermissionError):
            ti.execute("agent-001", "calculator", "2+2")

    def test_list_available(self) -> None:
        ti = InMemoryToolInterface()
        ti.register_tool("tool-a", "A")
        ti.register_tool("tool-b", "B")
        ti.grant_access("agent-001", "tool-a")
        available = ti.list_available("agent-001")
        assert "tool-a" in available
        assert "tool-b" not in available


# ---------------------------------------------------------------------------
# InMemoryHealthMonitor
# ---------------------------------------------------------------------------


class TestInMemoryHealthMonitor:
    def test_record_heartbeat(self) -> None:
        hm = InMemoryHealthMonitor()
        report = hm.record_heartbeat("agent-001", AgentStatus.READY)
        assert report.agent_id == "agent-001"
        assert report.available

    def test_record_failure(self) -> None:
        hm = InMemoryHealthMonitor()
        report = hm.record_failure("agent-001", "Something broke")
        assert not report.available
        assert report.failure_count == 1
        assert report.last_failure_message == "Something broke"

    def test_failure_increments_count(self) -> None:
        hm = InMemoryHealthMonitor()
        hm.record_failure("agent-001", "First failure")
        report = hm.record_failure("agent-001", "Second failure")
        assert report.failure_count == 2

    def test_get_report(self) -> None:
        hm = InMemoryHealthMonitor()
        assert hm.get_report("agent-001") is None
        hm.record_heartbeat("agent-001", AgentStatus.READY)
        assert hm.get_report("agent-001") is not None

    def test_list_reports(self) -> None:
        hm = InMemoryHealthMonitor()
        hm.record_heartbeat("agent-a", AgentStatus.READY)
        hm.record_heartbeat("agent-b", AgentStatus.BUSY)
        assert len(hm.list_reports()) == 2

    def test_list_unhealthy_by_status(self) -> None:
        hm = InMemoryHealthMonitor()
        hm.record_heartbeat("agent-a", AgentStatus.READY)
        hm.record_failure("agent-b", "Failed")
        unhealthy = hm.list_unhealthy()
        ids = {r.agent_id for r in unhealthy}
        assert "agent-b" in ids
        assert "agent-a" not in ids

    def test_list_unhealthy_by_timeout(self) -> None:
        hm = InMemoryHealthMonitor()
        hm.set_heartbeat_timeout(0)  # Force timeout immediately
        hm.record_heartbeat("agent-a", AgentStatus.READY)
        unhealthy = hm.list_unhealthy()
        assert "agent-a" in {r.agent_id for r in unhealthy}


# ---------------------------------------------------------------------------
# DefaultPolicyEngine
# ---------------------------------------------------------------------------


class TestDefaultPolicyEngine:
    def test_register_and_resolve(self) -> None:
        engine = DefaultPolicyEngine()
        scope = AgentPolicyScope(owner="owner1", workspace="ws1")
        policy = AgentPolicy(
            policy_id="pol-001",
            name="Custom Policy",
            max_concurrent_tasks=3,
        )
        engine.register_policy(scope, policy)
        resolved = engine.resolve(scope)
        assert resolved.policy_id == "pol-001"
        assert resolved.max_concurrent_tasks == 3

    def test_resolve_default(self) -> None:
        engine = DefaultPolicyEngine()
        scope = AgentPolicyScope(owner="unknown", workspace="unknown")
        resolved = engine.resolve(scope)
        assert resolved.policy_id == "agent-default"

    def test_resolve_enterprise_default(self) -> None:
        engine = DefaultPolicyEngine()
        scope = AgentPolicyScope(is_enterprise=True)
        resolved = engine.resolve(scope)
        assert resolved.policy_id == "enterprise-default"
        assert resolved.enterprise_governance

    def test_evaluate_no_violations(self, sample_agent: AgentMetadata) -> None:
        engine = DefaultPolicyEngine()
        policy = AgentPolicy(policy_id="default", name="Default")
        violations = engine.evaluate(agent=sample_agent, policy=policy)
        assert len(violations) == 0

    def test_evaluate_failed_state(self) -> None:
        engine = DefaultPolicyEngine()
        agent = AgentMetadata(
            identifier="a",
            name="a",
            description="",
            role="",
            capabilities=(),
            permissions=(),
            version="",
            status=AgentStatus.FAILED,
            owner="",
            workspace="",
        )
        policy = AgentPolicy(policy_id="default", name="Default")
        violations = engine.evaluate(agent=agent, policy=policy)
        assert "failed state" in violations[0]

    def test_evaluate_denied_capabilities(self) -> None:
        engine = DefaultPolicyEngine()
        cap = AgentCapability(name="forbidden", description="Bad")
        agent = AgentMetadata(
            identifier="a",
            name="a",
            description="",
            role="",
            capabilities=(cap,),
            permissions=(),
            version="",
            status=AgentStatus.READY,
            owner="",
            workspace="",
        )
        policy = AgentPolicy(
            policy_id="default",
            name="Default",
            denied_capabilities=("forbidden",),
        )
        violations = engine.evaluate(agent=agent, policy=policy)
        assert len(violations) == 1
        assert "denied" in violations[0]

    def test_evaluate_unallowed_capabilities(self) -> None:
        engine = DefaultPolicyEngine()
        cap = AgentCapability(name="something", description="Desc")
        agent = AgentMetadata(
            identifier="a",
            name="a",
            description="",
            role="",
            capabilities=(cap,),
            permissions=(),
            version="",
            status=AgentStatus.READY,
            owner="",
            workspace="",
        )
        policy = AgentPolicy(
            policy_id="default",
            name="Default",
            allowed_capabilities=("only_allowed_one",),
        )
        violations = engine.evaluate(agent=agent, policy=policy)
        assert len(violations) == 1
        assert "not allowed" in violations[0]


# ---------------------------------------------------------------------------
# AgentKernel Integration
# ---------------------------------------------------------------------------


class TestAgentKernel:
    def test_register_agent(self, kernel: AgentKernel, sample_definition: AgentDefinition) -> None:
        meta = kernel.register_agent(
            sample_definition,
            agent_id="agent-kernel-001",
            owner="test_owner",
            workspace="test_workspace",
        )
        assert meta.identifier == "agent-kernel-001"
        assert meta.status == AgentStatus.CREATED

    def test_activate_agent(self, kernel: AgentKernel, sample_definition: AgentDefinition) -> None:
        kernel.register_agent(
            sample_definition,
            agent_id="agent-activate",
            owner="owner",
            workspace="ws",
        )
        ready = kernel.activate_agent("agent-activate")
        assert ready.status == AgentStatus.READY

    def test_suspend_agent(self, kernel: AgentKernel, sample_definition: AgentDefinition) -> None:
        kernel.register_agent(
            sample_definition,
            agent_id="agent-suspend",
            owner="owner",
            workspace="ws",
        )
        kernel.activate_agent("agent-suspend")
        suspended = kernel.suspend_agent("agent-suspend")
        assert suspended.status == AgentStatus.SUSPENDED

    def test_recover_agent(self, kernel: AgentKernel, sample_definition: AgentDefinition) -> None:
        kernel.register_agent(
            sample_definition,
            agent_id="agent-recover",
            owner="owner",
            workspace="ws",
        )
        kernel.activate_agent("agent-recover")
        kernel.suspend_agent("agent-recover")
        recovered = kernel.recover_agent("agent-recover")
        assert recovered.status == AgentStatus.RECOVERING

    def test_retire_agent(self, kernel: AgentKernel, sample_definition: AgentDefinition) -> None:
        kernel.register_agent(
            sample_definition,
            agent_id="agent-retire",
            owner="owner",
            workspace="ws",
        )
        kernel.activate_agent("agent-retire")
        retired = kernel.retire_agent("agent-retire")
        assert retired.status == AgentStatus.RETIRED

    def test_deregister_agent(
        self, kernel: AgentKernel, sample_definition: AgentDefinition
    ) -> None:
        kernel.register_agent(
            sample_definition,
            agent_id="agent-dereg",
            owner="owner",
            workspace="ws",
        )
        kernel.deregister_agent("agent-dereg")
        assert kernel.get_agent("agent-dereg") is None

    def test_list_agents(self, kernel: AgentKernel, sample_definition: AgentDefinition) -> None:
        kernel.register_agent(
            sample_definition,
            agent_id="agent-1",
            owner="owner",
            workspace="ws",
        )
        kernel.register_agent(
            sample_definition,
            agent_id="agent-2",
            owner="owner",
            workspace="ws",
        )
        assert len(kernel.list_agents()) == 2

    def test_list_ready_agents(
        self, kernel: AgentKernel, sample_definition: AgentDefinition
    ) -> None:
        kernel.register_agent(
            sample_definition,
            agent_id="agent-rdy",
            owner="owner",
            workspace="ws",
        )
        assert len(kernel.list_ready_agents()) == 0
        kernel.activate_agent("agent-rdy")
        assert len(kernel.list_ready_agents()) == 1

    def test_find_agents_by_capability(
        self,
        kernel: AgentKernel,
        sample_definition: AgentDefinition,
    ) -> None:
        kernel.register_agent(
            sample_definition,
            agent_id="agent-cap",
            owner="owner",
            workspace="ws",
        )
        kernel.activate_agent("agent-cap")
        results = kernel.find_agents_by_capability("test")
        assert len(results) == 1
        results = kernel.find_agents_by_capability("nonexistent")
        assert len(results) == 0

    def test_discover_capabilities(
        self,
        kernel: AgentKernel,
        sample_definition: AgentDefinition,
    ) -> None:
        kernel.register_agent(
            sample_definition,
            agent_id="agent-disc",
            owner="owner",
            workspace="ws",
        )
        caps = kernel.discover_capabilities("agent-disc")
        assert len(caps) == 1
        assert caps[0].name == "test"

    def test_check_permission(
        self,
        kernel: AgentKernel,
        sample_definition: AgentDefinition,
    ) -> None:
        kernel.register_agent(
            sample_definition,
            agent_id="agent-perm",
            owner="owner",
            workspace="ws",
        )
        assert kernel.check_permission("agent-perm", "memory", "read")
        assert kernel.check_permission("agent-perm", "memory", "write")
        assert not kernel.check_permission("agent-perm", "memory", "admin")
        assert not kernel.check_permission("nonexistent", "memory", "read")

    def test_goal_management(self, kernel: AgentKernel) -> None:
        goal = kernel.create_goal("Test goal", TaskPriority.HIGH)
        assert goal.goal_id
        assert goal.description == "Test goal"
        assert goal.priority == TaskPriority.HIGH

        updated = kernel.update_goal_progress(goal.goal_id, 0.75)
        assert updated.progress == 0.75

        completed = kernel.complete_goal(goal.goal_id)
        assert completed.status == GoalStatus.COMPLETED

        all_goals = kernel.list_goals()
        assert len(all_goals) >= 1

    def test_task_management(self, kernel: AgentKernel) -> None:
        task = kernel.create_task("Test task", "agent-001", TaskPriority.CRITICAL)
        assert task.task_id
        assert task.status == TaskStatus.PENDING

        assigned = kernel.assign_task(task.task_id, "agent-001")
        assert assigned.status == TaskStatus.ASSIGNED

        result = AgentTaskResult(success=True, output="Task done")
        completed = kernel.complete_task(task.task_id, result)
        assert completed.status == TaskStatus.COMPLETED

        agent_tasks = kernel.list_tasks_by_agent("agent-001")
        assert len(agent_tasks) == 1

    def test_task_failure_and_retry(self, kernel: AgentKernel) -> None:
        task = kernel.create_task("Fail task", "agent-001", TaskPriority.MEDIUM)
        failed = kernel.fail_task(task.task_id, "Error!")
        assert failed.status == TaskStatus.RETRY

    def test_communication(
        self,
        kernel: AgentKernel,
        sample_definition: AgentDefinition,
    ) -> None:
        kernel.register_agent(
            sample_definition,
            agent_id="agent-src",
            owner="owner",
            workspace="ws",
        )
        kernel.register_agent(
            sample_definition,
            agent_id="agent-tgt",
            owner="owner",
            workspace="ws",
        )
        corr_id = kernel.send_request("agent-src", "agent-tgt", "greeting", "Hello")
        assert corr_id

        reqs = kernel.pending_requests("agent-tgt")
        assert len(reqs) == 1

        kernel.send_response(corr_id, "agent-tgt", "agent-src", "Hi back", True)
        resps = kernel.pending_responses(corr_id)
        assert len(resps) == 1
        assert resps[0].success

    def test_events(self, kernel: AgentKernel) -> None:
        kernel.publish_event("agent-001", "status_change", '{"status": "ready"}')
        events = kernel.pending_events("agent-001")
        assert len(events) == 1

    def test_memory_with_permission(
        self, kernel: AgentKernel, sample_definition: AgentDefinition
    ) -> None:
        kernel.register_agent(
            sample_definition,
            agent_id="agent-mem",
            owner="owner",
            workspace="ws",
        )
        kernel.activate_agent("agent-mem")
        kernel.store_memory("agent-mem", "key1", "value1")
        assert kernel.retrieve_memory("agent-mem", "key1") == "value1"

    def test_memory_without_permission(self, kernel: AgentKernel) -> None:
        # Agent with no memory permissions
        defn = AgentDefinition(
            role="no_perm",
            description="No permissions",
            capabilities=(),
            permissions=(),
        )
        kernel.register_agent(defn, agent_id="agent-no-mem", owner="o", workspace="w")
        kernel.activate_agent("agent-no-mem")
        with pytest.raises(PermissionError):
            kernel.store_memory("agent-no-mem", "k", "v")

    def test_knowledge_with_permission(
        self, kernel: AgentKernel, sample_definition: AgentDefinition
    ) -> None:
        kernel.register_agent(
            sample_definition,
            agent_id="agent-know",
            owner="owner",
            workspace="ws",
        )
        kernel.activate_agent("agent-know")
        # Add a document directly on the knowledge interface
        kernel._knowledge_interface.add_document("doc-001", "Test knowledge content", "ws")
        results = kernel.query_knowledge("agent-know", "test")
        assert len(results) >= 1

    def test_health_monitoring(
        self, kernel: AgentKernel, sample_definition: AgentDefinition
    ) -> None:
        kernel.register_agent(
            sample_definition,
            agent_id="agent-health",
            owner="owner",
            workspace="ws",
        )
        kernel.activate_agent("agent-health")
        report = kernel.get_health("agent-health")
        assert report is not None
        assert report.available

        fail_report = kernel.record_failure("agent-health", "Test failure")
        assert not fail_report.available

        unhealthy = kernel.list_unhealthy_agents()
        assert len(unhealthy) >= 1

    def test_policy_evaluation(
        self, kernel: AgentKernel, sample_definition: AgentDefinition
    ) -> None:
        scope = AgentPolicyScope(owner="owner", workspace="ws")
        policy = AgentPolicy(
            policy_id="pol-test",
            name="Test Policy",
        )
        kernel.register_policy(scope, policy)
        kernel.register_agent(
            sample_definition,
            agent_id="agent-pol",
            owner="owner",
            workspace="ws",
            policy_scope=scope,
            policy=policy,
        )
        violations = kernel.evaluate_policy("agent-pol")
        assert len(violations) == 0

    def test_register_agent_with_default_definitions(self, kernel: AgentKernel) -> None:
        for defn in DEFAULT_AGENT_DEFINITIONS:
            meta = kernel.register_agent(
                defn,
                agent_id=f"agent-{defn.role}",
                owner="system",
                workspace="default",
            )
            assert meta.role == defn.role

        all_agents = kernel.list_agents()
        assert len(all_agents) == len(DEFAULT_AGENT_DEFINITIONS)

    def test_full_workflow(self, kernel: AgentKernel) -> None:
        research_def = next(d for d in DEFAULT_AGENT_DEFINITIONS if d.role == "research")
        engineering_def = next(d for d in DEFAULT_AGENT_DEFINITIONS if d.role == "engineering")

        kernel.register_agent(
            research_def,
            agent_id="researcher",
            owner="user1",
            workspace="project-x",
        )
        kernel.register_agent(
            engineering_def,
            agent_id="engineer",
            owner="user1",
            workspace="project-x",
        )

        kernel.activate_agent("researcher")
        kernel.activate_agent("engineer")

        kernel.send_request("researcher", "engineer", "task", "Implement feature X")
        requests = kernel.pending_requests("engineer")
        assert len(requests) == 1

        kernel.store_memory("engineer", "finding", "Found a bug")
        bug = kernel.retrieve_memory("engineer", "finding")
        assert bug == "Found a bug"

        goal = kernel.create_goal("Complete feature X", TaskPriority.HIGH)
        kernel.update_goal_progress(goal.goal_id, 1.0)
        kernel.complete_goal(goal.goal_id)

        task = kernel.create_task("Write code", "engineer", TaskPriority.HIGH)
        result = AgentTaskResult(success=True, output="Code written")
        kernel.complete_task(task.task_id, result)

        assert kernel.get_health("researcher") is not None
        assert kernel.get_health("engineer") is not None

        ready = kernel.list_ready_agents()
        assert len(ready) == 2


# ---------------------------------------------------------------------------
# DEFAULT_AGENT_DEFINITIONS
# ---------------------------------------------------------------------------


class TestDefaultAgentDefinitions:
    def test_all_definitions_have_required_fields(self) -> None:
        for defn in DEFAULT_AGENT_DEFINITIONS:
            assert defn.role
            assert defn.description
            assert len(defn.capabilities) > 0

    def test_all_roles_unique(self) -> None:
        roles = [d.role for d in DEFAULT_AGENT_DEFINITIONS]
        assert len(roles) == len(set(roles))

    def test_contains_core_roles(self) -> None:
        roles = {d.role for d in DEFAULT_AGENT_DEFINITIONS}
        assert "research" in roles
        assert "engineering" in roles
        assert "planning" in roles
        assert "testing" in roles
