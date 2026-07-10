import pytest
from jarvis_orchestration.models import Workflow, WorkflowStep, WorkflowStatus, StepStatus
from jarvis_orchestration.engine import OrchestrationEngine


def _make_workflow(name: str = "Test", step_count: int = 2) -> Workflow:
    steps: list[WorkflowStep] = []
    for i in range(step_count):
        dep = (steps[i - 1].id,) if i > 0 else ()
        steps.append(WorkflowStep.create(f"Step {i}", depends_on=dep))
    return Workflow.create(name, steps=tuple(steps))


class TestOrchestrationEngine:
    def test_register_and_start(self):
        engine = OrchestrationEngine()
        wf = _make_workflow()
        engine.register(wf)
        exec_ = engine.start(wf.id)
        assert exec_ is not None
        assert exec_.status == WorkflowStatus.RUNNING

    def test_start_nonexistent(self):
        engine = OrchestrationEngine()
        assert engine.start("nonexistent") is None

    def test_advance_completes_step(self):
        engine = OrchestrationEngine()
        wf = _make_workflow()
        engine.register(wf)
        exec_ = engine.start(wf.id)
        first_step = wf.steps[0]
        result = engine.advance(exec_.id, first_step.id, success=True, output={"built": True})
        assert result is not None
        assert result.step_states[first_step.id] == StepStatus.COMPLETED

    def test_advance_completes_workflow(self):
        engine = OrchestrationEngine()
        wf = Workflow.create("Single", steps=(WorkflowStep.create("Only step"),))
        engine.register(wf)
        exec_ = engine.start(wf.id)
        engine.advance(exec_.id, wf.steps[0].id, success=True)
        assert exec_.status == WorkflowStatus.COMPLETED

    def test_advance_step_failure_no_retry(self):
        engine = OrchestrationEngine()
        s1 = WorkflowStep.create("Fail fast", max_retries=0)
        wf = Workflow.create("No retry", steps=(s1,))
        engine.register(wf)
        exec_ = engine.start(wf.id)
        engine.advance(exec_.id, s1.id, success=False, error="Build failed")
        assert exec_.step_states[s1.id] == StepStatus.FAILED
        assert exec_.status == WorkflowStatus.FAILED

    def test_advance_step_failure_retries(self):
        engine = OrchestrationEngine()
        wf = _make_workflow()
        engine.register(wf)
        exec_ = engine.start(wf.id)
        engine.advance(exec_.id, wf.steps[0].id, success=False, error="Retryable error")
        assert exec_.step_states[wf.steps[0].id] == StepStatus.READY
        assert exec_.status == WorkflowStatus.RUNNING

    def test_pause_and_resume(self):
        engine = OrchestrationEngine()
        wf = _make_workflow()
        engine.register(wf)
        exec_ = engine.start(wf.id)
        engine.pause(exec_.id)
        assert exec_.status == WorkflowStatus.PAUSED
        engine.resume(exec_.id)
        assert exec_.status == WorkflowStatus.RUNNING

    def test_cancel(self):
        engine = OrchestrationEngine()
        wf = _make_workflow()
        engine.register(wf)
        exec_ = engine.start(wf.id)
        engine.cancel(exec_.id)
        assert exec_.status == WorkflowStatus.CANCELLED

    def test_get_execution(self):
        engine = OrchestrationEngine()
        wf = _make_workflow()
        engine.register(wf)
        exec_ = engine.start(wf.id)
        assert engine.get_execution(exec_.id) is exec_

    def test_get_execution_nonexistent(self):
        engine = OrchestrationEngine()
        assert engine.get_execution("nonexistent") is None

    def test_list_executions(self):
        engine = OrchestrationEngine()
        wf = _make_workflow("WF1")
        wf2 = _make_workflow("WF2")
        engine.register(wf)
        engine.register(wf2)
        e1 = engine.start(wf.id)
        e2 = engine.start(wf2.id)
        all_execs = engine.list_executions()
        assert len(all_execs) == 2
        wf1_execs = engine.list_executions(workflow_id=wf.id)
        assert len(wf1_execs) == 1
        assert wf1_execs[0].id == e1.id

    def test_ready_steps_respected(self):
        engine = OrchestrationEngine()
        s1 = WorkflowStep.create("First")
        s2 = WorkflowStep.create("Second", depends_on=(s1.id,))
        wf = Workflow.create("Ordered", steps=(s1, s2))
        engine.register(wf)
        exec_ = engine.start(wf.id)
        assert exec_.step_states[s1.id] == StepStatus.READY
        assert exec_.step_states[s2.id] == StepStatus.PENDING

    def test_advance_nonexistent_execution(self):
        engine = OrchestrationEngine()
        assert engine.advance("nonexistent", "step-1", success=True) is None

    @property
    def registry(self):
        engine = OrchestrationEngine()
        assert engine.registry is not None
