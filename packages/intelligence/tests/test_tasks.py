import pytest
from jarvis_intelligence.tasks import Task, TaskGraph, TaskState


class TestTask:
    def test_create_defaults(self):
        task = Task.create(description="Do something")
        assert task.description == "Do something"
        assert task.state == TaskState.PENDING
        assert task.priority == 50
        assert task.max_retries == 3
        assert task.id.startswith("task-")

    def test_create_with_params(self):
        task = Task.create(
            description="Build feature X",
            depends_on=("task-abc",),
            required_capabilities=("python", "testing"),
            priority=90,
            max_retries=5,
            timeout_seconds=300,
        )
        assert "task-abc" in task.depends_on
        assert "python" in task.required_capabilities
        assert task.priority == 90
        assert task.max_retries == 5
        assert task.timeout_seconds == 300

    def test_frozen_dataclass(self):
        task = Task.create(description="Immutable")
        with pytest.raises(AttributeError):
            task.description = "changed"  # type: ignore[misc]


class TestTaskGraph:
    def test_add_and_get(self):
        g = TaskGraph()
        task = Task.create(description="Test")
        g.add(task)
        assert g.get(task.id) is task

    def test_get_nonexistent(self):
        g = TaskGraph()
        assert g.get("nonexistent") is None

    def test_update(self):
        g = TaskGraph()
        task = Task.create(description="Initial")
        g.add(task)
        updated = g.update(task.id, description="Updated", state=TaskState.RUNNING)
        assert updated is not None
        assert updated.description == "Updated"
        assert updated.state == TaskState.RUNNING

    def test_update_nonexistent(self):
        g = TaskGraph()
        assert g.update("nonexistent", state=TaskState.COMPLETED) is None

    def test_get_ready_tasks_no_deps(self):
        g = TaskGraph()
        t1 = Task.create(description="A")
        t2 = Task.create(description="B")
        g.add(t1)
        g.add(t2)
        ready = g.get_ready_tasks()
        assert len(ready) == 2

    def test_get_ready_tasks_with_deps(self):
        g = TaskGraph()
        t1 = Task.create(description="Root")
        t2 = Task.create(description="Child", depends_on=(t1.id,))
        g.add(t1)
        g.add(t2)
        ready = g.get_ready_tasks()
        assert len(ready) == 1
        assert ready[0].id == t1.id

    def test_get_ready_tasks_deps_met(self):
        g = TaskGraph()
        t1 = Task.create(description="Root")
        t2 = Task.create(description="Child", depends_on=(t1.id,))
        g.add(t1)
        g.add(t2)
        g.update(t1.id, state=TaskState.COMPLETED)
        ready = g.get_ready_tasks()
        assert len(ready) == 1
        assert ready[0].id == t2.id

    def test_get_ready_tasks_priority_order(self):
        g = TaskGraph()
        t1 = Task.create(description="Low", priority=10)
        t2 = Task.create(description="High", priority=100)
        g.add(t1)
        g.add(t2)
        ready = g.get_ready_tasks()
        assert ready[0].id == t2.id
        assert ready[1].id == t1.id

    def test_get_by_state(self):
        g = TaskGraph()
        t1 = Task.create(description="A")
        t2 = Task.create(description="B")
        g.add(t1)
        g.add(t2)
        g.update(t1.id, state=TaskState.RUNNING)
        running = g.get_by_state(TaskState.RUNNING)
        assert len(running) == 1
        assert running[0].id == t1.id
        pending = g.get_by_state(TaskState.PENDING)
        assert len(pending) == 1
        assert pending[0].id == t2.id

    def test_all(self):
        g = TaskGraph()
        assert g.all() == []
        g.add(Task.create(description="A"))
        g.add(Task.create(description="B"))
        assert len(g.all()) == 2

    def test_topological_sort_simple(self):
        g = TaskGraph()
        t1 = Task.create(description="First")
        t2 = Task.create(description="Second", depends_on=(t1.id,))
        g.add(t1)
        g.add(t2)
        order = g.topological_sort()
        assert len(order) == 2
        assert order[0].id == t1.id
        assert order[1].id == t2.id

    def test_topological_sort_complex(self):
        g = TaskGraph()
        t1 = Task.create(description="A")
        t2 = Task.create(description="B", depends_on=(t1.id,))
        t3 = Task.create(description="C", depends_on=(t1.id,))
        t4 = Task.create(description="D", depends_on=(t2.id, t3.id))
        g.add(t1)
        g.add(t2)
        g.add(t3)
        g.add(t4)
        order = g.topological_sort()
        assert len(order) == 4
        assert order[0].id == t1.id
        assert order[-1].id == t4.id
