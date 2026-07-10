from datetime import UTC, datetime
from jarvis_intelligence.context import ContextManager, ExecutionContext


class TestContextManager:
    def test_create_default(self):
        mgr = ContextManager()
        ctx = mgr.create()
        assert isinstance(ctx, ExecutionContext)
        assert ctx.workspace_id == "default"

    def test_create_with_context(self):
        mgr = ContextManager()
        initial = ExecutionContext(goal_id="g1", plan_id="p1", user_id="u1")
        ctx = mgr.create(initial)
        assert ctx.goal_id == "g1"
        assert ctx.plan_id == "p1"
        assert ctx.user_id == "u1"

    def test_get_context(self):
        mgr = ContextManager()
        created = mgr.create()
        ctx_id = f"ctx-{id(created)}"
        fetched = mgr.get(ctx_id)
        assert fetched is created

    def test_get_nonexistent(self):
        mgr = ContextManager()
        assert mgr.get("nonexistent") is None

    def test_update(self):
        mgr = ContextManager()
        ctx = mgr.create()
        mgr.update(ctx)

    def test_push_reasoning(self):
        mgr = ContextManager()
        ctx = mgr.create()
        mgr.push_reasoning(ctx, "analysis", "Analyzed the problem", 0.85)
        assert len(ctx.reasoning_history) == 1
        entry = ctx.reasoning_history[0]
        assert entry["stage"] == "analysis"
        assert entry["reasoning"] == "Analyzed the problem"
        assert entry["confidence"] == 0.85

    def test_push_reasoning_multiple(self):
        mgr = ContextManager()
        ctx = mgr.create()
        mgr.push_reasoning(ctx, "step1", "First step", 0.9)
        mgr.push_reasoning(ctx, "step2", "Second step", 0.8)
        assert len(ctx.reasoning_history) == 2

    def test_push_execution(self):
        mgr = ContextManager()
        ctx = mgr.create()
        mgr.push_execution(ctx, "build", "completed", {"files": 10})
        assert len(ctx.execution_history) == 1
        entry = ctx.execution_history[0]
        assert entry["action"] == "build"
        assert entry["status"] == "completed"

    def test_push_execution_without_details(self):
        mgr = ContextManager()
        ctx = mgr.create()
        mgr.push_execution(ctx, "deploy", "started")
        assert len(ctx.execution_history) == 1
        assert ctx.execution_history[0]["details"] == {}

    def test_execution_context_defaults(self):
        ctx = ExecutionContext()
        assert ctx.reasoning_history == []
        assert ctx.memory_references == []
        assert ctx.active_goals == []
        assert ctx.metadata == {}
        assert ctx.created_at is not None

    def test_execution_context_with_values(self):
        now = datetime.now(UTC)
        ctx = ExecutionContext(
            goal_id="g1",
            session_id="s1",
            workspace_id="workspace-1",
            active_goals=["g1", "g2"],
            memory_references=["mem1"],
            created_at=now,
        )
        assert ctx.session_id == "s1"
        assert ctx.workspace_id == "workspace-1"
        assert len(ctx.active_goals) == 2
        assert ctx.created_at == now
