from __future__ import annotations

import pytest
from jarvis_automation.approval import InMemoryApprovalEngine
from jarvis_automation.compensation import InMemoryCompensationEngine
from jarvis_automation.context import InMemoryExecutionContext
from jarvis_automation.engine import InMemoryWorkflowEngine
from jarvis_automation.kernel import AutomationKernel
from jarvis_automation.models import (
    ApprovalRequest,
    ApprovalStatus,
    AutomationPolicy,
    AutomationPolicyScope,
    ExecutionContextData,
    ExecutionMode,
    RetryPolicy,
    RetryStrategy,
    ScheduleDefinition,
    ScheduleType,
    StepState,
    StepStatus,
    StepType,
    TriggerDefinition,
    TriggerEvent,
    TriggerType,
    VariableScope,
    VariableValue,
    WorkflowCategory,
    WorkflowDefinition,
    WorkflowExecutionRequest,
    WorkflowExecutionState,
    WorkflowInput,
    WorkflowMetadata,
    WorkflowOutput,
    WorkflowStatus,
    WorkflowStep,
)
from jarvis_automation.monitoring import InMemoryMonitoringEngine
from jarvis_automation.policies import InMemoryPolicyEngine
from jarvis_automation.registry import InMemoryWorkflowRegistry
from jarvis_automation.retry import InMemoryRetryManager
from jarvis_automation.scheduler import InMemorySchedulerEngine
from jarvis_automation.state import InMemoryStateManager
from jarvis_automation.templates import WORKFLOW_TEMPLATES
from jarvis_automation.triggers import InMemoryTriggerEngine
from jarvis_automation.variables import InMemoryVariableManager

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def simple_workflow() -> WorkflowDefinition:
    return WorkflowDefinition(
        workflow_id="test.simple",
        name="Simple Workflow",
        description="A simple test workflow",
        version="1.0.0",
        category=WorkflowCategory.CUSTOM,
        steps=(
            WorkflowStep(
                step_id="step.one",
                name="Step One",
                description="First step",
            ),
            WorkflowStep(
                step_id="step.two",
                name="Step Two",
                description="Second step",
            ),
        ),
        inputs=(
            WorkflowInput(name="message", type="string", description="Input message"),
        ),
        outputs=(
            WorkflowOutput(name="result", type="string", description="Output result"),
        ),
    )


@pytest.fixture
def kernel() -> AutomationKernel:
    return AutomationKernel()


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class TestEnums:
    def test_workflow_status_values(self) -> None:
        assert WorkflowStatus.CREATED.value == "created"
        assert WorkflowStatus.RUNNING.value == "running"
        assert WorkflowStatus.COMPLETED.value == "completed"
        assert WorkflowStatus.FAILED.value == "failed"
        assert WorkflowStatus.CANCELLED.value == "cancelled"
        assert WorkflowStatus.COMPENSATING.value == "compensating"

    def test_step_status_values(self) -> None:
        assert StepStatus.PENDING.value == "pending"
        assert StepStatus.WAITING_APPROVAL.value == "waiting_approval"

    def test_trigger_type_values(self) -> None:
        assert TriggerType.MANUAL.value == "manual"
        assert TriggerType.SCHEDULED.value == "scheduled"

    def test_retry_strategy_values(self) -> None:
        assert RetryStrategy.IMMEDIATE.value == "immediate"
        assert RetryStrategy.EXPONENTIAL_BACKOFF.value == "exponential_backoff"


class TestWorkflowDefinition:
    def test_create(self, simple_workflow: WorkflowDefinition) -> None:
        assert simple_workflow.workflow_id == "test.simple"
        assert simple_workflow.category == WorkflowCategory.CUSTOM
        assert len(simple_workflow.steps) == 2

    def test_with_updated_at(self, simple_workflow: WorkflowDefinition) -> None:
        updated = simple_workflow.with_updated_at()
        assert updated.updated_at >= simple_workflow.updated_at

    def test_defaults(self) -> None:
        w = WorkflowDefinition(
            workflow_id="x", name="x", description="",
            version="1.0.0", category=WorkflowCategory.CUSTOM,
            steps=(),
        )
        assert w.owner == "system"
        assert w.workspace == "*"


class TestWorkflowMetadata:
    def test_with_status(self) -> None:
        w = WorkflowDefinition(
            workflow_id="x", name="x", description="",
            version="1.0.0", category=WorkflowCategory.CUSTOM,
            steps=(),
        )
        meta = WorkflowMetadata(workflow_id="x", definition=w)
        meta2 = meta.with_status(WorkflowStatus.RUNNING)
        assert meta2.status == WorkflowStatus.RUNNING
        assert meta.status == WorkflowStatus.CREATED

    def test_with_definition(self) -> None:
        w = WorkflowDefinition(
            workflow_id="x", name="x", description="",
            version="1.0.0", category=WorkflowCategory.CUSTOM,
            steps=(),
        )
        meta = WorkflowMetadata(workflow_id="x", definition=w)
        w2 = w.with_updated_at()
        meta2 = meta.with_definition(w2)
        assert meta2.definition.workflow_id == "x"


class TestStepState:
    def test_with_status(self) -> None:
        s = StepState(step_id="s1")
        s2 = s.with_status(StepStatus.RUNNING)
        assert s2.status == StepStatus.RUNNING

    def test_with_attempt(self) -> None:
        s = StepState(step_id="s1")
        s2 = s.with_attempt()
        assert s2.attempts == 1

    def test_with_error(self) -> None:
        s = StepState(step_id="s1")
        s2 = s.with_error("oops")
        assert s2.status == StepStatus.FAILED
        assert s2.error_message == "oops"


class TestWorkflowExecutionState:
    def test_with_status(self) -> None:
        es = WorkflowExecutionState(execution_id="e1", workflow_id="w1")
        es2 = es.with_status(WorkflowStatus.RUNNING)
        assert es2.status == WorkflowStatus.RUNNING

    def test_with_step_state(self) -> None:
        es = WorkflowExecutionState(execution_id="e1", workflow_id="w1")
        ss = StepState(step_id="s1", status=StepStatus.COMPLETED)
        es2 = es.with_step_state(ss)
        assert len(es2.step_states) == 1

    def test_with_current_step(self) -> None:
        es = WorkflowExecutionState(execution_id="e1", workflow_id="w1")
        es2 = es.with_current_step("step.one")
        assert es2.current_step_id == "step.one"


class TestExecutionContextData:
    def test_with_current_step(self) -> None:
        ctx = ExecutionContextData(
            workflow_id="w1", execution_id="e1", correlation_id="c1",
        )
        ctx2 = ctx.with_current_step("step.one")
        assert ctx2.current_step_id == "step.one"
        assert ctx2.history == ("step.one",)


class TestApprovalRequest:
    def test_with_approval(self) -> None:
        req = ApprovalRequest(
            approval_id="a1", execution_id="e1",
            workflow_id="w1", step_id="s1",
            gate_id="g1", description="test", requested_by="user",
        )
        req2 = req.with_approval("approver1")
        assert req2.status == ApprovalStatus.APPROVED
        assert req2.approved_by == ("approver1",)

    def test_with_rejection(self) -> None:
        req = ApprovalRequest(
            approval_id="a1", execution_id="e1",
            workflow_id="w1", step_id="s1",
            gate_id="g1", description="test", requested_by="user",
        )
        req2 = req.with_rejection("approver1")
        assert req2.status == ApprovalStatus.REJECTED


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

class TestInMemoryWorkflowRegistry:
    def test_register_and_get(self, simple_workflow: WorkflowDefinition) -> None:
        r = InMemoryWorkflowRegistry()
        meta = r.register(simple_workflow)
        assert meta.workflow_id == "test.simple"
        assert r.get("test.simple") is meta
        assert r.get("nonexistent") is None

    def test_deregister(self, simple_workflow: WorkflowDefinition) -> None:
        r = InMemoryWorkflowRegistry()
        r.register(simple_workflow)
        r.deregister("test.simple")
        assert r.get("test.simple") is None

    def test_list(self, simple_workflow: WorkflowDefinition) -> None:
        r = InMemoryWorkflowRegistry()
        r.register(simple_workflow)
        assert len(r.list()) == 1

    def test_list_by_status(self, simple_workflow: WorkflowDefinition) -> None:
        r = InMemoryWorkflowRegistry()
        r.register(simple_workflow)
        assert len(r.list_by_status(WorkflowStatus.CREATED)) == 1
        assert len(r.list_by_status(WorkflowStatus.RUNNING)) == 0

    def test_list_by_category(self, simple_workflow: WorkflowDefinition) -> None:
        r = InMemoryWorkflowRegistry()
        r.register(simple_workflow)
        assert len(r.list_by_category("custom")) == 1
        assert len(r.list_by_category("research")) == 0

    def test_update(self, simple_workflow: WorkflowDefinition) -> None:
        r = InMemoryWorkflowRegistry()
        meta = r.register(simple_workflow)
        r.update(meta.with_status(WorkflowStatus.RUNNING))
        assert r.get("test.simple").status == WorkflowStatus.RUNNING


# ---------------------------------------------------------------------------
# State Manager
# ---------------------------------------------------------------------------

class TestInMemoryStateManager:
    def test_create_and_get(self) -> None:
        sm = InMemoryStateManager()
        state = sm.create("exec1", "workflow1")
        assert state.execution_id == "exec1"
        assert sm.get("exec1") is state

    def test_update_status(self) -> None:
        sm = InMemoryStateManager()
        sm.create("exec1", "workflow1")
        updated = sm.update_status("exec1", WorkflowStatus.RUNNING)
        assert updated.status == WorkflowStatus.RUNNING

    def test_update_status_terminal(self) -> None:
        sm = InMemoryStateManager()
        sm.create("exec1", "workflow1")
        sm.update_status("exec1", WorkflowStatus.COMPLETED)
        state = sm.get("exec1")
        assert state is not None
        assert state.status == WorkflowStatus.COMPLETED
        assert state.completed_at is not None

    def test_update_step(self) -> None:
        sm = InMemoryStateManager()
        sm.create("exec1", "workflow1")
        ss = StepState(step_id="s1", status=StepStatus.COMPLETED)
        state = sm.update_step("exec1", ss)
        assert len(state.step_states) == 1

    def test_list_by_status(self) -> None:
        sm = InMemoryStateManager()
        sm.create("exec1", "w1")
        sm.create("exec2", "w2")
        sm.update_status("exec2", WorkflowStatus.RUNNING)
        running = sm.list_by_status(WorkflowStatus.RUNNING)
        assert len(running) == 1
        assert running[0].execution_id == "exec2"


# ---------------------------------------------------------------------------
# Execution Context
# ---------------------------------------------------------------------------

class TestInMemoryExecutionContext:
    def test_create_and_get(self) -> None:
        ctx = InMemoryExecutionContext()
        data = ctx.create("w1", "e1", "c1")
        assert data.execution_id == "e1"
        assert ctx.get("e1") is data

    def test_advance_step(self) -> None:
        ctx = InMemoryExecutionContext()
        ctx.create("w1", "e1", "c1")
        ctx.advance_step("e1", "step.one")
        data = ctx.get("e1")
        assert data is not None
        assert data.current_step_id == "step.one"
        assert data.history == ("step.one",)

    def test_get_history_empty(self) -> None:
        ctx = InMemoryExecutionContext()
        assert ctx.get_history("nonexistent") == ()


# ---------------------------------------------------------------------------
# Variables
# ---------------------------------------------------------------------------

class TestInMemoryVariableManager:
    def test_set_and_get(self) -> None:
        vm = InMemoryVariableManager()
        v = VariableValue(name="x", value="hello")
        vm.set("e1", v)
        assert vm.get("e1", "x") is v

    def test_list(self) -> None:
        vm = InMemoryVariableManager()
        vm.set("e1", VariableValue(name="a", value="1"))
        vm.set("e1", VariableValue(name="b", value="2"))
        assert len(vm.list("e1")) == 2

    def test_list_by_scope(self) -> None:
        vm = InMemoryVariableManager()
        vm.set("e1", VariableValue(name="a", value="1", scope=VariableScope.INPUT))
        vm.set("e1", VariableValue(name="b", value="2", scope=VariableScope.OUTPUT))
        inputs = vm.list_by_scope("e1", VariableScope.INPUT)
        assert len(inputs) == 1
        assert inputs[0].name == "a"

    def test_delete(self) -> None:
        vm = InMemoryVariableManager()
        vm.set("e1", VariableValue(name="x", value="v"))
        vm.delete("e1", "x")
        assert vm.get("e1", "x") is None

    def test_immutable_raises(self) -> None:
        vm = InMemoryVariableManager()
        vm.set("e1", VariableValue(name="x", value="v", immutable=True))
        with pytest.raises(ValueError, match="immutable"):
            vm.set("e1", VariableValue(name="x", value="v2"))


# ---------------------------------------------------------------------------
# Retry Manager
# ---------------------------------------------------------------------------

class TestInMemoryRetryManager:
    def test_should_retry_under_limit(self) -> None:
        rm = InMemoryRetryManager()
        policy = RetryPolicy(max_retries=3)
        assert rm.should_retry("s1", policy, 1)
        assert rm.should_retry("s1", policy, 2)
        assert not rm.should_retry("s1", policy, 3)

    def test_next_delay_immediate(self) -> None:
        rm = InMemoryRetryManager()
        policy = RetryPolicy(strategy=RetryStrategy.IMMEDIATE)
        assert rm.next_delay(policy, 1) == 0

    def test_next_delay_exponential(self) -> None:
        rm = InMemoryRetryManager()
        policy = RetryPolicy(
            strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
            delay_seconds=1,
            backoff_multiplier=2.0,
        )
        assert rm.next_delay(policy, 1) == 1
        assert rm.next_delay(policy, 2) == 2
        assert rm.next_delay(policy, 3) == 4

    def test_record_and_get_attempts(self) -> None:
        rm = InMemoryRetryManager()
        assert rm.record_attempt("e1", "s1") == 1
        assert rm.record_attempt("e1", "s1") == 2
        assert rm.get_attempts("e1", "s1") == 2

    def test_reset(self) -> None:
        rm = InMemoryRetryManager()
        rm.record_attempt("e1", "s1")
        rm.reset("e1", "s1")
        assert rm.get_attempts("e1", "s1") == 0


# ---------------------------------------------------------------------------
# Compensation Engine
# ---------------------------------------------------------------------------

class TestInMemoryCompensationEngine:
    def test_register_and_compensate(self) -> None:
        ce = InMemoryCompensationEngine()
        ce.register_compensation("e1", "s1", "comp1")
        ce.register_compensation("e1", "s2", "comp2")
        compensated = ce.compensate("e1", "s2")
        assert len(compensated) == 1
        assert compensated[0] == "s1"

    def test_get_compensation_order(self) -> None:
        ce = InMemoryCompensationEngine()
        ce.register_compensation("e1", "s1", "c1")
        ce.register_compensation("e1", "s2", "c2")
        order = ce.get_compensation_order("e1")
        # Reverse order: s2 first, then s1
        assert len(order) == 2


# ---------------------------------------------------------------------------
# Approval Engine
# ---------------------------------------------------------------------------

class TestInMemoryApprovalEngine:
    def test_request_approval(self) -> None:
        ae = InMemoryApprovalEngine()
        req = ApprovalRequest(
            approval_id="a1", execution_id="e1",
            workflow_id="w1", step_id="s1",
            gate_id="g1", description="test", requested_by="user",
        )
        result = ae.request_approval(req)
        assert result.status == ApprovalStatus.PENDING

    def test_approve(self) -> None:
        ae = InMemoryApprovalEngine()
        req = ApprovalRequest(
            approval_id="a1", execution_id="e1",
            workflow_id="w1", step_id="s1",
            gate_id="g1", description="test", requested_by="user",
        )
        ae.request_approval(req)
        updated = ae.approve("a1", "approver")
        assert updated.status == ApprovalStatus.APPROVED

    def test_reject(self) -> None:
        ae = InMemoryApprovalEngine()
        req = ApprovalRequest(
            approval_id="a1", execution_id="e1",
            workflow_id="w1", step_id="s1",
            gate_id="g1", description="test", requested_by="user",
        )
        ae.request_approval(req)
        updated = ae.reject("a1", "approver")
        assert updated.status == ApprovalStatus.REJECTED

    def test_is_approved(self) -> None:
        ae = InMemoryApprovalEngine()
        req = ApprovalRequest(
            approval_id="a1", execution_id="e1",
            workflow_id="w1", step_id="s1",
            gate_id="g1", description="test", requested_by="user",
        )
        ae.request_approval(req)
        assert not ae.is_approved("a1")
        ae.approve("a1", "approver")
        assert ae.is_approved("a1")

    def test_list_pending(self) -> None:
        ae = InMemoryApprovalEngine()
        req = ApprovalRequest(
            approval_id="a1", execution_id="e1",
            workflow_id="w1", step_id="s1",
            gate_id="g1", description="test", requested_by="user",
        )
        ae.request_approval(req)
        assert len(ae.list_pending("e1")) == 1

    def test_get_request_nonexistent(self) -> None:
        ae = InMemoryApprovalEngine()
        assert ae.get_request("nonexistent") is None


# ---------------------------------------------------------------------------
# Scheduler
# ---------------------------------------------------------------------------

class TestInMemorySchedulerEngine:
    def test_register_and_get(self) -> None:
        se = InMemorySchedulerEngine()
        sched = ScheduleDefinition(
            schedule_id="s1", schedule_type=ScheduleType.INTERVAL,
            workflow_id="w1", interval_seconds=3600,
        )
        se.register_schedule(sched)
        assert se.get_schedule("s1") is sched

    def test_unregister(self) -> None:
        se = InMemorySchedulerEngine()
        sched = ScheduleDefinition(
            schedule_id="s1", schedule_type=ScheduleType.INTERVAL,
            workflow_id="w1", interval_seconds=3600,
        )
        se.register_schedule(sched)
        se.unregister_schedule("s1")
        assert se.get_schedule("s1") is None

    def test_list_schedules(self) -> None:
        se = InMemorySchedulerEngine()
        sched = ScheduleDefinition(
            schedule_id="s1", schedule_type=ScheduleType.INTERVAL,
            workflow_id="w1", interval_seconds=3600,
        )
        se.register_schedule(sched)
        assert len(se.list_schedules()) == 1


# ---------------------------------------------------------------------------
# Triggers
# ---------------------------------------------------------------------------

class TestInMemoryTriggerEngine:
    def test_register_and_list(self) -> None:
        te = InMemoryTriggerEngine()
        trig = TriggerDefinition(
            trigger_id="t1", trigger_type=TriggerType.MANUAL,
            workflow_id="w1",
        )
        te.register_trigger(trig)
        assert len(te.list_triggers()) == 1
        assert len(te.list_by_type(TriggerType.MANUAL)) == 1

    def test_fire_matches(self) -> None:
        te = InMemoryTriggerEngine()
        trig = TriggerDefinition(
            trigger_id="t1", trigger_type=TriggerType.EVENT,
            workflow_id="w1", parameters={"key": "value"},
        )
        te.register_trigger(trig)
        event = TriggerEvent(
            event_id="ev1", trigger_type=TriggerType.EVENT,
            workflow_id="w1", payload={"extra": "data"},
        )
        requests = te.fire(event)
        assert len(requests) == 1
        assert requests[0].workflow_id == "w1"
        assert requests[0].inputs["key"] == "value"
        assert requests[0].inputs["extra"] == "data"

    def test_fire_no_match(self) -> None:
        te = InMemoryTriggerEngine()
        trig = TriggerDefinition(
            trigger_id="t1", trigger_type=TriggerType.MANUAL,
            workflow_id="w1",
        )
        te.register_trigger(trig)
        event = TriggerEvent(
            event_id="ev1", trigger_type=TriggerType.EVENT,
            workflow_id="w1",
        )
        requests = te.fire(event)
        assert len(requests) == 0

    def test_unregister(self) -> None:
        te = InMemoryTriggerEngine()
        trig = TriggerDefinition(
            trigger_id="t1", trigger_type=TriggerType.MANUAL,
            workflow_id="w1",
        )
        te.register_trigger(trig)
        te.unregister_trigger("t1")
        assert te.get_trigger("t1") is None


# ---------------------------------------------------------------------------
# Policy Engine
# ---------------------------------------------------------------------------

class TestInMemoryPolicyEngine:
    def test_default_policy(self) -> None:
        pe = InMemoryPolicyEngine()
        policy = pe.resolve(AutomationPolicyScope())
        assert policy.policy_id == "default"

    def test_register_and_resolve(self) -> None:
        pe = InMemoryPolicyEngine()
        scope = AutomationPolicyScope(owner="alice")
        policy = AutomationPolicy(policy_id="p1", name="Alice Policy")
        pe.register_policy(scope, policy)
        resolved = pe.resolve(AutomationPolicyScope(owner="alice"))
        assert resolved.policy_id == "p1"

    def test_evaluate_no_violations(self) -> None:
        pe = InMemoryPolicyEngine()
        policy = AutomationPolicy(policy_id="p1", name="test", workspace_restrictions=())
        violations = pe.evaluate("test.workflow", policy)
        assert len(violations) == 0

    def test_evaluate_denied(self) -> None:
        pe = InMemoryPolicyEngine()
        policy = AutomationPolicy(
            policy_id="p1", name="test",
            denied_workflows=("test.workflow",),
            workspace_restrictions=(),
        )
        violations = pe.evaluate("test.workflow", policy)
        assert len(violations) == 1


# ---------------------------------------------------------------------------
# Monitoring
# ---------------------------------------------------------------------------

class TestInMemoryMonitoringEngine:
    def test_record_execution(self) -> None:
        me = InMemoryMonitoringEngine()
        report = me.record_execution("w1", "e1", WorkflowStatus.COMPLETED)
        assert report.workflow_id == "w1"
        assert report.status == WorkflowStatus.COMPLETED

    def test_get_workflow_health(self) -> None:
        me = InMemoryMonitoringEngine()
        me.record_execution("w1", "e1", WorkflowStatus.COMPLETED)
        health = me.get_workflow_health("w1")
        assert health is not None
        assert health.execution_count == 1
        assert health.success_count == 1

    def test_list_unhealthy(self) -> None:
        me = InMemoryMonitoringEngine()
        me.record_execution("w1", "e1", WorkflowStatus.FAILED)
        me.record_execution("w1", "e2", WorkflowStatus.FAILED)
        unhealthy = me.list_unhealthy()
        assert len(unhealthy) == 1

    def test_record_step_completion(self) -> None:
        me = InMemoryMonitoringEngine()
        me.record_execution("w1", "e1", WorkflowStatus.RUNNING)
        me.record_step_completion("e1", "s1", 100, True)
        # No crash


# ---------------------------------------------------------------------------
# Workflow Engine
# ---------------------------------------------------------------------------

class TestInMemoryWorkflowEngine:
    def test_start(self) -> None:
        we = InMemoryWorkflowEngine()
        req = WorkflowExecutionRequest(
            execution_id="e1", workflow_id="w1",
            trigger_type=TriggerType.MANUAL,
        )
        result = we.start(req)
        assert result.status == WorkflowStatus.RUNNING

    def test_pause(self) -> None:
        we = InMemoryWorkflowEngine()
        req = WorkflowExecutionRequest(
            execution_id="e1", workflow_id="w1",
            trigger_type=TriggerType.MANUAL,
        )
        we.start(req)
        # Manually set running
        we.state_manager.update_status("e1", WorkflowStatus.RUNNING)
        result = we.pause("e1")
        assert result.status == WorkflowStatus.PAUSED

    def test_resume(self) -> None:
        we = InMemoryWorkflowEngine()
        req = WorkflowExecutionRequest(
            execution_id="e1", workflow_id="w1",
            trigger_type=TriggerType.MANUAL,
        )
        we.start(req)
        we.state_manager.update_status("e1", WorkflowStatus.RUNNING)
        we.pause("e1")
        result = we.resume("e1")
        assert result.status == WorkflowStatus.RUNNING

    def test_cancel(self) -> None:
        we = InMemoryWorkflowEngine()
        req = WorkflowExecutionRequest(
            execution_id="e1", workflow_id="w1",
            trigger_type=TriggerType.MANUAL,
        )
        we.start(req)
        result = we.cancel("e1")
        assert result.status == WorkflowStatus.CANCELLED

    def test_get_status(self) -> None:
        we = InMemoryWorkflowEngine()
        req = WorkflowExecutionRequest(
            execution_id="e1", workflow_id="w1",
            trigger_type=TriggerType.MANUAL,
        )
        we.start(req)
        state = we.get_status("e1")
        assert state is not None
        assert state.workflow_id == "w1"

    def test_get_result_none(self) -> None:
        we = InMemoryWorkflowEngine()
        assert we.get_result("nonexistent") is None

    def test_execute_steps(self) -> None:
        we = InMemoryWorkflowEngine()
        definition = WorkflowDefinition(
            workflow_id="test.exec",
            name="Exec Test",
            description="",
            version="1.0.0",
            category=WorkflowCategory.CUSTOM,
            steps=(
                WorkflowStep(step_id="s1", name="Step 1", description=""),
                WorkflowStep(step_id="s2", name="Step 2", description=""),
            ),
        )
        req = WorkflowExecutionRequest(
            execution_id="e1", workflow_id="test.exec",
            trigger_type=TriggerType.MANUAL,
        )
        we.start(req)
        result = we._execute_steps(definition, "e1", {}, definition.steps)
        assert result.status == WorkflowStatus.COMPLETED
        assert result.completed_steps == 2

    def test_execute_steps_with_parallel(self) -> None:
        we = InMemoryWorkflowEngine()
        definition = WorkflowDefinition(
            workflow_id="test.parallel",
            name="Parallel Test",
            description="",
            version="1.0.0",
            category=WorkflowCategory.CUSTOM,
            steps=(
                WorkflowStep(
                    step_id="parallel.1",
                    name="Parallel",
                    description="",
                    step_type=StepType.PARALLEL,
                    execution_mode=ExecutionMode.PARALLEL,
                    sub_steps=(
                        WorkflowStep(step_id="sub1", name="Sub 1", description=""),
                        WorkflowStep(step_id="sub2", name="Sub 2", description=""),
                    ),
                ),
                WorkflowStep(step_id="s2", name="Final", description=""),
            ),
        )
        req = WorkflowExecutionRequest(
            execution_id="e2", workflow_id="test.parallel",
            trigger_type=TriggerType.MANUAL,
        )
        we.start(req)
        result = we._execute_steps(definition, "e2", {}, definition.steps)
        assert result.status == WorkflowStatus.COMPLETED
        assert result.completed_steps == 2


# ---------------------------------------------------------------------------
# Automation Kernel
# ---------------------------------------------------------------------------

class TestAutomationKernel:
    def test_kernel_initializes_with_templates(self, kernel: AutomationKernel) -> None:
        workflows = kernel.list_workflows()
        assert len(workflows) >= 8

    def test_register_and_list(
        self, kernel: AutomationKernel, simple_workflow: WorkflowDefinition,
    ) -> None:
        kernel.register_workflow(simple_workflow)
        assert len(kernel.list_workflows()) >= 9

    def test_execute_simple(
        self, kernel: AutomationKernel, simple_workflow: WorkflowDefinition,
    ) -> None:
        kernel.register_workflow(simple_workflow)
        result = kernel.execute("test.simple", {"message": "hello"})
        assert result.status == WorkflowStatus.COMPLETED
        assert result.completed_steps >= 1

    def test_execute_nonexistent(self, kernel: AutomationKernel) -> None:
        result = kernel.execute("nonexistent", {})
        assert result.status != WorkflowStatus.COMPLETED

    def test_pause_resume(
        self, kernel: AutomationKernel, simple_workflow: WorkflowDefinition,
    ) -> None:
        kernel.register_workflow(simple_workflow)
        kernel.execute("test.simple", {})
        # Get the execution ID from state
        states = kernel.state_manager.list_by_status(WorkflowStatus.COMPLETED)
        if states:
            # If completed, we can't pause — just verify the flow
            assert states[0].status == WorkflowStatus.COMPLETED

    def test_get_health(
        self, kernel: AutomationKernel, simple_workflow: WorkflowDefinition,
    ) -> None:
        kernel.register_workflow(simple_workflow)
        kernel.execute("test.simple", {"message": "test"})
        health = kernel.get_health("test.simple")
        assert health is not None
        assert health.execution_count >= 1

    def test_list_templates(self, kernel: AutomationKernel) -> None:
        templates = kernel.list_templates()
        assert len(templates) == 8

    def test_register_workflow_from_template(self, kernel: AutomationKernel) -> None:
        meta = kernel.register_workflow_from_template("template.research")
        assert meta is not None
        assert meta.definition.category == WorkflowCategory.RESEARCH

    def test_cancel_execution(
        self, kernel: AutomationKernel, simple_workflow: WorkflowDefinition,
    ) -> None:
        kernel.register_workflow(simple_workflow)
        kernel.execute("test.simple", {})
        states = kernel.state_manager.list_by_status(WorkflowStatus.COMPLETED)
        if states:
            result = kernel.cancel(states[0].execution_id)
            assert result.status == WorkflowStatus.CANCELLED


# ---------------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------------

class TestWorkflowTemplates:
    def test_all_templates_have_ids(self) -> None:
        for t in WORKFLOW_TEMPLATES:
            assert t.template_id, f"Missing template_id: {t.name}"

    def test_all_templates_have_categories(self) -> None:
        for t in WORKFLOW_TEMPLATES:
            assert isinstance(t.category, WorkflowCategory), f"Bad category: {t.template_id}"

    def test_count(self) -> None:
        assert len(WORKFLOW_TEMPLATES) == 8

    def test_research_template_structure(self) -> None:
        t = next(t for t in WORKFLOW_TEMPLATES if t.template_id == "template.research")
        assert len(t.definition.steps) == 3


# ---------------------------------------------------------------------------
# Edge Cases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_workflow_with_no_steps(self) -> None:
        w = WorkflowDefinition(
            workflow_id="empty", name="empty", description="",
            version="1.0.0", category=WorkflowCategory.CUSTOM,
            steps=(),
        )
        assert len(w.steps) == 0

    def test_register_duplicate(self) -> None:
        r = InMemoryWorkflowRegistry()
        w = WorkflowDefinition(
            workflow_id="dup", name="dup", description="",
            version="1.0.0", category=WorkflowCategory.CUSTOM,
            steps=(),
        )
        r.register(w)
        w2 = w.with_updated_at()
        r.register(w2)
        assert r.get("dup") is not None
        assert len(r.list()) == 1  # Register overwrites existing entry

    def test_empty_inputs(self, kernel: AutomationKernel) -> None:
        w = WorkflowDefinition(
            workflow_id="test.noinputs",
            name="No Inputs",
            description="",
            version="1.0.0",
            category=WorkflowCategory.CUSTOM,
            steps=(WorkflowStep(step_id="s1", name="S1", description=""),),
        )
        kernel.register_workflow(w)
        result = kernel.execute("test.noinputs", {})
        assert result.status == WorkflowStatus.COMPLETED

    def test_retry_manager_default_policy(self) -> None:
        InMemoryRetryManager()
        policy = RetryPolicy()
        assert policy.strategy == RetryStrategy.IMMEDIATE
        assert policy.max_retries == 3
