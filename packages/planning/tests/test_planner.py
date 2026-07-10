from jarvis_planning.analyzer import Goal
from jarvis_planning.events import EventBus
from jarvis_planning.planner import Plan, PlanStatus, Planner
from jarvis_planning.validator import ValidationResult


class TestPlan:
    def test_creation(self) -> None:
        p = Plan(id="p1", objective="Build an app")
        assert p.id == "p1"
        assert p.status == PlanStatus.CREATED
        assert p.metadata == {}

    def test_to_dict(self) -> None:
        p = Plan(id="p1", objective="Test", status=PlanStatus.ANALYZED)
        d = p.to_dict()
        assert d["id"] == "p1"
        assert d["status"] == "analyzed"

    def test_to_dict_with_goal(self) -> None:
        p = Plan(id="p1", objective="Test", goal=Goal(objective="Test"))
        d = p.to_dict()
        assert d["goal"] is not None
        assert d["goal"]["objective"] == "Test"

    def test_to_dict_with_validation(self) -> None:
        p = Plan(id="p1", objective="Test", validation=ValidationResult(valid=True))
        d = p.to_dict()
        assert d["validation"] is not None
        assert d["validation"]["valid"] is True


class TestPlanner:
    def test_create_plan(self) -> None:
        planner = Planner()
        plan = planner.create_plan("Build an accounting app")
        assert plan.id is not None
        assert plan.objective == "Build an accounting app"

    def test_analyze(self) -> None:
        planner = Planner()
        plan = planner.create_plan("Build a web portal")
        plan = planner.analyze(plan.id)
        assert plan.goal is not None
        assert plan.goal.category == "web"
        assert plan.status == PlanStatus.ANALYZED

    def test_decompose(self) -> None:
        planner = Planner()
        plan = planner.create_plan("Build a web application")
        plan = planner.decompose(plan.id)
        assert len(plan.tasks) > 0
        assert plan.graph is not None
        assert plan.status == PlanStatus.DECOMPOSED

    def test_decompose_with_templates(self) -> None:
        planner = Planner()
        plan = planner.decompose(
            planner.create_plan("Test").id,
            templates=["gather_requirements", "testing"],
        )
        assert len(plan.tasks) == 2

    def test_decompose_auto_analyzes(self) -> None:
        planner = Planner()
        plan = planner.create_plan("Build a web application")
        plan = planner.decompose(plan.id)
        assert plan.goal is not None

    def test_validate(self) -> None:
        planner = Planner()
        plan = planner.create_plan("Build a web application")
        plan = planner.decompose(plan.id)
        plan = planner.validate(plan.id)
        assert plan.validation is not None
        assert plan.status == PlanStatus.VALIDATED

    def test_prepare_execution(self) -> None:
        planner = Planner()
        plan = planner.full_plan("Build a web app")
        assert plan.scheduler is not None
        assert plan.status == PlanStatus.EXECUTING

    def test_full_plan(self) -> None:
        planner = Planner()
        plan = planner.full_plan("Build a web application")
        assert plan.goal is not None
        assert len(plan.tasks) > 0
        assert plan.graph is not None
        assert plan.scheduler is not None

    def test_execute_all(self) -> None:
        planner = Planner()
        plan = planner.full_plan("Build a web application")
        plan = planner.execute_all(plan.id)
        assert plan.status == PlanStatus.COMPLETED

    def test_execute_next(self) -> None:
        planner = Planner()
        plan = planner.full_plan("Build a web app")
        plan = planner.execute_next(plan.id)
        assert plan.status in (PlanStatus.EXECUTING, PlanStatus.COMPLETED)

    def test_get_plan(self) -> None:
        planner = Planner()
        created = planner.create_plan("Test")
        retrieved = planner.get_plan(created.id)
        assert retrieved is not None
        assert retrieved.id == created.id

    def test_get_plan_not_found(self) -> None:
        planner = Planner()
        assert planner.get_plan("nonexistent") is None

    def test_get_progress(self) -> None:
        planner = Planner()
        plan = planner.full_plan("Build a web app")
        progress = planner.get_progress(plan.id)
        assert progress is not None
        assert progress.total_tasks > 0

    def test_get_progress_no_monitor(self) -> None:
        planner = Planner()
        plan = planner.create_plan("Test")
        assert planner.get_progress(plan.id) is None

    def test_get_explanation_with_full_plan(self) -> None:
        planner = Planner()
        plan = planner.full_plan("Build a web application")
        exp = planner.get_explanation(plan.id)
        assert len(exp.sections) >= 1

    def test_get_explanation_goal_only(self) -> None:
        planner = Planner()
        plan = planner.create_plan("Build a web app")
        plan = planner.analyze(plan.id)
        exp = planner.get_explanation(plan.id)
        assert len(exp.sections) >= 1

    def test_get_explanation_no_plan(self) -> None:
        planner = Planner()
        plan = planner.create_plan("Test")
        exp = planner.get_explanation(plan.id)
        assert len(exp.sections) == 0

    def test_get_completion_summary(self) -> None:
        planner = Planner()
        plan = planner.full_plan("Build a web app")
        planner.execute_all(plan.id)
        exp = planner.get_completion_summary(plan.id)
        assert len(exp.sections) >= 1

    def test_cancel_plan(self) -> None:
        planner = Planner()
        plan = planner.create_plan("Test")
        plan = planner.cancel_plan(plan.id)
        assert plan.status == PlanStatus.CANCELLED

    def test_list_plans(self) -> None:
        planner = Planner()
        planner.create_plan("Plan 1")
        planner.create_plan("Plan 2")
        plans = planner.list_plans()
        assert len(plans) == 2

    def test_replan(self) -> None:
        planner = Planner()
        plan = planner.full_plan("Build a web app")
        result = planner.replan(plan.id, "requirement_change", {"changed_areas": ["frontend"]})
        assert result is not None

    def test_get_plan_by_nonexistent_id(self) -> None:
        planner = Planner()
        try:
            planner._get_plan("nonexistent")
            assert False
        except ValueError as e:
            assert "not found" in str(e)

    def test_get_executor_not_prepared(self) -> None:
        planner = Planner()
        plan = planner.create_plan("Test")
        try:
            planner._get_executor(plan.id)
            assert False
        except ValueError as e:
            assert "prepare_execution" in str(e)

    def test_register_executor(self) -> None:
        planner = Planner()
        plan = planner.full_plan("Build a web app")
        planner.register_executor(plan.id, "__default__", lambda t, o: {"custom": True})
        plan = planner.execute_all(plan.id)
        assert plan.status == PlanStatus.COMPLETED

    def test_assign_agents_no_assigner(self) -> None:
        planner = Planner()
        plan = planner.create_plan("Test")
        plan = planner.decompose(plan.id)
        assignments = planner.assign_agents(plan.id)
        assert assignments == []

    def test_store_to_memory_no_connector(self) -> None:
        planner = Planner()
        plan = planner.create_plan("Test")
        result = planner.store_to_memory(plan.id)
        assert result is None

    def test_retrieve_similar_plans_no_connector(self) -> None:
        planner = Planner()
        results = planner.retrieve_similar_plans("build an app")
        assert results == []

    def test_event_bus(self) -> None:
        planner = Planner()
        assert planner.event_bus is not None

    def test_full_plan_without_agent_memory(self) -> None:
        planner = Planner()
        plan = planner.full_plan("Build a web app", assign_agents=False, store_memory=False)
        assert plan.goal is not None
        assert plan.status == PlanStatus.EXECUTING

    def test_execute_all_without_memory(self) -> None:
        planner = Planner()
        plan = planner.full_plan("Build a web app", store_memory=False)
        plan = planner.execute_all(plan.id, store_memory=False)
        assert plan.status == PlanStatus.COMPLETED

    def test_analyze_empty_objective(self) -> None:
        planner = Planner()
        plan = planner.create_plan("")
        plan = planner.analyze(plan.id)
        assert plan.goal is not None

    def test_templates_in_create_plan(self) -> None:
        planner = Planner()
        plan = planner.create_plan("Test", templates=["gather_requirements"])
        assert plan is not None
