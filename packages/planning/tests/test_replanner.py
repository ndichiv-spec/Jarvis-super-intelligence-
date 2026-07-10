from jarvis_planning.dependency_graph import DependencyGraph
from jarvis_planning.decomposer import Task
from jarvis_planning.events import EventBus
from jarvis_planning.executor import Executor
from jarvis_planning.monitor import ProgressMonitor
from jarvis_planning.replanner import Replanner
from jarvis_planning.scheduler import Scheduler
from jarvis_planning.state_machine import TaskState


def _task(tid: str, deps: list[str] | None = None, priority: int = 0) -> Task:
    return Task(id=tid, title=tid, description="", dependencies=deps or [], priority=priority)


def _make_replanner(tasks: list[Task]) -> Replanner:
    g = DependencyGraph()
    g.add_tasks(tasks)
    s = Scheduler(g)
    eb = EventBus()
    ex = Executor(s, eb)
    m = ProgressMonitor(s, ex, eb)
    r = Replanner(s, ex, m, eb)
    r.set_plan_id("plan-1")
    return r


class TestReplanner:
    def test_task_failure_blocks_dependents(self) -> None:
        r = _make_replanner([_task("t1"), _task("t2", ["t1"])])
        r._scheduler.mark_failed("t1")
        result = r.replan("task_failure", {"task_id": "t1"})
        assert "t1" in result.changed_tasks
        assert r._scheduler.get_state("t2") == TaskState.BLOCKED

    def test_task_failure_with_alternative(self) -> None:
        r = _make_replanner([_task("t1")])
        result = r.replan("task_failure", {"task_id": "t1", "alternative": "retry"})
        assert len(result.new_tasks) == 1
        assert "replacement-" in result.new_tasks[0]

    def test_dependency_change_removed(self) -> None:
        r = _make_replanner([_task("t1"), _task("t2", ["t1"])])
        r._scheduler.mark_blocked("t2")
        result = r.replan("dependency_change", {
            "affected_tasks": ["t2"],
            "dependency_removed": True,
        })
        assert r._scheduler.get_state("t2") == TaskState.READY

    def test_dependency_change_added(self) -> None:
        r = _make_replanner([_task("t1"), _task("t2", ["t1"])])
        r._scheduler.mark_ready("t2")
        result = r.replan("dependency_change", {
            "affected_tasks": ["t2"],
            "dependency_removed": False,
        })
        assert r._scheduler.get_state("t2") == TaskState.BLOCKED

    def test_agent_unavailable(self) -> None:
        r = _make_replanner([_task("t1")])
        result = r.replan("agent_unavailable", {"task_id": "t1"})
        assert "t1" in result.reassigned_tasks

    def test_requirement_change(self) -> None:
        r = _make_replanner([_task("t1", priority=1), _task("backend-dev", priority=2)])
        r._scheduler.mark_running("t1")
        result = r.replan("requirement_change", {"changed_areas": ["backend"]})
        assert "backend-dev" in result.changed_tasks

    def test_timeout(self) -> None:
        r = _make_replanner([_task("t1"), _task("t2", priority=5)])
        result = r.replan("timeout", {"task_id": "t1"})
        assert "t1" in result.changed_tasks

    def test_has_changes_true(self) -> None:
        r = _make_replanner([_task("t1")])
        result = r.replan("task_failure", {"task_id": "t1"})
        assert result.has_changes is True

    def test_has_changes_false(self) -> None:
        r = _make_replanner([_task("t1")])
        result = r.replan("unknown_trigger", {})
        assert result.has_changes is False

    def test_generic_handler(self) -> None:
        r = _make_replanner([_task("t1")])
        result = r.replan("generic_change", {"task_id": "t1"})
        assert result.has_changes is False

    def test_get_triggers(self) -> None:
        r = _make_replanner([])
        triggers = r.get_triggers()
        assert "task_failure" in triggers
        assert "dependency_change" in triggers
        assert "agent_unavailable" in triggers
