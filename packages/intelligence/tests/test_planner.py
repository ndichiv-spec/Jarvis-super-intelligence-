import pytest
from jarvis_intelligence.planner import IntelligencePlanner, IntelligencePlan
from jarvis_intelligence.goals import GoalPriority, GoalState
from jarvis_intelligence.tasks import TaskState


class TestIntelligencePlanner:
    def test_create_plan(self):
        planner = IntelligencePlanner()
        plan = planner.create_plan("Build the platform", GoalPriority.HIGH, ("engineering", "devops"))
        assert isinstance(plan, IntelligencePlan)
        assert plan.goal.description == "Build the platform"
        assert plan.goal.priority == GoalPriority.HIGH
        assert plan.goal.state == GoalState.DRAFT
        assert plan.id.startswith("plan-")

    def test_create_plan_defaults(self):
        planner = IntelligencePlanner()
        plan = planner.create_plan("Simple task")
        assert plan.goal.priority == GoalPriority.MEDIUM

    def test_add_objective(self):
        planner = IntelligencePlanner()
        plan = planner.create_plan("Test objective")
        obj = planner.add_objective(plan.id, "Achieve 90% coverage")
        assert obj is not None
        assert obj.description == "Achieve 90% coverage"
        assert len(plan.objectives) == 1

    def test_add_objective_nonexistent_plan(self):
        planner = IntelligencePlanner()
        assert planner.add_objective("nonexistent", "description") is None

    def test_add_task(self):
        planner = IntelligencePlanner()
        plan = planner.create_plan("Test tasks")
        task = planner.add_task(plan.id, "Design the solution")
        assert task is not None
        assert task.description == "Design the solution"
        assert len(plan.task_graph.all()) == 1

    def test_add_task_nonexistent_plan(self):
        planner = IntelligencePlanner()
        assert planner.add_task("nonexistent", "description") is None

    def test_decompose_goal(self):
        planner = IntelligencePlanner()
        plan = planner.create_plan("Build a complete inventory management system")
        decomposed = planner.decompose_goal(plan.id)
        assert decomposed is not None
        assert decomposed.status == "decomposed"
        tasks = decomposed.task_graph.all()
        assert len(tasks) >= 4

    def test_decompose_goal_nonexistent(self):
        planner = IntelligencePlanner()
        assert planner.decompose_goal("nonexistent") is None

    def test_get_plan(self):
        planner = IntelligencePlanner()
        plan = planner.create_plan("Find me")
        assert planner.get_plan(plan.id) is plan

    def test_get_plan_nonexistent(self):
        planner = IntelligencePlanner()
        assert planner.get_plan("nonexistent") is None

    def test_list_plans(self):
        planner = IntelligencePlanner()
        assert len(planner.list_plans()) == 0
        planner.create_plan("A")
        planner.create_plan("B")
        assert len(planner.list_plans()) == 2

    def test_get_goal_manager(self):
        planner = IntelligencePlanner()
        gm = planner.get_goal_manager()
        assert gm is not None
        assert gm.count() == 0
        planner.create_plan("Goal in manager")
        assert gm.count() == 1

    def test_decompose_adds_dependencies(self):
        planner = IntelligencePlanner()
        plan = planner.create_plan("Build a system")
        planner.decompose_goal(plan.id)
        tasks = plan.task_graph.all()
        non_root = [t for t in tasks if t.depends_on]
        assert len(non_root) > 0
