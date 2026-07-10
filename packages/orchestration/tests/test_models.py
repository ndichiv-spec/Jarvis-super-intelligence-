import pytest
from jarvis_orchestration.models import Workflow, WorkflowStep, WorkflowExecution, WorkflowStatus, StepStatus, WorkflowPriority


class TestWorkflowStep:
    def test_create_defaults(self):
        step = WorkflowStep.create("Build")
        assert step.name == "Build"
        assert step.id.startswith("step-")
        assert step.depends_on == ()
        assert step.max_retries == 3

    def test_create_with_deps(self):
        step = WorkflowStep.create("Test", depends_on=("step-abc",), max_retries=5, timeout_seconds=120)
        assert "step-abc" in step.depends_on
        assert step.max_retries == 5
        assert step.timeout_seconds == 120

    def test_frozen(self):
        step = WorkflowStep.create("Frozen")
        with pytest.raises(AttributeError):
            step.name = "changed"  # type: ignore[misc]


class TestWorkflow:
    def test_create_defaults(self):
        wf = Workflow.create("Deploy pipeline")
        assert wf.name == "Deploy pipeline"
        assert wf.id.startswith("wf-")
        assert wf.priority == WorkflowPriority.MEDIUM
        assert wf.owner == "system"

    def test_create_with_steps(self):
        s1 = WorkflowStep.create("Build")
        s2 = WorkflowStep.create("Test", depends_on=(s1.id,))
        wf = Workflow.create("CI/CD", priority=WorkflowPriority.HIGH, owner="devops",
                             tags=("ci", "deploy"), steps=(s1, s2))
        assert wf.priority == WorkflowPriority.HIGH
        assert len(wf.steps) == 2
        assert "ci" in wf.tags


class TestWorkflowExecution:
    def test_create(self):
        wf = Workflow.create("Test workflow", steps=(WorkflowStep.create("A"), WorkflowStep.create("B")))
        exec_ = WorkflowExecution.create(wf)
        assert exec_.id.startswith("exec-")
        assert exec_.workflow_id == wf.id
        assert exec_.status == WorkflowStatus.PENDING
        assert len(exec_.step_states) == 2
        assert all(s == StepStatus.PENDING for s in exec_.step_states.values())
