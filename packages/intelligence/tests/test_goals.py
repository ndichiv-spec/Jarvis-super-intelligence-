import pytest
from datetime import UTC, datetime, timedelta
from jarvis_intelligence.goals import Goal, GoalManager, GoalState, GoalPriority


class TestGoal:
    def test_create_defaults(self):
        goal = Goal.create(description="Build the platform")
        assert goal.description == "Build the platform"
        assert goal.priority == GoalPriority.MEDIUM
        assert goal.state == GoalState.DRAFT
        assert goal.owner == "system"
        assert goal.id.startswith("goal-")

    def test_create_with_all_params(self):
        deadline = datetime.now(UTC) + timedelta(days=7)
        goal = Goal.create(
            description="Deploy to production",
            priority=GoalPriority.HIGH,
            constraints=("no_downtime", "rollback_plan"),
            success_criteria=("all_tests_pass", "latency_under_200ms"),
            dependencies=("goal-abc",),
            deadline=deadline,
            required_capabilities=("devops", "networking"),
            owner="alice",
            workspace_id="prod-1",
            parent_goal_id="goal-parent",
        )
        assert goal.priority == GoalPriority.HIGH
        assert "no_downtime" in goal.constraints
        assert goal.owner == "alice"
        assert goal.workspace_id == "prod-1"

    def test_is_overdue_no_deadline(self):
        goal = Goal.create(description="No deadline")
        assert goal.is_overdue() is False

    def test_is_overdue_past_deadline(self):
        past = datetime.now(UTC) - timedelta(hours=1)
        goal = Goal.create(description="Overdue", deadline=past)
        assert goal.is_overdue() is True

    def test_remaining_time_no_deadline(self):
        goal = Goal.create(description="No deadline")
        assert goal.remaining_time() is None

    def test_remaining_time_future(self):
        future = datetime.now(UTC) + timedelta(days=3)
        goal = Goal.create(description="Future", deadline=future)
        rt = goal.remaining_time()
        assert rt is not None
        assert rt.total_seconds() > 0

    def test_frozen_dataclass(self):
        goal = Goal.create(description="Immutable")
        with pytest.raises(AttributeError):
            goal.description = "changed"  # type: ignore[misc]


class TestGoalManager:
    def test_add_and_get(self):
        mgr = GoalManager()
        goal = Goal.create(description="Test")
        mgr.add(goal)
        assert mgr.get(goal.id) is goal

    def test_get_nonexistent(self):
        mgr = GoalManager()
        assert mgr.get("nonexistent") is None

    def test_update(self):
        mgr = GoalManager()
        goal = Goal.create(description="Old description")
        mgr.add(goal)
        updated = mgr.update(goal.id, description="New description", state=GoalState.ACTIVE)
        assert updated is not None
        assert updated.description == "New description"
        assert updated.state == GoalState.ACTIVE

    def test_update_nonexistent(self):
        mgr = GoalManager()
        assert mgr.update("nonexistent", state=GoalState.ACTIVE) is None

    def test_list_all(self):
        mgr = GoalManager()
        g1 = Goal.create(description="A", priority=GoalPriority.LOW)
        g2 = Goal.create(description="B", priority=GoalPriority.HIGH)
        mgr.add(g1)
        mgr.add(g2)
        assert len(mgr.list()) == 2

    def test_list_filter_by_state(self):
        mgr = GoalManager()
        g1 = Goal.create(description="Draft")
        g2 = Goal.create(description="Active")
        mgr.add(g1)
        mgr.add(g2)
        mgr.update(g2.id, state=GoalState.ACTIVE)
        active = mgr.list(state=GoalState.ACTIVE)
        assert len(active) == 1
        assert active[0].id == g2.id

    def test_remove(self):
        mgr = GoalManager()
        goal = Goal.create(description="Remove me")
        mgr.add(goal)
        assert mgr.remove(goal.id) is True
        assert mgr.get(goal.id) is None

    def test_remove_nonexistent(self):
        mgr = GoalManager()
        assert mgr.remove("nonexistent") is False

    def test_count(self):
        mgr = GoalManager()
        assert mgr.count() == 0
        mgr.add(Goal.create(description="A"))
        mgr.add(Goal.create(description="B"))
        assert mgr.count() == 2
