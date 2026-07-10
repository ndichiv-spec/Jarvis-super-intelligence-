from jarvis_planning.dependency_graph import DependencyGraph
from jarvis_planning.decomposer import Task
from jarvis_planning.events import EventBus
from jarvis_planning.executor import Executor
from jarvis_planning.scheduler import Scheduler


def _task(tid: str, deps: list[str] | None = None) -> Task:
    return Task(id=tid, title=tid, description="", dependencies=deps or [])


def _make_executor(tasks: list[Task]) -> Executor:
    g = DependencyGraph()
    g.add_tasks(tasks)
    s = Scheduler(g)
    eb = EventBus()
    ex = Executor(s, eb)
    return ex


class TestExecutor:
    def test_execute_next_with_ready_task(self) -> None:
        ex = _make_executor([_task("t1")])
        result = ex.execute_next()
        assert result is not None
        assert result.task_id == "t1"
        assert result.success is True

    def test_execute_all_tasks(self) -> None:
        ex = _make_executor([_task("t1"), _task("t2", ["t1"])])
        while not ex.is_complete():
            ex.execute_next()
        results = ex.get_all_results()
        assert len(results) == 2
        assert all(r.success for r in results.values())

    def test_execute_sequential(self) -> None:
        ex = _make_executor([_task("t1"), _task("t2", ["t1"]), _task("t3", ["t2"])])
        r1 = ex.execute_next()
        assert r1 is not None and r1.task_id == "t1"
        r2 = ex.execute_next()
        assert r2 is not None and r2.task_id == "t2"
        r3 = ex.execute_next()
        assert r3 is not None and r3.task_id == "t3"

    def test_no_ready_tasks_returns_none(self) -> None:
        ex = _make_executor([_task("t1")])
        ex._scheduler.mark_completed("t1")
        result = ex.execute_next()
        assert result is None

    def test_is_complete(self) -> None:
        ex = _make_executor([_task("t1")])
        assert ex.is_complete() is False
        ex.execute_next()
        assert ex.is_complete() is True

    def test_get_result(self) -> None:
        ex = _make_executor([_task("t1")])
        ex.execute_next()
        result = ex.get_result("t1")
        assert result is not None
        assert result.success is True

    def test_get_task_outputs(self) -> None:
        ex = _make_executor([_task("t1")])
        ex.execute_next()
        outputs = ex.get_task_outputs()
        assert "t1" in outputs

    def test_register_executor_func(self) -> None:
        ex = _make_executor([_task("t1")])
        ex.register_executor("__default__", lambda t, o: {"custom": "output"})
        result = ex.execute_next()
        assert result is not None
        assert result.outputs.get("custom") == "output"

    def test_plan_id(self) -> None:
        ex = _make_executor([_task("t1")])
        ex.set_plan_id("plan-123")
        assert ex._plan_id == "plan-123"

    def test_unknown_task(self) -> None:
        ex = _make_executor([])
        result = ex.execute_task("nonexistent")
        assert result.success is False
        assert "not found" in result.error

    def test_task_outputs_accumulate(self) -> None:
        ex = _make_executor([_task("t1"), _task("t2", ["t1"])])
        ex.execute_next()
        ex.execute_next()
        outputs = ex.get_task_outputs()
        assert "t1" in outputs
        assert "t2" in outputs

    def test_initial_results_empty(self) -> None:
        ex = _make_executor([_task("t1")])
        assert ex.get_all_results() == {}

    def test_initial_task_outputs_empty(self) -> None:
        ex = _make_executor([])
        assert ex.get_task_outputs() == {}
