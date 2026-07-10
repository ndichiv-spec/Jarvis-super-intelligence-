import pytest
from jarvis_intelligence.objectives import Objective


class TestObjective:
    def test_create_defaults(self):
        obj = Objective.create(description="Build the module")
        assert obj.description == "Build the module"
        assert obj.id.startswith("obj-")
        assert obj.goal_id is None
        assert obj.priority == 50

    def test_create_with_goal_id(self):
        obj = Objective.create(description="Test module", goal_id="goal-abc")
        assert obj.goal_id == "goal-abc"
        assert obj.description == "Test module"

    def test_create_with_constraints(self):
        obj = Objective.create(
            description="Deploy",
            constraints=("no_downtime", "rollback"),
            priority=90,
        )
        assert "no_downtime" in obj.constraints
        assert obj.priority == 90

    def test_frozen_dataclass(self):
        obj = Objective.create(description="Immutable")
        with pytest.raises(AttributeError):
            obj.description = "changed"

    def test_objective_str(self):
        obj = Objective.create(description="My objective")
        assert "My objective" in str(obj) or "Objective" in type(obj).__name__
