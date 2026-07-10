import pytest
from jarvis_intelligence.engine import IntelligenceEngine, IntelligenceResult
from jarvis_intelligence.goals import GoalPriority
from jarvis_intelligence.policies import ExecutionPolicy


class TestIntelligenceEngine:
    @pytest.mark.asyncio
    async def test_execute_goal_success(self):
        engine = IntelligenceEngine()
        result = await engine.execute_goal("Design and build a dashboard")
        assert isinstance(result, IntelligenceResult)
        assert result.success is True
        assert result.goal is not None
        assert result.plan is not None
        assert result.cognition is not None
        assert result.reasoning is not None
        assert len(result.decisions) > 0
        assert result.coordination is not None
        assert len(result.evaluations) > 0

    @pytest.mark.asyncio
    async def test_execute_goal_with_priority_and_policy(self):
        engine = IntelligenceEngine()
        result = await engine.execute_goal(
            "Deploy the application to staging",
            priority=GoalPriority.HIGH,
            policy=ExecutionPolicy.CONSERVATIVE,
        )
        assert result.success is True

    @pytest.mark.asyncio
    async def test_execute_goal_with_context(self):
        engine = IntelligenceEngine()
        result = await engine.execute_goal(
            "Test the API endpoints",
            context={"deadline": "2026-08-01", "env": "staging"},
        )
        assert result.success is True

    def test_get_status(self):
        engine = IntelligenceEngine()
        status = engine.get_status()
        assert "active_goals" in status
        assert "active_plans" in status
        assert "policy" in status
        assert "total_learned" in status
        assert status["policy"] == "balanced"

    @pytest.mark.asyncio
    async def test_execute_goal(self):
        engine = IntelligenceEngine()
        result = await engine.execute_goal("Build a simple feature")
        assert result.success is True
        assert result.goal is not None
        assert len(result.evaluations) > 0

    @pytest.mark.asyncio
    async def test_multiple_executions(self):
        engine = IntelligenceEngine()
        r1 = await engine.execute_goal("Build module A")
        r2 = await engine.execute_goal("Build module B")
        assert r1.success is True
        assert r2.success is True
        status = engine.get_status()
        assert status["active_goals"] >= 2

    @pytest.mark.asyncio
    async def test_learning_from_execution(self):
        engine = IntelligenceEngine()
        await engine.execute_goal("Create a report generator")
        assert len(engine.learning.get_all()) > 0

    def test_properties(self):
        engine = IntelligenceEngine()
        assert engine.goal_manager is not None
        assert engine.planner is not None
        assert engine.coordinator is not None
        assert engine.telemetry is not None
        assert engine.learning is not None
        assert engine.policy is not None
        assert engine.safety is not None
        assert engine.context_manager is not None
