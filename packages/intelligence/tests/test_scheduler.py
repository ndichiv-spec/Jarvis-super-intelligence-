from datetime import UTC, datetime, timedelta
from jarvis_intelligence.scheduler import SchedulerEngine, ScheduledTask
from jarvis_intelligence.tasks import Task, TaskState


class TestSchedulerEngine:
    def test_schedule_once(self):
        engine = SchedulerEngine()
        task = Task.create(description="One-time task")
        st = engine.schedule(task)
        assert isinstance(st, ScheduledTask)
        assert st.is_recurring is False
        assert st.interval_seconds is None
        assert st.id.startswith("sched-")

    def test_schedule_recurring(self):
        engine = SchedulerEngine()
        task = Task.create(description="Recurring task")
        st = engine.schedule(task, interval_seconds=3600)
        assert st.is_recurring is True
        assert st.interval_seconds == 3600

    def test_get_due_empty(self):
        engine = SchedulerEngine()
        assert engine.get_due() == []

    def test_get_due_with_scheduled(self):
        engine = SchedulerEngine()
        task = Task.create(description="Due task")
        engine.schedule(task)
        due = engine.get_due()
        assert len(due) == 1
        assert due[0].task.id == task.id

    def test_get_due_excludes_running(self):
        engine = SchedulerEngine()
        task = Task.create(description="Running task")
        running_task = Task(
            id=task.id, description=task.description,
            state=TaskState.RUNNING,
        )
        engine.schedule(running_task)
        due = engine.get_due()
        assert len(due) == 0

    def test_mark_completed(self):
        engine = SchedulerEngine()
        task = Task.create(description="Complete me")
        st = engine.schedule(task)
        engine.mark_completed(st.id)
        updated = engine.list_scheduled()[0]
        assert updated.last_run is not None
        assert updated.next_run is None

    def test_mark_completed_recurring(self):
        engine = SchedulerEngine()
        task = Task.create(description="Recurring")
        st = engine.schedule(task, interval_seconds=60)
        engine.mark_completed(st.id)
        updated = engine.list_scheduled()[0]
        assert updated.last_run is not None
        assert updated.next_run is not None
        assert updated.next_run > updated.last_run

    def test_mark_completed_nonexistent(self):
        engine = SchedulerEngine()
        engine.mark_completed("nonexistent")

    def test_list_scheduled(self):
        engine = SchedulerEngine()
        assert engine.list_scheduled() == []
        engine.schedule(Task.create(description="A"))
        engine.schedule(Task.create(description="B"))
        assert len(engine.list_scheduled()) == 2

    def test_scheduled_task_dataclass(self):
        task = Task.create(description="Test")
        now = datetime.now(UTC)
        st = ScheduledTask(
            id="s1", task=task, scheduled_at=now,
            interval_seconds=300.0, is_recurring=True,
            next_run=now + timedelta(seconds=300),
        )
        assert st.id == "s1"
        assert st.interval_seconds == 300.0
        assert st.is_recurring is True
