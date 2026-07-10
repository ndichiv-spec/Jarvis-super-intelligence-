import pytest
from jarvis_intelligence.coordinator import CoordinatorEngine, CoordinationReport
from jarvis_intelligence.tasks import Task, TaskGraph
from jarvis_intelligence.context import ExecutionContext


class TestCoordinatorEngine:
    @pytest.mark.asyncio
    async def test_coordinate_simple_graph(self):
        engine = CoordinatorEngine()
        graph = TaskGraph()
        t1 = Task.create(description="Design the module")
        t2 = Task.create(description="Build the module", depends_on=(t1.id,))
        graph.add(t1)
        graph.add(t2)
        report = await engine.coordinate("plan-1", graph)
        assert isinstance(report, CoordinationReport)
        assert report.total_tasks == 2
        assert report.completed_tasks == 2
        assert report.failed_tasks == 0
        assert report.decisions_made > 0
        assert report.plan_id == "plan-1"

    @pytest.mark.asyncio
    async def test_coordinate_empty_graph(self):
        engine = CoordinatorEngine()
        graph = TaskGraph()
        report = await engine.coordinate("plan-empty", graph)
        assert report.total_tasks == 0
        assert report.completed_tasks == 0

    @pytest.mark.asyncio
    async def test_coordinate_with_context(self):
        engine = CoordinatorEngine()
        graph = TaskGraph()
        task = Task.create(description="Deploy the application")
        graph.add(task)
        ctx = ExecutionContext()
        ctx.metadata["env"] = "production"
        report = await engine.coordinate("plan-ctx", graph, ctx)
        assert report.completed_tasks == 1

    @pytest.mark.asyncio
    async def test_get_report(self):
        engine = CoordinatorEngine()
        graph = TaskGraph()
        graph.add(Task.create(description="Test task"))
        await engine.coordinate("plan-get", graph)
        report = engine.get_report("plan-get")
        assert report is not None
        assert report.plan_id == "plan-get"

    @pytest.mark.asyncio
    async def test_get_report_nonexistent(self):
        engine = CoordinatorEngine()
        assert engine.get_report("nonexistent") is None

    @pytest.mark.asyncio
    async def test_coordinate_duration_recorded(self):
        engine = CoordinatorEngine()
        graph = TaskGraph()
        graph.add(Task.create(description="Quick task"))
        report = await engine.coordinate("plan-dur", graph)
        assert report.duration_seconds >= 0
