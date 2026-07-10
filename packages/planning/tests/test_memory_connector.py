from datetime import UTC, datetime

from jarvis_planning.analyzer import Goal
from jarvis_planning.decomposer import Task
from jarvis_planning.dependency_graph import DependencyGraph
from jarvis_planning.events import EventBus
from jarvis_planning.executor import Executor
from jarvis_planning.memory_connector import MemoryConnector, PlanMemoryRecord
from jarvis_planning.planner import Plan
from jarvis_planning.scheduler import Scheduler


class TestPlanMemoryRecord:
    def test_creation(self) -> None:
        now = datetime.now(UTC)
        record = PlanMemoryRecord(
            plan_id="p1", objective="Build app", goal=None, tasks=[],
            status="completed", created_at=now, completed_at=now,
        )
        assert record.plan_id == "p1"
        assert record.outcome == ""
        assert record.lessons == []

    def test_to_dict(self) -> None:
        now = datetime.now(UTC)
        goal = Goal(objective="Build app")
        task = Task(id="t1", title="Task 1", description="")
        record = PlanMemoryRecord(
            plan_id="p1", objective="Build app", goal=goal, tasks=[task],
            status="completed", created_at=now, completed_at=now,
            outcome="success"
        )
        d = record.to_dict()
        assert d["plan_id"] == "p1"
        assert d["outcome"] == "success"
        assert len(d["tasks"]) == 1


class TestMemoryConnector:
    def test_store_plan_no_kernel(self) -> None:
        mc = MemoryConnector()
        plan = Plan(id="p1", objective="test")
        record = mc.store_plan(plan)
        assert record.metadata.identifier == "plan-p1"

    def test_store_execution_result_no_kernel(self) -> None:
        mc = MemoryConnector()
        plan = Plan(id="p1", objective="test")
        g = DependencyGraph()
        g.add_task(Task(id="t1", title="T1", description=""))
        s = Scheduler(g)
        eb = EventBus()
        ex = Executor(s, eb)
        ex.set_plan_id("p1")
        record = mc.store_execution_result(plan, ex)
        assert record is not None

    def test_retrieve_similar_plans_no_kernel(self) -> None:
        mc = MemoryConnector()
        results = mc.retrieve_similar_plans("build an app")
        assert results == []

    def test_store_plan_with_kernel(self) -> None:
        mc = MemoryConnector(None)
        plan = Plan(id="p1", objective="Build an inventory management platform")
        record = mc.store_plan(plan)
        assert record.metadata.identifier == "plan-p1"
