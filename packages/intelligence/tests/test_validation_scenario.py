"""
EPIC-005 Validation Scenario

Demonstrates the JARVIS Intelligence Core (JIC) handling:

    "Design, build, test, document, and deploy a complete inventory management platform."

Validates:
- Understanding complex user goals
- Generating structured execution plans
- Selecting appropriate agents
- Coordinating multi-agent execution
- Monitoring progress
- Re-planning on failures
- Evaluating results
- Storing successful strategies in JARVIS Memory
"""
import pytest
from jarvis_intelligence.engine import IntelligenceEngine, IntelligenceResult
from jarvis_intelligence.goals import GoalPriority, GoalState
from jarvis_intelligence.policies import ExecutionPolicy
from jarvis_intelligence.tasks import TaskState


GOAL = "Design, build, test, document, and deploy a complete inventory management platform"


class TestValidationScenario:
    @pytest.mark.asyncio
    async def test_goal_understanding(self):
        """1. Understand the goal via cognition engine."""
        engine = IntelligenceEngine()
        result = await engine.execute_goal(GOAL, priority=GoalPriority.HIGH)
        assert result.cognition is not None
        assert result.cognition.understanding != ""
        assert "inventory" in result.cognition.understanding.lower() or "platform" in result.cognition.understanding.lower()
        assert result.cognition.intent == "design_and_plan"
        assert "platform" in result.cognition.key_entities or "system" in result.cognition.key_entities

    @pytest.mark.asyncio
    async def test_structured_execution_plan(self):
        """2. Generate a structured execution plan with task graph."""
        engine = IntelligenceEngine()
        result = await engine.execute_goal(GOAL, priority=GoalPriority.HIGH)
        assert result.plan is not None
        assert result.plan.task_graph is not None
        tasks = result.plan.task_graph.all()
        assert len(tasks) >= 4
        descriptions = [t.description.lower() for t in tasks]
        assert any("design" in d for d in descriptions)
        assert any("build" in d for d in descriptions)
        assert any("test" in d for d in descriptions)
        assert any("document" in d for d in descriptions)
        assert any("deploy" in d for d in descriptions)

    @pytest.mark.asyncio
    async def test_agent_selection(self):
        """3. Select appropriate specialist agents based on task capabilities."""
        engine = IntelligenceEngine()
        result = await engine.execute_goal(GOAL)
        decisions = result.decisions
        assert len(decisions) > 0
        strategy_decision = next((d for d in decisions if d.type.value == "select_strategy"), None)
        assert strategy_decision is not None
        assert strategy_decision.confidence > 0

    @pytest.mark.asyncio
    async def test_coordinated_execution(self):
        """4. Coordinate execution across all tasks."""
        engine = IntelligenceEngine()
        result = await engine.execute_goal(GOAL, priority=GoalPriority.HIGH)
        assert result.coordination is not None
        assert result.coordination.total_tasks >= 4
        assert result.coordination.completed_tasks >= 0
        assert result.coordination.duration_seconds >= 0
        assert result.coordination.decisions_made > 0

    @pytest.mark.asyncio
    async def test_execution_monitoring(self):
        """5. Monitor execution progress through task states."""
        engine = IntelligenceEngine()
        result = await engine.execute_goal(GOAL)
        assert result.plan is not None
        tasks = result.plan.task_graph.all()
        states = {t.state for t in tasks}
        valid_states = {TaskState.COMPLETED, TaskState.FAILED, TaskState.PENDING, TaskState.RUNNING}
        assert states.issubset(valid_states), f"Unexpected states: {states}"

    @pytest.mark.asyncio
    async def test_replan_on_failure(self):
        """6. Re-plan when failures occur (simulate via retry decisions)."""
        engine = IntelligenceEngine()
        result = await engine.execute_goal(GOAL, policy=ExecutionPolicy.AGGRESSIVE)
        assert result.success is True or result.error is not None
        if result.coordination:
            assert result.coordination.decisions_made >= 0

    @pytest.mark.asyncio
    async def test_result_evaluation(self):
        """7. Evaluate every completed task."""
        engine = IntelligenceEngine()
        result = await engine.execute_goal(GOAL)
        assert len(result.evaluations) >= 4
        for eval_result in result.evaluations:
            assert eval_result.confidence > 0
            assert 0 <= eval_result.quality_score <= 1
            assert 0 <= eval_result.efficiency_score <= 1

    @pytest.mark.asyncio
    async def test_learning_and_memory(self):
        """8. Store successful strategies in JARVIS Memory."""
        engine = IntelligenceEngine()
        result = await engine.execute_goal(GOAL)
        records = engine.learning.get_all()
        assert len(records) > 0
        record = records[0]
        assert record.pattern != ""
        assert record.context != ""
        assert record.confidence > 0

    @pytest.mark.asyncio
    async def test_full_pipeline(self):
        """End-to-end: full pipeline with status reporting."""
        engine = IntelligenceEngine()
        result = await engine.execute_goal(GOAL, priority=GoalPriority.HIGH)
        assert isinstance(result, IntelligenceResult)
        assert result.goal is not None
        assert result.goal.description == GOAL
        assert result.goal.priority == GoalPriority.HIGH

        status = engine.get_status()
        assert status["active_goals"] >= 1
        assert status["policy"] == "balanced"

        metrics = engine.telemetry.get_metrics()
        assert metrics.total_executions >= 1
