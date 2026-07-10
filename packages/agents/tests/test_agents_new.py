from __future__ import annotations

import pytest
from datetime import UTC, datetime, timedelta
from jarvis_agents.agents import (
    AutomationAgent,
    BaseAgent,
    CodingAgent,
    CommunicationAgent,
    DesktopAgent,
    MemoryAgent,
    PlannerAgent,
    ResearchAgent,
    VisionAgent,
    VoiceAgent,
    WebIntelligenceAgent,
)
from jarvis_agents.arbitration import ConflictArbitrator, ResourceLock, ConflictRecord
from jarvis_agents.communication import InMemoryCommunicationBus
from jarvis_agents.context import SharedContext, ContextEntry
from jarvis_agents.coordinator import InMemoryAgentCoordinator, WorkflowStep
from jarvis_agents.delegation import TaskDelegator, Delegation
from jarvis_agents.discovery import InMemoryAgentDiscovery, CapabilityMatch
from jarvis_agents.events import EventSystem, TypedEvent
from jarvis_agents.interfaces import Agent
from jarvis_agents.manager import AgentManager
from jarvis_agents.metrics import MetricsCollector, MetricRecord
from jarvis_agents.models import (
    AgentCapability,
    AgentDefinition,
    AgentMetadata,
    AgentPermission,
    AgentPermissionResource,
    AgentStatus,
    AgentTask,
    AgentTaskResult,
    PermissionAccess,
    TaskPriority,
    TaskStatus,
)
from jarvis_agents.registry import InMemoryAgentRegistry
from jarvis_agents.routing import MessageRouter, RoutingRule
from jarvis_agents.scheduler import InMemoryAgentScheduler, ScheduledTask
from jarvis_agents.supervisor import AgentSupervisor, EscalationPolicy
from jarvis_agents.tasks import InMemoryTaskManager
from jarvis_agents.health import InMemoryHealthMonitor
from jarvis_agents.lifecycle import InMemoryLifecycleManager


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_agent() -> AgentMetadata:
    return AgentMetadata(
        identifier="agent-001",
        name="TestAgent",
        description="A test agent",
        role="test",
        capabilities=(AgentCapability(name="test", description="Test capability"),),
        permissions=(AgentPermission(resource=AgentPermissionResource.MEMORY, access=PermissionAccess.WRITE),),
        version="1.0.0",
        status=AgentStatus.READY,
        owner="owner",
        workspace="ws",
    )


@pytest.fixture
def registry(sample_agent: AgentMetadata) -> InMemoryAgentRegistry:
    r = InMemoryAgentRegistry()
    r.register(sample_agent)
    return r


@pytest.fixture
def task_manager() -> InMemoryTaskManager:
    return InMemoryTaskManager()


@pytest.fixture
def health() -> InMemoryHealthMonitor:
    return InMemoryHealthMonitor()


@pytest.fixture
def lifecycle() -> InMemoryLifecycleManager:
    return InMemoryLifecycleManager()


# ---------------------------------------------------------------------------
# InMemoryAgentDiscovery
# ---------------------------------------------------------------------------


class TestInMemoryAgentDiscovery:
    def test_build_index_and_find_by_capability(self, registry: InMemoryAgentRegistry) -> None:
        discovery = InMemoryAgentDiscovery(registry)
        discovery.build_index()
        results = discovery.find_by_capability("test")
        assert len(results) == 1
        assert results[0].identifier == "agent-001"

    def test_find_by_capability_no_match(self, registry: InMemoryAgentRegistry) -> None:
        discovery = InMemoryAgentDiscovery(registry)
        discovery.build_index()
        results = discovery.find_by_capability("nonexistent")
        assert len(results) == 0

    def test_find_by_multiple_capabilities(self, registry: InMemoryAgentRegistry) -> None:
        discovery = InMemoryAgentDiscovery(registry)
        discovery.build_index()
        matches = discovery.find_by_multiple_capabilities({"test"})
        assert len(matches) == 1
        assert matches[0].score == 1.0

    def test_find_by_multiple_require_all(self, registry: InMemoryAgentRegistry) -> None:
        discovery = InMemoryAgentDiscovery(registry)
        discovery.build_index()
        matches = discovery.find_by_multiple_capabilities({"test", "nonexistent"}, require_all=True)
        assert len(matches) == 0

    def test_find_by_workspace(self, registry: InMemoryAgentRegistry) -> None:
        discovery = InMemoryAgentDiscovery(registry)
        discovery.build_index()
        results = discovery.find_by_workspace("ws")
        assert len(results) == 1

    def test_find_nearest_capability(self, registry: InMemoryAgentRegistry) -> None:
        discovery = InMemoryAgentDiscovery(registry)
        discovery.build_index()
        agent = discovery.find_nearest_capability("test")
        assert agent is not None
        assert agent.identifier == "agent-001"

    def test_count_by_capability(self, registry: InMemoryAgentRegistry) -> None:
        discovery = InMemoryAgentDiscovery(registry)
        discovery.build_index()
        counts = discovery.count_by_capability()
        assert counts.get("test") == 1

    def test_list_all_capabilities(self, registry: InMemoryAgentRegistry) -> None:
        discovery = InMemoryAgentDiscovery(registry)
        discovery.build_index()
        caps = discovery.list_all_capabilities()
        assert len(caps) == 1
        assert caps[0].name == "test"

    def test_capability_match_structure(self) -> None:
        agent = AgentMetadata(
            identifier="a", name="a", description="", role="",
            capabilities=(AgentCapability(name="c1", description="d1"),),
            permissions=(), version="", status=AgentStatus.READY, owner="o", workspace="w",
        )
        match = CapabilityMatch(
            agent=agent,
            matched_capabilities=(AgentCapability(name="c1", description="d1"),),
            score=0.5,
        )
        assert match.score == 0.5
        assert match.agent.identifier == "a"


# ---------------------------------------------------------------------------
# AgentSupervisor
# ---------------------------------------------------------------------------


class TestAgentSupervisor:
    def test_check_health(self, registry: InMemoryAgentRegistry, health: InMemoryHealthMonitor, lifecycle: InMemoryLifecycleManager) -> None:
        supervisor = AgentSupervisor(registry, health, lifecycle)
        health.record_heartbeat("agent-001", AgentStatus.READY)
        report = supervisor.check_health("agent-001")
        assert report is not None
        assert report.available

    def test_health_summary(self, registry: InMemoryAgentRegistry, health: InMemoryHealthMonitor, lifecycle: InMemoryLifecycleManager) -> None:
        supervisor = AgentSupervisor(registry, health, lifecycle)
        health.record_heartbeat("agent-001", AgentStatus.READY)
        summary = supervisor.health_summary()
        assert summary["total"] == 1
        assert summary["healthy"] == 1

    def test_attempt_restart(self, registry: InMemoryAgentRegistry, health: InMemoryHealthMonitor, lifecycle: InMemoryLifecycleManager) -> None:
        lifecycle.initialize("agent-001")
        lifecycle.transition("agent-001", AgentStatus.INITIALIZING)
        lifecycle.transition("agent-001", AgentStatus.READY)
        supervisor = AgentSupervisor(registry, health, lifecycle)
        result = supervisor.attempt_restart("agent-001")
        assert result

    def test_record_failure(self, registry: InMemoryAgentRegistry, health: InMemoryHealthMonitor, lifecycle: InMemoryLifecycleManager) -> None:
        supervisor = AgentSupervisor(registry, health, lifecycle)
        report = supervisor.record_failure("agent-001", "error")
        assert not report.available

    def test_supervise_all(self, registry: InMemoryAgentRegistry, health: InMemoryHealthMonitor, lifecycle: InMemoryLifecycleManager) -> None:
        lifecycle.initialize("agent-001")
        lifecycle.transition("agent-001", AgentStatus.INITIALIZING)
        lifecycle.transition("agent-001", AgentStatus.READY)
        health.record_failure("agent-001", "fail")
        supervisor = AgentSupervisor(registry, health, lifecycle)
        restarted = supervisor.supervise_all()
        assert len(restarted) >= 0

    def test_escalation_policy(self, registry: InMemoryAgentRegistry, health: InMemoryHealthMonitor, lifecycle: InMemoryLifecycleManager) -> None:
        supervisor = AgentSupervisor(registry, health, lifecycle)
        policy = EscalationPolicy(max_failures_before_escalation=1, auto_restart_enabled=False)
        supervisor.set_escalation_policy("agent-001", policy)
        assert supervisor.get_policy("agent-001").max_failures_before_escalation == 1

    def test_reset_restart_count(self, registry: InMemoryAgentRegistry, health: InMemoryHealthMonitor, lifecycle: InMemoryLifecycleManager) -> None:
        supervisor = AgentSupervisor(registry, health, lifecycle)
        supervisor._restart_counts["agent-001"] = 3
        supervisor.reset_restart_count("agent-001")
        assert supervisor._restart_counts.get("agent-001") is None


# ---------------------------------------------------------------------------
# InMemoryAgentCoordinator
# ---------------------------------------------------------------------------


class TestInMemoryAgentCoordinator:
    def test_create_workflow(self, registry: InMemoryAgentRegistry, task_manager: InMemoryTaskManager) -> None:
        coord = InMemoryAgentCoordinator(registry, task_manager)
        step = WorkflowStep(step_id="s1", agent_role="test", task_description="do something")
        wf = coord.create_workflow("test-wf", (step,))
        assert wf.name == "test-wf"
        assert len(wf.steps) == 1

    def test_get_workflow(self, registry: InMemoryAgentRegistry, task_manager: InMemoryTaskManager) -> None:
        coord = InMemoryAgentCoordinator(registry, task_manager)
        step = WorkflowStep(step_id="s1", agent_role="test", task_description="do")
        wf = coord.create_workflow("wf", (step,))
        assert coord.get_workflow(wf.workflow_id) is not None

    def test_list_workflows(self, registry: InMemoryAgentRegistry, task_manager: InMemoryTaskManager) -> None:
        coord = InMemoryAgentCoordinator(registry, task_manager)
        step = WorkflowStep(step_id="s1", agent_role="test", task_description="do")
        coord.create_workflow("wf1", (step,))
        coord.create_workflow("wf2", (step,))
        assert len(coord.list_workflows()) == 2

    def test_start_workflow(self, registry: InMemoryAgentRegistry, task_manager: InMemoryTaskManager) -> None:
        coord = InMemoryAgentCoordinator(registry, task_manager)
        step = WorkflowStep(step_id="s1", agent_role="test", task_description="do")
        wf = coord.create_workflow("wf", (step,))
        started = coord.start_workflow(wf.workflow_id)
        assert started is not None
        assert started.status == "running"


# ---------------------------------------------------------------------------
# InMemoryCommunicationBus (enhanced)
# ---------------------------------------------------------------------------


class TestInMemoryCommunicationBusEnhanced:
    def test_subscribe_and_dispatch(self) -> None:
        bus = InMemoryCommunicationBus()
        received: list[str] = []

        def handler(event):
            received.append(event.payload)

        bus.subscribe("sub-1", handler)
        from jarvis_agents.models import AgentEvent
        bus.publish_event(AgentEvent(
            event_id="e1", source_agent_id="src", event_type="test", payload="hello"
        ))
        assert len(received) >= 1

    def test_event_filter(self) -> None:
        bus = InMemoryCommunicationBus()
        received: list[str] = []

        def handler(event):
            received.append(event.payload)

        bus.subscribe("sub-1", handler)
        bus.add_event_filter("sub-1", "allowed")
        from jarvis_agents.models import AgentEvent
        bus.publish_event(AgentEvent(event_id="e1", source_agent_id="src", event_type="blocked", payload="nope"))
        assert len(received) == 0
        bus.publish_event(AgentEvent(event_id="e2", source_agent_id="src", event_type="allowed", payload="yes"))
        assert len(received) >= 1

    def test_drain_requests(self) -> None:
        bus = InMemoryCommunicationBus()
        from jarvis_agents.models import AgentCommunicationRequest
        req = AgentCommunicationRequest(
            source_agent_id="a", target_agent_id="b", message_type="t", payload="p", correlation_id="c"
        )
        bus.send_request(req)
        drained = bus.drain_requests("b")
        assert len(drained) == 1
        assert len(bus.pending_requests("b")) == 0

    def test_drain_events(self) -> None:
        bus = InMemoryCommunicationBus()
        from jarvis_agents.models import AgentEvent
        bus.publish_event(AgentEvent(event_id="e1", source_agent_id="src", event_type="t", payload="p"))
        drained = bus.drain_events("src")
        assert len(drained) == 1
        assert len(bus.pending_events("src")) == 0

    def test_event_count(self) -> None:
        bus = InMemoryCommunicationBus()
        from jarvis_agents.models import AgentEvent
        bus.publish_event(AgentEvent(event_id="e1", source_agent_id="src", event_type="t", payload="p"))
        assert bus.event_count() >= 1

    def test_clear(self) -> None:
        bus = InMemoryCommunicationBus()
        from jarvis_agents.models import AgentEvent
        bus.publish_event(AgentEvent(event_id="e1", source_agent_id="src", event_type="t", payload="p"))
        bus.clear()
        assert bus.event_count() == 0


# ---------------------------------------------------------------------------
# InMemoryAgentScheduler
# ---------------------------------------------------------------------------


class TestInMemoryAgentScheduler:
    def test_schedule_and_cancel(self) -> None:
        sched = InMemoryAgentScheduler()
        called = False

        def handler() -> None:
            nonlocal called
            called = True

        task = sched.schedule("test", 60.0, "do_stuff", handler)
        assert task.name == "test"
        assert sched.cancel(task.task_id)
        assert sched.get_task(task.task_id) is None

    def test_pause_and_resume(self) -> None:
        sched = InMemoryAgentScheduler()

        def handler() -> None:
            pass

        task = sched.schedule("test", 60.0, "do_stuff", handler)
        assert sched.pause(task.task_id)
        paused = sched.get_task(task.task_id)
        assert paused is not None
        assert not paused.enabled
        assert sched.resume(task.task_id)
        resumed = sched.get_task(task.task_id)
        assert resumed is not None
        assert resumed.enabled

    def test_tick(self) -> None:
        sched = InMemoryAgentScheduler()
        called = False

        def handler() -> None:
            nonlocal called
            called = True

        sched.schedule("test", 0.0, "do_stuff", handler)
        from datetime import timedelta
        for t in sched._scheduled_tasks.values():
            sched._scheduled_tasks[t.task_id] = ScheduledTask(
                task_id=t.task_id, name=t.name, interval_seconds=t.interval_seconds,
                action=t.action, enabled=True,
                last_run=t.last_run,
                next_run=datetime.now(UTC) - timedelta(seconds=1),
                created_at=t.created_at,
            )
        executed = sched.tick()
        assert len(executed) >= 1

    def test_list_tasks(self) -> None:
        sched = InMemoryAgentScheduler()

        def handler() -> None:
            pass

        sched.schedule("a", 10.0, "act", handler)
        sched.schedule("b", 20.0, "act", handler)
        assert len(sched.list_tasks()) == 2

    def test_clear(self) -> None:
        sched = InMemoryAgentScheduler()

        def handler() -> None:
            pass

        sched.schedule("a", 10.0, "act", handler)
        sched.clear()
        assert len(sched.list_tasks()) == 0

    def test_cancel_nonexistent(self) -> None:
        sched = InMemoryAgentScheduler()
        assert not sched.cancel("nonexistent")


# ---------------------------------------------------------------------------
# SharedContext
# ---------------------------------------------------------------------------


class TestSharedContext:
    def test_create_and_set_get(self) -> None:
        ctx = SharedContext()
        cid = ctx.create_context()
        entry = ctx.set(cid, "key1", "value1", "agent-001")
        assert isinstance(entry, ContextEntry)
        assert ctx.get(cid, "key1") == "value1"

    def test_get_nonexistent_key(self) -> None:
        ctx = SharedContext()
        cid = ctx.create_context()
        assert ctx.get(cid, "nonexistent") is None

    def test_get_nonexistent_context(self) -> None:
        ctx = SharedContext()
        assert ctx.get("nonexistent", "key") is None

    def test_get_all(self) -> None:
        ctx = SharedContext()
        cid = ctx.create_context()
        ctx.set(cid, "a", "1", "agent-001")
        ctx.set(cid, "b", "2", "agent-001")
        all_vals = ctx.get_all(cid)
        assert dict(all_vals) == {"a": "1", "b": "2"}

    def test_delete(self) -> None:
        ctx = SharedContext()
        cid = ctx.create_context()
        ctx.set(cid, "key1", "value1", "agent-001")
        assert ctx.delete(cid, "key1")
        assert ctx.get(cid, "key1") is None

    def test_destroy_context(self) -> None:
        ctx = SharedContext()
        cid = ctx.create_context()
        ctx.set(cid, "k", "v", "agent-001")
        assert ctx.destroy_context(cid)
        assert ctx.get(cid, "k") is None

    def test_get_entry(self) -> None:
        ctx = SharedContext()
        cid = ctx.create_context()
        ctx.set(cid, "k", "v", "agent-001")
        entry = ctx.get_entry(cid, "k")
        assert entry is not None
        assert entry.value == "v"
        assert entry.source_agent_id == "agent-001"

    def test_get_history(self) -> None:
        ctx = SharedContext()
        cid = ctx.create_context()
        ctx.set(cid, "k", "v1", "agent-001")
        ctx.set(cid, "k", "v2", "agent-001")
        history = ctx.get_history(cid)
        assert len(history) == 2

    def test_list_contexts(self) -> None:
        ctx = SharedContext()
        cid1 = ctx.create_context()
        cid2 = ctx.create_context()
        assert cid1 in ctx.list_contexts()
        assert cid2 in ctx.list_contexts()

    def test_search(self) -> None:
        ctx = SharedContext()
        cid = ctx.create_context()
        ctx.set(cid, "color", "blue", "agent-001")
        results = ctx.search("blue")
        assert len(results) == 1

    def test_clear(self) -> None:
        ctx = SharedContext()
        ctx.create_context()
        ctx.clear()
        assert len(ctx.list_contexts()) == 0

    def test_set_nonexistent_context_raises(self) -> None:
        ctx = SharedContext()
        with pytest.raises(KeyError):
            ctx.set("nonexistent", "k", "v", "agent-001")

    def test_delete_nonexistent_context(self) -> None:
        ctx = SharedContext()
        assert not ctx.delete("nonexistent", "k")

    def test_destroy_nonexistent_context(self) -> None:
        ctx = SharedContext()
        assert not ctx.destroy_context("nonexistent")


# ---------------------------------------------------------------------------
# MessageRouter
# ---------------------------------------------------------------------------


class TestMessageRouter:
    def test_add_rule_and_route(self, registry: InMemoryAgentRegistry) -> None:
        router = MessageRouter(registry)
        router.add_rule("test-rule", "query", "test")
        result = router.route("query")
        assert result is not None
        assert result.identifier == "agent-001"

    def test_route_no_match(self, registry: InMemoryAgentRegistry) -> None:
        router = MessageRouter(registry)
        router.add_rule("rule", "something", "nonexistent")
        result = router.route("query")
        assert result is None

    def test_remove_rule(self, registry: InMemoryAgentRegistry) -> None:
        router = MessageRouter(registry)
        rule = router.add_rule("rule", "query", "test")
        assert router.remove_rule(rule.rule_id)
        assert len(router.list_rules()) == 0

    def test_route_to_specific(self, registry: InMemoryAgentRegistry) -> None:
        router = MessageRouter(registry)
        result = router.route_to_specific("agent-001", "query")
        assert result == "agent-001"

    def test_set_routing_table(self, registry: InMemoryAgentRegistry) -> None:
        router = MessageRouter(registry)
        router.set_routing("source", "target")
        assert router.route_to_specific("source", "msg") == "target"

    def test_clear_routing(self, registry: InMemoryAgentRegistry) -> None:
        router = MessageRouter(registry)
        router.set_routing("source", "target")
        assert router.route_to_specific("source", "msg") == "target"
        router.clear_routing("source")
        assert router.route_to_specific("source", "msg") is None

    def test_list_rules(self, registry: InMemoryAgentRegistry) -> None:
        router = MessageRouter(registry)
        router.add_rule("r1", "a", "test")
        router.add_rule("r2", "b", "test")
        assert len(router.list_rules()) == 2


# ---------------------------------------------------------------------------
# TaskDelegator
# ---------------------------------------------------------------------------


class TestTaskDelegator:
    def test_delegate(self, registry: InMemoryAgentRegistry, task_manager: InMemoryTaskManager) -> None:
        delegator = TaskDelegator(registry, task_manager)
        parent = AgentTask(task_id="parent-001", description="parent", assigned_agent_id="test")
        delegation = delegator.delegate(parent, (("sub1", "test"), ("sub2", "test")))
        assert delegation.strategy == "sequential"
        assert len(delegation.subtask_ids) == 2

    def test_get_delegation(self, registry: InMemoryAgentRegistry, task_manager: InMemoryTaskManager) -> None:
        delegator = TaskDelegator(registry, task_manager)
        parent = AgentTask(task_id="p1", description="parent", assigned_agent_id="test")
        d = delegator.delegate(parent, (("sub", "test"),))
        assert delegator.get_delegation(d.delegation_id) is not None

    def test_list_delegations(self, registry: InMemoryAgentRegistry, task_manager: InMemoryTaskManager) -> None:
        delegator = TaskDelegator(registry, task_manager)
        parent = AgentTask(task_id="p1", description="parent", assigned_agent_id="test")
        delegator.delegate(parent, (("sub", "test"),))
        delegator.delegate(parent, (("sub2", "test"),))
        assert len(delegator.list_delegations()) == 2

    def test_complete_subtask(self, registry: InMemoryAgentRegistry, task_manager: InMemoryTaskManager) -> None:
        delegator = TaskDelegator(registry, task_manager)
        parent = AgentTask(task_id="p1", description="parent", assigned_agent_id="test")
        d = delegator.delegate(parent, (("sub1", "test"),))
        sid = d.subtask_ids[0]
        result = AgentTaskResult(success=True, output="done")
        assert delegator.complete_subtask(sid, result)

    def test_fail_subtask(self, registry: InMemoryAgentRegistry, task_manager: InMemoryTaskManager) -> None:
        delegator = TaskDelegator(registry, task_manager)
        parent = AgentTask(task_id="p1", description="parent", assigned_agent_id="test")
        d = delegator.delegate(parent, (("sub1", "test"),))
        sid = d.subtask_ids[0]
        assert delegator.fail_subtask(sid, "error")

    def test_delegation_status(self, registry: InMemoryAgentRegistry, task_manager: InMemoryTaskManager) -> None:
        delegator = TaskDelegator(registry, task_manager)
        parent = AgentTask(task_id="p1", description="parent", assigned_agent_id="test")
        d = delegator.delegate(parent, (("sub1", "test"),))
        status = delegator.delegation_status(d.delegation_id)
        assert status is not None
        assert status["status"] == "active"


# ---------------------------------------------------------------------------
# ConflictArbitrator
# ---------------------------------------------------------------------------


class TestConflictArbitrator:
    def test_acquire_lock(self, registry: InMemoryAgentRegistry) -> None:
        arb = ConflictArbitrator(registry)
        assert arb.acquire_lock("resource-1", "agent-001")
        assert not arb.acquire_lock("resource-1", "agent-002")

    def test_release_lock(self, registry: InMemoryAgentRegistry) -> None:
        arb = ConflictArbitrator(registry)
        arb.acquire_lock("r1", "agent-001")
        assert arb.release_lock("r1", "agent-001")
        assert arb.acquire_lock("r1", "agent-002")

    def test_release_lock_wrong_owner(self, registry: InMemoryAgentRegistry) -> None:
        arb = ConflictArbitrator(registry)
        arb.acquire_lock("r1", "agent-001")
        assert not arb.release_lock("r1", "agent-002")

    def test_get_lock(self, registry: InMemoryAgentRegistry) -> None:
        arb = ConflictArbitrator(registry)
        arb.acquire_lock("r1", "agent-001")
        lock = arb.get_lock("r1")
        assert lock is not None
        assert lock.holder_id == "agent-001"

    def test_set_and_get_priority(self, registry: InMemoryAgentRegistry) -> None:
        arb = ConflictArbitrator(registry)
        arb.set_priority("agent-001", TaskPriority.HIGH)
        assert arb.get_priority("agent-001") == TaskPriority.HIGH

    def test_arbitrate_by_priority(self, registry: InMemoryAgentRegistry) -> None:
        arb = ConflictArbitrator(registry)
        arb.set_priority("agent-001", TaskPriority.HIGH)
        arb.set_priority("agent-002", TaskPriority.LOW)
        winner = arb.arbitrate("agent-001", "agent-002")
        assert winner == "agent-001"

    def test_arbitrate_equal_priority(self, registry: InMemoryAgentRegistry) -> None:
        arb = ConflictArbitrator(registry)
        arb.set_priority("agent-001", TaskPriority.MEDIUM)
        arb.set_priority("agent-002", TaskPriority.MEDIUM)
        assert arb.arbitrate("agent-001", "agent-002") is None

    def test_register_and_resolve_conflict(self, registry: InMemoryAgentRegistry) -> None:
        arb = ConflictArbitrator(registry)
        conflict = arb.register_conflict("agent-001", "agent-002", "resource-1", "contention")
        assert conflict.reason == "contention"
        assert arb.resolve_conflict(conflict.conflict_id, "granted to agent-001")

    def test_pending_conflicts(self, registry: InMemoryAgentRegistry) -> None:
        arb = ConflictArbitrator(registry)
        arb.register_conflict("a", "b", "r1", "reason")
        assert len(arb.pending_conflicts()) == 1

    def test_resolved_conflicts(self, registry: InMemoryAgentRegistry) -> None:
        arb = ConflictArbitrator(registry)
        c = arb.register_conflict("a", "b", "r1", "reason")
        arb.resolve_conflict(c.conflict_id, "done")
        assert len(arb.resolved_conflicts()) == 1

    def test_list_conflicts(self, registry: InMemoryAgentRegistry) -> None:
        arb = ConflictArbitrator(registry)
        arb.register_conflict("a", "b", "r1", "r")
        arb.register_conflict("c", "d", "r2", "r")
        assert len(arb.list_conflicts()) == 2

    def test_clear_expired_locks(self, registry: InMemoryAgentRegistry) -> None:
        arb = ConflictArbitrator(registry)
        arb.acquire_lock("r1", "agent-001", ttl_seconds=0.0)
        import time
        time.sleep(0.01)
        cleared = arb.clear_expired_locks()
        assert cleared >= 1

    def test_lock_expiry(self, registry: InMemoryAgentRegistry) -> None:
        lock = ResourceLock(resource_id="r1", holder_id="a1", ttl_seconds=0.0)
        import time
        time.sleep(0.01)
        assert lock.is_expired()

    def test_lock_not_expired(self, registry: InMemoryAgentRegistry) -> None:
        lock = ResourceLock(resource_id="r1", holder_id="a1", ttl_seconds=3600)
        assert not lock.is_expired()

    def test_lock_no_ttl(self, registry: InMemoryAgentRegistry) -> None:
        lock = ResourceLock(resource_id="r1", holder_id="a1")
        assert not lock.is_expired()

    def test_duplicate_conflict(self, registry: InMemoryAgentRegistry) -> None:
        arb = ConflictArbitrator(registry)
        c1 = arb.register_conflict("a", "b", "r1", "reason")
        c2 = arb.register_conflict("a", "b", "r1", "reason")
        assert c1.conflict_id == c2.conflict_id

    def test_resolve_nonexistent_conflict(self, registry: InMemoryAgentRegistry) -> None:
        arb = ConflictArbitrator(registry)
        assert not arb.resolve_conflict("nonexistent", "done")


# ---------------------------------------------------------------------------
# MetricsCollector
# ---------------------------------------------------------------------------


class TestMetricsCollector:
    def test_record(self) -> None:
        m = MetricsCollector()
        rec = m.record("agent-001", "test_metric", 42.0)
        assert rec.agent_id == "agent-001"
        assert rec.metric_name == "test_metric"
        assert rec.value == 42.0

    def test_record_task_duration(self) -> None:
        m = MetricsCollector()
        rec = m.record_task_duration("agent-001", 1.5)
        assert rec.metric_name == "task_duration"
        assert rec.value == 1.5

    def test_record_task_success(self) -> None:
        m = MetricsCollector()
        rec = m.record_task_success("agent-001")
        assert rec.value == 1.0

    def test_record_task_failure(self) -> None:
        m = MetricsCollector()
        rec = m.record_task_failure("agent-001")
        assert rec.value == 1.0

    def test_record_message_sent(self) -> None:
        m = MetricsCollector()
        rec = m.record_message_sent("agent-001")
        assert rec.value == 1.0

    def test_record_message_received(self) -> None:
        m = MetricsCollector()
        rec = m.record_message_received("agent-001")
        assert rec.value == 1.0

    def test_average(self) -> None:
        m = MetricsCollector()
        m.record("agent-001", "latency", 10.0)
        m.record("agent-001", "latency", 20.0)
        assert m.average("agent-001", "latency") == 15.0

    def test_average_no_data(self) -> None:
        m = MetricsCollector()
        assert m.average("agent-001", "nonexistent") is None

    def test_count(self) -> None:
        m = MetricsCollector()
        m.record("agent-001", "m1", 1.0)
        m.record("agent-001", "m1", 2.0)
        assert m.count("agent-001", "m1") == 2

    def test_latest(self) -> None:
        m = MetricsCollector()
        m.record("agent-001", "m1", 1.0)
        m.record("agent-001", "m1", 2.0)
        latest = m.latest("agent-001", "m1")
        assert latest is not None
        assert latest.value == 2.0

    def test_query_by_agent(self) -> None:
        m = MetricsCollector()
        m.record("agent-a", "m1", 1.0)
        m.record("agent-b", "m2", 2.0)
        assert len(m.query(agent_id="agent-a")) == 1

    def test_query_by_metric(self) -> None:
        m = MetricsCollector()
        m.record("agent-a", "m1", 1.0)
        m.record("agent-b", "m1", 2.0)
        assert len(m.query(metric_name="m1")) == 2

    def test_summary(self) -> None:
        m = MetricsCollector()
        m.record("agent-001", "latency", 10.0)
        m.record("agent-001", "latency", 20.0)
        summary = m.summary("agent-001")
        assert "latency" in summary

    def test_agent_summaries(self) -> None:
        m = MetricsCollector()
        m.record("agent-a", "m1", 1.0)
        m.record("agent-b", "m1", 2.0)
        summaries = m.agent_summaries()
        assert "agent-a" in summaries
        assert "agent-b" in summaries

    def test_clear(self) -> None:
        m = MetricsCollector()
        m.record("agent-001", "m1", 1.0)
        m.clear()
        assert m.count("agent-001", "m1") == 0


# ---------------------------------------------------------------------------
# EventSystem
# ---------------------------------------------------------------------------


class TestEventSystem:
    def test_on_and_emit(self) -> None:
        es = EventSystem()
        received: list[TypedEvent] = []

        def handler(event: TypedEvent) -> None:
            received.append(event)

        es.on("test_event", handler)
        es.emit("test_event", '{"key": "value"}', "agent-001")
        assert len(received) == 1
        assert received[0].event_type == "test_event"

    def test_on_any(self) -> None:
        es = EventSystem()
        received: list[TypedEvent] = []

        def handler(event: TypedEvent) -> None:
            received.append(event)

        es.on_any(handler)
        es.emit("type_a", "payload_a", "src")
        es.emit("type_b", "payload_b", "src")
        assert len(received) == 2

    def test_off(self) -> None:
        es = EventSystem()
        received: list[TypedEvent] = []

        def handler(event: TypedEvent) -> None:
            received.append(event)

        es.on("test_event", handler)
        es.off("test_event", handler)
        es.emit("test_event", "payload", "src")
        assert len(received) == 0

    def test_history(self) -> None:
        es = EventSystem()
        es.emit("type_a", "pa", "src")
        es.emit("type_b", "pb", "src")
        hist = es.history()
        assert len(hist) == 2

    def test_history_filter_by_type(self) -> None:
        es = EventSystem()
        es.emit("type_a", "pa", "src")
        es.emit("type_b", "pb", "src")
        hist = es.history(event_type="type_a")
        assert len(hist) == 1

    def test_history_filter_by_source(self) -> None:
        es = EventSystem()
        es.emit("t", "p", "src-a")
        es.emit("t", "p", "src-b")
        hist = es.history(source="src-a")
        assert len(hist) == 1

    def test_count(self) -> None:
        es = EventSystem()
        es.emit("a", "p", "src")
        es.emit("a", "p", "src")
        es.emit("b", "p", "src")
        assert es.count() == 3
        assert es.count("a") == 2

    def test_clear(self) -> None:
        es = EventSystem()
        es.emit("a", "p", "src")
        es.clear()
        assert es.count() == 0

    def test_handler_count(self) -> None:
        es = EventSystem()

        def h1(event): pass
        def h2(event): pass

        es.on("a", h1)
        es.on("b", h2)
        es.on_any(h1)
        assert es.handler_count() == 3

    def test_emit_from_model(self) -> None:
        es = EventSystem()
        from jarvis_agents.models import AgentEvent
        agent_event = AgentEvent(event_id="e1", source_agent_id="src", event_type="test", payload="p")
        typed = es.emit_from_model(agent_event)
        assert typed.event_type == "test"
        assert typed.source == "src"


# ---------------------------------------------------------------------------
# AgentManager
# ---------------------------------------------------------------------------


class TestAgentManager:
    def test_register_and_list(self) -> None:
        mgr = AgentManager()
        defn = AgentDefinition(
            role="test", description="test",
            capabilities=(AgentCapability(name="c1", description="d1"),),
            permissions=(),
        )
        agent = mgr.register_agent(defn, agent_id="a1", owner="o", workspace="w")
        assert agent.identifier == "a1"
        agents = mgr.list_agents()
        assert len(agents) == 1

    def test_activate_agent(self) -> None:
        mgr = AgentManager()
        defn = AgentDefinition(role="test", description="test", capabilities=(), permissions=())
        mgr.register_agent(defn, agent_id="a1", owner="o", workspace="w")
        activated = mgr.activate_agent("a1")
        assert activated.status == AgentStatus.READY

    def test_find_by_capability(self) -> None:
        mgr = AgentManager()
        cap = AgentCapability(name="research", description="research")
        defn = AgentDefinition(role="test", description="test", capabilities=(cap,), permissions=())
        mgr.register_agent(defn, agent_id="a1", owner="o", workspace="w")
        mgr.activate_agent("a1")
        mgr.discovery.build_index()
        results = mgr.find_agents_by_capability("research")
        assert len(results) >= 1

    def test_create_context(self) -> None:
        mgr = AgentManager()
        cid = mgr.create_context()
        assert cid.startswith("ctx-")

    def test_health_summary(self) -> None:
        mgr = AgentManager()
        summary = mgr.health_summary()
        assert "total" in summary

    def test_system_status(self) -> None:
        mgr = AgentManager()
        status = mgr.get_system_status()
        assert "total_agents" in status
        assert "ready_agents" in status

    def test_execute_task(self) -> None:
        mgr = AgentManager()
        task = AgentTask(task_id="t1", description="test", assigned_agent_id="agent-001")
        result = mgr.execute_task(task)
        assert result.success

    def test_recover_agent(self) -> None:
        mgr = AgentManager()
        defn = AgentDefinition(role="test", description="test", capabilities=(), permissions=())
        mgr.register_agent(defn, agent_id="a1", owner="o", workspace="w")
        mgr.activate_agent("a1")
        mgr.supervisor._restart_counts["a1"] = 0
        recovered = mgr.recover_agent("a1")
        assert recovered is not None


class TestBaseAgent:
    def test_attributes(self) -> None:
        agent = BaseAgent(name="Test", description="Test agent", capabilities=(), permissions=())
        assert agent.name == "Test"
        assert agent.description == "Test agent"
        assert agent.status.value == "created"
        assert agent.capabilities == ()
        assert agent.permissions == ()
        assert agent.agent_id.startswith("agent-")

    def test_lifecycle(self) -> None:
        agent = BaseAgent(name="Test", description="Test", capabilities=(), permissions=())
        agent.initialize()
        assert agent.status.value == "initializing"
        agent.start()
        assert agent.status.value == "ready"
        agent.pause()
        assert agent.status.value == "paused"
        agent.resume()
        assert agent.status.value == "ready"
        agent.stop()
        assert agent.status.value == "retired"

    def test_send_and_receive_messages(self) -> None:
        agent = BaseAgent(name="Test", description="Test", capabilities=(), permissions=())
        corr_id = agent.send_message("target-1", "greeting", "hello")
        assert corr_id.startswith("corr-")
        msgs = agent.receive_messages()
        assert len(msgs) == 1
        assert msgs[0].target_agent_id == "target-1"
        assert msgs[0].message_type == "greeting"
        assert msgs[0].payload == "hello"
        assert agent.receive_messages() == ()

    def test_send_and_receive_responses(self) -> None:
        agent = BaseAgent(name="Test", description="Test", capabilities=(), permissions=())
        agent.send_response("corr-1", "target-1", "done", success=True)
        resps = agent.receive_responses()
        assert len(resps) == 1
        assert resps[0].correlation_id == "corr-1"
        assert resps[0].success is True
        assert agent.receive_responses() == ()

    def test_handle_task_default_raises(self) -> None:
        agent = BaseAgent(name="Test", description="Test", capabilities=(), permissions=())
        with pytest.raises(NotImplementedError):
            agent.handle_task(AgentTask(
                task_id="t1", description="test",
                assigned_agent_id=agent.agent_id,
            ))

    def test_metadata_auto_generated(self) -> None:
        agent = BaseAgent(name="TestAgent", description="desc", capabilities=(), permissions=())
        assert agent.metadata.name == "TestAgent"
        assert agent.metadata.identifier == agent.agent_id


class TestPlannerAgent:
    def test_capabilities_and_permissions(self) -> None:
        agent = PlannerAgent()
        caps = {c.name for c in agent.capabilities}
        assert "planning" in caps
        assert "analysis" in caps
        assert "reasoning" in caps
        assert "reporting" in caps

    def test_handle_plan_task(self) -> None:
        agent = PlannerAgent()
        task = AgentTask(task_id="t1", description="Create a plan for project", assigned_agent_id=agent.agent_id)
        result = agent.handle_task(task)
        assert result.success is True
        assert "plan" in result.output.lower()

    def test_handle_progress_task(self) -> None:
        agent = PlannerAgent()
        task = AgentTask(task_id="t2", description="Track progress on sprint", assigned_agent_id=agent.agent_id)
        result = agent.handle_task(task)
        assert result.success is True

    def test_handle_generic_task(self) -> None:
        agent = PlannerAgent()
        task = AgentTask(task_id="t3", description="Analyze something", assigned_agent_id=agent.agent_id)
        result = agent.handle_task(task)
        assert result.success is True


class TestCodingAgent:
    def test_capabilities(self) -> None:
        agent = CodingAgent()
        caps = {c.name for c in agent.capabilities}
        assert "programming" in caps
        assert "code_review" in caps
        assert "debugging" in caps
        assert "testing" in caps

    def test_handle_review(self) -> None:
        agent = CodingAgent()
        task = AgentTask(task_id="t1", description="Code review PR #42", assigned_agent_id=agent.agent_id)
        result = agent.handle_task(task)
        assert result.success is True
        assert "review" in result.output.lower()

    def test_handle_debug(self) -> None:
        agent = CodingAgent()
        task = AgentTask(task_id="t2", description="Fix login bug", assigned_agent_id=agent.agent_id)
        result = agent.handle_task(task)
        assert result.success is True
        assert "fix" in result.output.lower() or "debug" in result.output.lower()

    def test_handle_test(self) -> None:
        agent = CodingAgent()
        task = AgentTask(task_id="t3", description="Write tests for module", assigned_agent_id=agent.agent_id)
        result = agent.handle_task(task)
        assert result.success is True
        assert "test" in result.output.lower()


class TestResearchAgent:
    def test_capabilities(self) -> None:
        agent = ResearchAgent()
        caps = {c.name for c in agent.capabilities}
        assert "research" in caps
        assert "summarization" in caps
        assert "analysis" in caps

    def test_handle_research(self) -> None:
        agent = ResearchAgent()
        task = AgentTask(task_id="t1", description="Investigate quantum computing trends", assigned_agent_id=agent.agent_id)
        result = agent.handle_task(task)
        assert result.success is True
        assert "research" in result.output.lower() or "investigate" in result.output.lower()

    def test_handle_summarize(self) -> None:
        agent = ResearchAgent()
        task = AgentTask(task_id="t2", description="Summarize the report", assigned_agent_id=agent.agent_id)
        result = agent.handle_task(task)
        assert result.success is True
        assert "summary" in result.output.lower()


class TestMemoryAgent:
    def test_capabilities(self) -> None:
        agent = MemoryAgent()
        caps = {c.name for c in agent.capabilities}
        assert "memory_management" in caps
        assert "knowledge_retrieval" in caps
        assert "context_management" in caps

    def test_handle_store(self) -> None:
        agent = MemoryAgent()
        task = AgentTask(task_id="t1", description="Store user preferences", assigned_agent_id=agent.agent_id)
        result = agent.handle_task(task)
        assert result.success is True
        assert "store" in result.output.lower()

    def test_handle_retrieve(self) -> None:
        agent = MemoryAgent()
        task = AgentTask(task_id="t2", description="Find previous conversation", assigned_agent_id=agent.agent_id)
        result = agent.handle_task(task)
        assert result.success is True
        assert "retriev" in result.output.lower() or "find" in result.output.lower()

    def test_handle_index(self) -> None:
        agent = MemoryAgent()
        task = AgentTask(task_id="t3", description="Index knowledge base", assigned_agent_id=agent.agent_id)
        result = agent.handle_task(task)
        assert result.success is True


class TestAutomationAgent:
    def test_capabilities(self) -> None:
        agent = AutomationAgent()
        caps = {c.name for c in agent.capabilities}
        assert "automation" in caps
        assert "monitoring" in caps

    def test_handle_workflow(self) -> None:
        agent = AutomationAgent()
        task = AgentTask(task_id="t1", description="Automate deployment pipeline", assigned_agent_id=agent.agent_id)
        result = agent.handle_task(task)
        assert result.success is True
        assert "workflow" in result.output.lower() or "pipeline" in result.output.lower()

    def test_handle_monitor(self) -> None:
        agent = AutomationAgent()
        task = AgentTask(task_id="t2", description="Watch server logs", assigned_agent_id=agent.agent_id)
        result = agent.handle_task(task)
        assert result.success is True

    def test_handle_schedule(self) -> None:
        agent = AutomationAgent()
        task = AgentTask(task_id="t3", description="Schedule nightly backup", assigned_agent_id=agent.agent_id)
        result = agent.handle_task(task)
        assert result.success is True
        assert "schedule" in result.output.lower()


class TestDesktopAgent:
    def test_capabilities(self) -> None:
        agent = DesktopAgent()
        caps = {c.name for c in agent.capabilities}
        assert "file_management" in caps
        assert "process_management" in caps
        assert "system_monitoring" in caps

    def test_handle_file(self) -> None:
        agent = DesktopAgent()
        task = AgentTask(task_id="t1", description="Create file structure", assigned_agent_id=agent.agent_id)
        result = agent.handle_task(task)
        assert result.success is True
        assert "file" in result.output.lower()

    def test_handle_process(self) -> None:
        agent = DesktopAgent()
        task = AgentTask(task_id="t2", description="Run build script", assigned_agent_id=agent.agent_id)
        result = agent.handle_task(task)
        assert result.success is True

    def test_handle_system_monitor(self) -> None:
        agent = DesktopAgent()
        task = AgentTask(task_id="t3", description="Monitor system resources", assigned_agent_id=agent.agent_id)
        result = agent.handle_task(task)
        assert result.success is True


class TestWebIntelligenceAgent:
    def test_capabilities(self) -> None:
        agent = WebIntelligenceAgent()
        caps = {c.name for c in agent.capabilities}
        assert "web_scraping" in caps
        assert "web_monitoring" in caps
        assert "content_extraction" in caps

    def test_handle_scrape(self) -> None:
        agent = WebIntelligenceAgent()
        task = AgentTask(task_id="t1", description="Scrape product prices", assigned_agent_id=agent.agent_id)
        result = agent.handle_task(task)
        assert result.success is True
        assert "scrap" in result.output.lower()

    def test_handle_monitor(self) -> None:
        agent = WebIntelligenceAgent()
        task = AgentTask(task_id="t2", description="Track stock changes", assigned_agent_id=agent.agent_id)
        result = agent.handle_task(task)
        assert result.success is True

    def test_handle_extract(self) -> None:
        agent = WebIntelligenceAgent()
        task = AgentTask(task_id="t3", description="Extract article data", assigned_agent_id=agent.agent_id)
        result = agent.handle_task(task)
        assert result.success is True
        assert "extract" in result.output.lower()


class TestVisionAgent:
    def test_capabilities(self) -> None:
        agent = VisionAgent()
        caps = {c.name for c in agent.capabilities}
        assert "vision" in caps
        assert "analysis" in caps

    def test_handle_image(self) -> None:
        agent = VisionAgent()
        task = AgentTask(task_id="t1", description="Analyze product photo", assigned_agent_id=agent.agent_id)
        result = agent.handle_task(task)
        assert result.success is True
        assert "image" in result.output.lower() or "photo" in result.output.lower()

    def test_handle_diagram(self) -> None:
        agent = VisionAgent()
        task = AgentTask(task_id="t2", description="Read architecture diagram", assigned_agent_id=agent.agent_id)
        result = agent.handle_task(task)
        assert result.success is True
        assert "diagram" in result.output.lower()


class TestVoiceAgent:
    def test_capabilities(self) -> None:
        agent = VoiceAgent()
        caps = {c.name for c in agent.capabilities}
        assert "voice" in caps
        assert "translation" in caps
        assert "communication" in caps

    def test_handle_transcribe(self) -> None:
        agent = VoiceAgent()
        task = AgentTask(task_id="t1", description="Transcribe meeting recording", assigned_agent_id=agent.agent_id)
        result = agent.handle_task(task)
        assert result.success is True
        assert "transcrib" in result.output.lower() or "speech" in result.output.lower()

    def test_handle_translate(self) -> None:
        agent = VoiceAgent()
        task = AgentTask(task_id="t2", description="Translate audio to French", assigned_agent_id=agent.agent_id)
        result = agent.handle_task(task)
        assert result.success is True
        assert "translat" in result.output.lower()

    def test_handle_audio(self) -> None:
        agent = VoiceAgent()
        task = AgentTask(task_id="t3", description="Process audio file", assigned_agent_id=agent.agent_id)
        result = agent.handle_task(task)
        assert result.success is True
        assert "audio" in result.output.lower()


class TestCommunicationAgent:
    def test_capabilities(self) -> None:
        agent = CommunicationAgent()
        caps = {c.name for c in agent.capabilities}
        assert "communication" in caps
        assert "message_routing" in caps
        assert "event_broker" in caps
        assert "coordination" in caps

    def test_handle_route(self) -> None:
        agent = CommunicationAgent()
        task = AgentTask(task_id="t1", description="Route message to agent", assigned_agent_id=agent.agent_id)
        result = agent.handle_task(task)
        assert result.success is True
        assert "route" in result.output.lower()

    def test_handle_broadcast(self) -> None:
        agent = CommunicationAgent()
        task = AgentTask(task_id="t2", description="Broadcast system alert", assigned_agent_id=agent.agent_id)
        result = agent.handle_task(task)
        assert result.success is True
        assert "broadcast" in result.output.lower()

    def test_handle_coordinate(self) -> None:
        agent = CommunicationAgent()
        task = AgentTask(task_id="t3", description="Coordinate multi-agent task", assigned_agent_id=agent.agent_id)
        result = agent.handle_task(task)
        assert result.success is True
        assert "coordinat" in result.output.lower() or "orchestrat" in result.output.lower()
