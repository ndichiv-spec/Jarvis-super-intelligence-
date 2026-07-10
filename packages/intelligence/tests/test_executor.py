import pytest
from jarvis_intelligence.executor import ExecutionEngine, ExecutionResult
from jarvis_intelligence.tasks import Task, TaskGraph, TaskState


class TestExecutionEngine:
    @pytest.mark.asyncio
    async def test_execute_deploy_task(self):
        engine = ExecutionEngine()
        task = Task.create(description="Deploy the application to staging")
        result = await engine.execute_task(task)
        assert result.success is True
        assert result.output["status"] == "deployed"
        assert result.started_at is not None
        assert result.completed_at is not None
        assert result.duration_seconds >= 0

    @pytest.mark.asyncio
    async def test_execute_test_task(self):
        engine = ExecutionEngine()
        task = Task.create(description="Run all unit tests")
        result = await engine.execute_task(task)
        assert result.success is True
        assert result.output["passed"] == 42
        assert result.output["coverage"] == 87.5

    @pytest.mark.asyncio
    async def test_execute_document_task(self):
        engine = ExecutionEngine()
        task = Task.create(description="Document the API endpoints")
        result = await engine.execute_task(task)
        assert result.success is True
        assert "architecture" in result.output["sections"]

    @pytest.mark.asyncio
    async def test_execute_build_task(self):
        engine = ExecutionEngine()
        task = Task.create(description="Build the frontend components")
        result = await engine.execute_task(task)
        assert result.success is True
        assert result.output["components"] == 12

    @pytest.mark.asyncio
    async def test_execute_design_task(self):
        engine = ExecutionEngine()
        task = Task.create(description="Design the system architecture")
        result = await engine.execute_task(task)
        assert result.success is True
        assert result.output["decisions"] == 8

    @pytest.mark.asyncio
    async def test_execute_generic_task(self):
        engine = ExecutionEngine()
        task = Task.create(description="Perform analysis on the data")
        result = await engine.execute_task(task)
        assert result.success is True
        assert result.output["status"] == "completed"

    @pytest.mark.asyncio
    async def test_result_defaults(self):
        engine = ExecutionEngine()
        task = Task.create(description="Simple task")
        result = await engine.execute_task(task)
        assert isinstance(result, ExecutionResult)
        assert result.task_id == task.id
        assert result.error is None

    def test_execute_task_sync(self):
        engine = ExecutionEngine()
        task = Task.create(description="Deploy to production")
        result = engine.execute_task_sync(task)
        assert result.success is True

    @pytest.mark.asyncio
    async def test_get_result(self):
        engine = ExecutionEngine()
        task = Task.create(description="Store result")
        await engine.execute_task(task)
        result = engine.get_result(task.id)
        assert result is not None
        assert result.task_id == task.id

    @pytest.mark.asyncio
    async def test_get_all_results(self):
        engine = ExecutionEngine()
        t1 = Task.create(description="Deploy app")
        t2 = Task.create(description="Test app")
        await engine.execute_task(t1)
        await engine.execute_task(t2)
        results = engine.get_all_results()
        assert len(results) == 2

    @pytest.mark.asyncio
    async def test_execute_graph_sequential(self):
        engine = ExecutionEngine()
        graph = TaskGraph()
        t1 = Task.create(description="Design architecture")
        t2 = Task.create(description="Build components", depends_on=(t1.id,))
        t3 = Task.create(description="Test components", depends_on=(t2.id,))
        graph.add(t1)
        graph.add(t2)
        graph.add(t3)
        results = await engine.execute_graph(graph)
        assert len(results) == 3
        assert all(r.success for r in results.values())

    @pytest.mark.asyncio
    async def test_execute_graph_no_tasks(self):
        engine = ExecutionEngine()
        graph = TaskGraph()
        results = await engine.execute_graph(graph)
        assert results == {}

    def test_get_result_nonexistent(self):
        engine = ExecutionEngine()
        assert engine.get_result("nonexistent") is None

    def test_initial_results_empty(self):
        engine = ExecutionEngine()
        assert engine.get_all_results() == {}
