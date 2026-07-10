from jarvis_planning.analyzer import Goal
from jarvis_planning.decomposer import Task, TaskDecomposer, TaskInput, TaskOutput, TaskType
from jarvis_planning.estimator import Complexity


class TestTask:
    def test_task_creation(self) -> None:
        t = Task(id="task-01", title="Test Task", description="A test task")
        assert t.id == "task-01"
        assert t.title == "Test Task"
        assert t.task_type == TaskType.ATOMIC
        assert t.priority == 0
        assert t.assigned_agent == ""
        assert t.estimated_effort_hours == 1.0

    def test_task_to_dict(self) -> None:
        t = Task(id="task-01", title="Test", description="Desc",
                 task_type=TaskType.HIERARCHICAL, priority=5, group="dev")
        d = t.to_dict()
        assert d["id"] == "task-01"
        assert d["task_type"] == "hierarchical"
        assert d["priority"] == 5
        assert d["group"] == "dev"

    def test_task_with_inputs_outputs(self) -> None:
        t = Task(
            id="task-01", title="Test", description="Desc",
            inputs=[TaskInput(name="data", description="Input data")],
            outputs=[TaskOutput(name="result", description="Output result")],
        )
        assert len(t.inputs) == 1
        assert t.inputs[0].name == "data"
        assert len(t.outputs) == 1
        assert t.outputs[0].name == "result"


class TestTaskInput:
    def test_defaults(self) -> None:
        inp = TaskInput(name="cfg", description="Configuration")
        assert inp.required is True
        assert inp.source_task_id is None

    def test_to_dict(self) -> None:
        inp = TaskInput(name="cfg", description="Config", required=False, source_task_id="task-00")
        d = inp.to_dict()
        assert d["required"] is False
        assert d["source_task_id"] == "task-00"


class TestTaskOutput:
    def test_defaults(self) -> None:
        out = TaskOutput(name="result", description="Result")
        assert out.type == "artifact"

    def test_to_dict(self) -> None:
        out = TaskOutput(name="code", description="Source", type="code")
        d = out.to_dict()
        assert d["type"] == "code"


class TestTaskDecomposer:
    def test_decompose_web_app(self) -> None:
        goal = Goal(objective="Build a web application", category="web")
        decomposer = TaskDecomposer()
        tasks = decomposer.decompose(goal)
        assert len(tasks) == 8
        assert tasks[0].title == "Gather Requirements"
        assert tasks[0].group == "initiation"

    def test_decompose_mobile_app(self) -> None:
        goal = Goal(objective="Build a mobile app", category="mobile")
        decomposer = TaskDecomposer()
        tasks = decomposer.decompose(goal)
        assert len(tasks) == 7
        assert any("Mobile" in t.title for t in tasks)

    def test_decompose_data_pipeline(self) -> None:
        goal = Goal(objective="Build data pipeline", category="data")
        decomposer = TaskDecomposer()
        tasks = decomposer.decompose(goal)
        assert len(tasks) == 7
        assert any("ETL" in t.title for t in tasks)

    def test_decompose_ml_project(self) -> None:
        goal = Goal(objective="Build ML model", category="ai-ml")
        decomposer = TaskDecomposer()
        tasks = decomposer.decompose(goal)
        assert len(tasks) == 7
        assert any("Model" in t.title for t in tasks)

    def test_decompose_devops(self) -> None:
        goal = Goal(objective="Setup CI/CD", category="devops")
        decomposer = TaskDecomposer()
        tasks = decomposer.decompose(goal)
        assert len(tasks) == 7

    def test_decompose_security(self) -> None:
        goal = Goal(objective="Security audit", category="security")
        decomposer = TaskDecomposer()
        tasks = decomposer.decompose(goal)
        assert len(tasks) == 6

    def test_decompose_general(self) -> None:
        goal = Goal(objective="General project", category="general")
        decomposer = TaskDecomposer()
        tasks = decomposer.decompose(goal)
        assert len(tasks) == 5

    def test_decompose_with_templates(self) -> None:
        goal = Goal(objective="Test")
        decomposer = TaskDecomposer()
        tasks = decomposer.decompose(goal, template_names=["gather_requirements", "testing"])
        assert len(tasks) == 2
        assert tasks[0].title == "Gather Requirements"
        assert tasks[1].title == "Testing"
        assert tasks[1].dependencies == ["task-01"]

    def test_dependencies_linked_within_groups(self) -> None:
        goal = Goal(objective="Build web app", category="web")
        decomposer = TaskDecomposer()
        tasks = decomposer.decompose(goal)
        dev_tasks = [t for t in tasks if t.group == "development"]
        if len(dev_tasks) > 1:
            for i in range(1, len(dev_tasks)):
                assert dev_tasks[i - 1].id in dev_tasks[i].dependencies

    def test_get_available_templates(self) -> None:
        decomposer = TaskDecomposer()
        templates = decomposer.get_available_templates()
        assert "gather_requirements" in templates
        assert "testing" in templates
        assert "design_architecture" in templates
