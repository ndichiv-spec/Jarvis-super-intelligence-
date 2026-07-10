from jarvis_planning.dependency_graph import DependencyGraph
from jarvis_planning.decomposer import Task
from jarvis_planning.policies import ExecutionPolicy
from jarvis_planning.scheduler import Scheduler
from jarvis_planning.state_machine import TaskState


def _task(tid: str, deps: list[str] | None = None, priority: int = 0, effort: float = 1.0) -> Task:
    return Task(id=tid, title=tid, description="", dependencies=deps or [],
                priority=priority, estimated_effort_hours=effort)


def _graph(tasks: list[Task]) -> DependencyGraph:
    g = DependencyGraph()
    g.add_tasks(tasks)
    return g


class TestScheduler:
    def test_all_ready(self) -> None:
        g = _graph([_task("t1"), _task("t2")])
        s = Scheduler(g)
        result = s.schedule()
        assert len(result.ready_queue) == 2
        assert len(result.completed_tasks) == 0
        assert len(result.waiting_tasks) == 0

    def test_dependency_waiting(self) -> None:
        g = _graph([_task("t1"), _task("t2", ["t1"])])
        s = Scheduler(g)
        result = s.schedule()
        assert "t1" in result.ready_queue
        assert "t2" in result.waiting_tasks

    def test_completed_not_in_ready(self) -> None:
        g = _graph([_task("t1"), _task("t2", ["t1"])])
        s = Scheduler(g)
        s.mark_completed("t1")
        result = s.schedule()
        assert "t1" in result.completed_tasks
        assert "t2" in result.ready_queue

    def test_blocked_on_failed(self) -> None:
        g = _graph([_task("t1"), _task("t2", ["t1"])])
        s = Scheduler(g)
        s.mark_failed("t1")
        result = s.schedule()
        assert "t2" in result.blocked_tasks

    def test_running_not_requeued(self) -> None:
        g = _graph([_task("t1")])
        s = Scheduler(g)
        s.mark_running("t1")
        result = s.schedule()
        assert "t1" in result.running_tasks

    def test_priority_sorting(self) -> None:
        g = _graph([_task("low", priority=1), _task("high", priority=10)])
        s = Scheduler(g)
        result = s.schedule()
        assert result.ready_queue == ["high", "low"]

    def test_max_concurrent(self) -> None:
        policy = ExecutionPolicy(max_concurrent_tasks=1)
        g = _graph([_task("t1"), _task("t2")])
        s = Scheduler(g, policy)
        s.mark_running("t1")
        result = s.schedule()
        assert len(result.ready_queue) <= 1

    def test_mark_ready(self) -> None:
        g = _graph([_task("t1")])
        s = Scheduler(g)
        s.mark_ready("t1")
        assert s.get_state("t1") == TaskState.READY

    def test_get_task_summary(self) -> None:
        g = _graph([_task("t1"), _task("t2", ["t1"])])
        s = Scheduler(g)
        s.mark_completed("t1")
        summary = s.get_task_summary()
        assert summary["t1"] == "COMPLETED"
        assert summary["t2"] == "PLANNED"

    def test_get_available_capacity(self) -> None:
        policy = ExecutionPolicy(max_concurrent_tasks=5)
        g = _graph([_task("t1"), _task("t2")])
        s = Scheduler(g, policy)
        assert s.get_available_capacity() == 5
        s.mark_running("t1")
        assert s.get_available_capacity() == 4

    def test_unlimited_capacity(self) -> None:
        policy = ExecutionPolicy(max_concurrent_tasks=0)
        g = _graph([_task("t1")])
        s = Scheduler(g, policy)
        assert s.get_available_capacity() == 999

    def test_get_ready_tasks(self) -> None:
        g = _graph([_task("t1"), _task("t2")])
        s = Scheduler(g)
        ready = s.get_ready_tasks(max_tasks=1)
        assert len(ready) == 1

    def test_schedule_to_dict(self) -> None:
        g = _graph([_task("t1")])
        s = Scheduler(g)
        d = s.to_dict()
        assert "task_states" in d
        assert "schedule" in d
        assert "policy" in d
