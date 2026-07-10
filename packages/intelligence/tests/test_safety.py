from datetime import UTC, datetime, timedelta
from jarvis_intelligence.safety import SafetyEngine, SafetyCheck
from jarvis_intelligence.goals import Goal, GoalPriority
from jarvis_intelligence.tasks import Task, TaskGraph


class TestSafetyEngine:
    def test_validate_goal_no_deadline(self):
        engine = SafetyEngine()
        goal = Goal.create(description="Safe goal")
        checks = engine.validate_goal(goal)
        assert len(checks) >= 1
        assert any(c.check_name == "goal_valid" for c in checks)

    def test_validate_goal_long_description(self):
        engine = SafetyEngine()
        goal = Goal.create(description="x" * 2500)
        checks = engine.validate_goal(goal)
        names = [c.check_name for c in checks]
        assert "description_length" in names

    def test_validate_goal_short_description(self):
        engine = SafetyEngine()
        goal = Goal.create(description="Short")
        checks = engine.validate_goal(goal)
        assert all(c.passed for c in checks if c.severity != "info")

    def test_validate_task_graph_empty(self):
        engine = SafetyEngine()
        graph = TaskGraph()
        checks = engine.validate_task_graph(graph)
        assert len(checks) >= 1
        assert checks[-1].passed

    def test_validate_task_graph_acyclic(self):
        engine = SafetyEngine()
        graph = TaskGraph()
        t1 = Task.create(description="Root")
        t2 = Task.create(description="Child", depends_on=(t1.id,))
        graph.add(t1)
        graph.add(t2)
        checks = engine.validate_task_graph(graph)
        critical = [c for c in checks if c.severity == "critical" and not c.passed]
        assert len(critical) == 0

    def test_validate_task_graph_cycle_detected(self):
        engine = SafetyEngine()
        graph = TaskGraph()
        t1 = Task.create(description="A")
        t2 = Task.create(description="B", depends_on=(t1.id,))
        t1_with_dep = Task.create(
            description="A with dep on B",
            depends_on=(t2.id,),
        )
        task_a = Task(
            id=t1.id,
            description=t1.description,
            depends_on=(t2.id,),
        )
        graph.add(task_a)
        graph.add(t2)
        checks = engine.validate_task_graph(graph)
        circular = [c for c in checks if c.check_name == "circular_dependency"]
        assert len(circular) > 0

    def test_validate_execution_normal(self):
        engine = SafetyEngine()
        task = Task.create(description="Normal task", max_retries=3, timeout_seconds=300)
        checks = engine.validate_execution(task)
        assert all(c.passed for c in checks)

    def test_validate_execution_high_retries(self):
        engine = SafetyEngine()
        task = Task.create(description="High retry", max_retries=15)
        checks = engine.validate_execution(task)
        assert any(not c.passed for c in checks if c.check_name == "max_retries")

    def test_validate_execution_long_timeout(self):
        engine = SafetyEngine()
        task = Task.create(description="Long timeout", timeout_seconds=90000)
        checks = engine.validate_execution(task)
        assert any(not c.passed for c in checks if c.check_name == "timeout")

    def test_get_all_checks(self):
        engine = SafetyEngine()
        assert engine.get_all_checks() == []
        engine.validate_goal(Goal.create(description="Test"))
        assert len(engine.get_all_checks()) > 0

    def test_safety_check_dataclass(self):
        check = SafetyCheck(passed=True, check_name="test", details="OK", severity="info")
        assert check.passed is True
        assert check.check_name == "test"
        assert check.severity == "info"
