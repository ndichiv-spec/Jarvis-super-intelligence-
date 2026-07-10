from jarvis_planning.dependency_graph import DependencyGraph
from jarvis_planning.decomposer import Task
from jarvis_planning.events import EventBus
from jarvis_planning.executor import Executor
from jarvis_planning.monitor import ProgressMonitor
from jarvis_planning.scheduler import Scheduler


def _task(tid: str, deps: list[str] | None = None, effort: float = 1.0) -> Task:
    return Task(id=tid, title=tid, description="", dependencies=deps or [], estimated_effort_hours=effort)


class TestProgressMonitor:
    def test_initial_progress(self) -> None:
        g = DependencyGraph()
        g.add_tasks([_task("t1"), _task("t2", ["t1"])])
        s = Scheduler(g)
        eb = EventBus()
        ex = Executor(s, eb)
        m = ProgressMonitor(s, ex, eb)
        m.start_monitoring("plan-1")
        p = m.get_progress()
        assert p.plan_id == "plan-1"
        assert p.total_tasks == 2
        assert p.completed_tasks == 0
        assert p.completion_percentage == 0.0

    def test_progress_after_execution(self) -> None:
        g = DependencyGraph()
        g.add_tasks([_task("t1", effort=1.0)])
        s = Scheduler(g)
        eb = EventBus()
        ex = Executor(s, eb)
        m = ProgressMonitor(s, ex, eb)
        m.start_monitoring("plan-1")
        ex.execute_next()
        p = m.get_progress()
        assert p.completed_tasks == 1
        assert p.completion_percentage == 100.0

    def test_partial_progress(self) -> None:
        g = DependencyGraph()
        g.add_tasks([_task("t1", effort=1.0), _task("t2", ["t1"], effort=2.0)])
        s = Scheduler(g)
        eb = EventBus()
        ex = Executor(s, eb)
        m = ProgressMonitor(s, ex, eb)
        m.start_monitoring("plan-1")
        ex.execute_next()
        p = m.get_progress()
        assert p.completed_tasks == 1
        assert p.running_tasks == 0
        assert 0 < p.completion_percentage < 100

    def test_progress_to_dict(self) -> None:
        g = DependencyGraph()
        g.add_tasks([_task("t1")])
        s = Scheduler(g)
        eb = EventBus()
        ex = Executor(s, eb)
        m = ProgressMonitor(s, ex, eb)
        m.start_monitoring("plan-1")
        p = m.get_progress()
        d = p.to_dict()
        assert d["plan_id"] == "plan-1"
        assert "total_tasks" in d
        assert "completion_percentage" in d

    def test_get_summary(self) -> None:
        g = DependencyGraph()
        g.add_tasks([_task("t1")])
        s = Scheduler(g)
        eb = EventBus()
        ex = Executor(s, eb)
        m = ProgressMonitor(s, ex, eb)
        m.start_monitoring("plan-1")
        summary = m.get_summary()
        assert "plan_id" in summary
        assert "progress" in summary
        assert "events" in summary

    def test_last_event_tracks_progress(self) -> None:
        g = DependencyGraph()
        g.add_tasks([_task("t1")])
        s = Scheduler(g)
        eb = EventBus()
        ex = Executor(s, eb)
        m = ProgressMonitor(s, ex, eb)
        m.start_monitoring("plan-1")
        ex.execute_next()
        p = m.get_progress()
        assert "completed" in p.last_event
