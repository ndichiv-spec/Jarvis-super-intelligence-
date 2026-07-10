from jarvis_planning.analyzer import Goal
from jarvis_planning.decomposer import Task
from jarvis_planning.dependency_graph import DependencyGraph
from jarvis_planning.validator import PlanValidator, ValidationIssue, ValidationResult


class TestValidationIssue:
    def test_creation(self) -> None:
        issue = ValidationIssue("error", "Something is wrong", "location", "Fix it")
        assert issue.severity == "error"
        assert issue.message == "Something is wrong"

    def test_to_dict(self) -> None:
        issue = ValidationIssue("warning", "Be careful", "field", "Review")
        d = issue.to_dict()
        assert d["severity"] == "warning"
        assert d["location"] == "field"


class TestValidationResult:
    def test_to_dict(self) -> None:
        result = ValidationResult(valid=True, issues=[
            ValidationIssue("warning", "test msg", "loc", "sugg")
        ])
        d = result.to_dict()
        assert d["valid"] is True
        assert d["issue_count"] == 1


class TestPlanValidator:
    def test_validate_goal_empty(self) -> None:
        v = PlanValidator()
        result = v.validate_goal(Goal(objective=""))
        assert result.valid is False
        assert any(i.severity == "error" for i in result.issues)

    def test_validate_goal_short(self) -> None:
        v = PlanValidator()
        result = v.validate_goal(Goal(objective="Hi"))
        assert any(i.severity == "warning" for i in result.issues)

    def test_validate_goal_with_ambiguity(self) -> None:
        v = PlanValidator()
        result = v.validate_goal(Goal(objective="Build something", ambiguity=["vague"]))
        assert any("ambiguous" in i.message.lower() for i in result.issues)

    def test_validate_goal_no_deliverables_warning(self) -> None:
        v = PlanValidator()
        result = v.validate_goal(Goal(objective="Test project", deliverables=[]))
        assert any("deliverables" in i.message.lower() for i in result.issues)

    def test_validate_goal_good(self) -> None:
        v = PlanValidator()
        result = v.validate_goal(Goal(
            objective="Build a professional inventory management platform",
            deliverables=["source_code"],
        ))
        assert result.valid is True

    def test_validate_graph_cycle(self) -> None:
        v = PlanValidator()
        g = DependencyGraph()
        g.add_task(Task(id="t1", title="T1", description="", dependencies=["t2"]))
        g.add_task(Task(id="t2", title="T2", description="", dependencies=["t1"]))
        result = v.validate_graph(g)
        assert result.valid is False
        assert any("cycle" in i.message.lower() for i in result.issues)

    def test_validate_graph_missing_dep(self) -> None:
        v = PlanValidator()
        g = DependencyGraph()
        g.add_task(Task(id="t1", title="T1", description="", dependencies=["nonexistent"]))
        result = v.validate_graph(g)
        assert result.valid is False
        assert any("missing" in i.message.lower() for i in result.issues)

    def test_validate_graph_ok(self) -> None:
        v = PlanValidator()
        g = DependencyGraph()
        g.add_task(Task(id="t1", title="T1", description="", estimated_effort_hours=1.0))
        g.add_task(Task(id="t2", title="T2", description="", dependencies=["t1"], estimated_effort_hours=1.0))
        result = v.validate_graph(g)
        assert result.valid is True

    def test_validate_tasks(self) -> None:
        v = PlanValidator()
        result = v.validate_tasks([
            Task(id="t1", title="T1", description="", estimated_effort_hours=1.0),
        ])
        assert result.valid is True

    def test_validate_plan_completeness_empty(self) -> None:
        v = PlanValidator()
        g = DependencyGraph()
        result = v.validate_plan_completeness(g)
        assert result.valid is False

    def test_validate_all(self) -> None:
        v = PlanValidator()
        goal = Goal(objective="Build a platform", deliverables=["code"])
        g = DependencyGraph()
        g.add_task(Task(id="t1", title="T1", description="", estimated_effort_hours=1.0))
        result = v.validate_all(goal, g)
        assert result.valid is True
