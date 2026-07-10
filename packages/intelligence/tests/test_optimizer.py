from jarvis_intelligence.optimizer import OptimizerEngine, OptimizationSuggestion
from jarvis_intelligence.tasks import Task, TaskGraph, TaskState
from jarvis_intelligence.evaluator import EvaluationResult


class TestOptimizerEngine:
    def test_optimize_task_order_no_suggestions(self):
        engine = OptimizerEngine()
        graph = TaskGraph()
        task = Task.create(description="Simple task")
        graph.add(task)
        suggestions = engine.optimize_task_order(graph)
        assert len(suggestions) == 0

    def test_optimize_task_order_many_deps(self):
        engine = OptimizerEngine()
        graph = TaskGraph()
        task = Task.create(description="Complex", depends_on=("a", "b", "c", "d"))
        graph.add(task)
        suggestions = engine.optimize_task_order(graph)
        assert len(suggestions) > 0
        assert suggestions[0].type == "dependency"

    def test_optimize_agent_selection_low_quality(self):
        engine = OptimizerEngine()
        eval_result = EvaluationResult(
            task_id="t1", success=False, quality_score=0.3,
            efficiency_score=0.5, confidence=0.4,
        )
        suggestions = engine.optimize_agent_selection(eval_result)
        assert len(suggestions) > 0
        assert suggestions[0].type == "agent"

    def test_optimize_agent_selection_good_quality(self):
        engine = OptimizerEngine()
        eval_result = EvaluationResult(
            task_id="t1", success=True, quality_score=0.9,
            efficiency_score=0.85, confidence=0.88,
        )
        suggestions = engine.optimize_agent_selection(eval_result)
        assert len(suggestions) == 0

    def test_optimize_retry_strategy_failed(self):
        engine = OptimizerEngine()
        task = Task.create(description="Failed task", max_retries=3)
        task_with_state = Task(
            id=task.id, description=task.description,
            state=TaskState.FAILED, retry_count=3, max_retries=3,
        )
        suggestion = engine.optimize_retry_strategy(task_with_state)
        assert suggestion is not None
        assert suggestion.type == "retry"

    def test_optimize_retry_strategy_not_failed(self):
        engine = OptimizerEngine()
        task = Task.create(description="Pending task")
        suggestion = engine.optimize_retry_strategy(task)
        assert suggestion is None

    def test_get_all_suggestions_accumulates(self):
        engine = OptimizerEngine()
        assert engine.get_all_suggestions() == []
        graph = TaskGraph()
        graph.add(Task.create(description="Complex", depends_on=("a", "b", "c", "d")))
        engine.optimize_task_order(graph)
        assert len(engine.get_all_suggestions()) > 0

    def test_optimization_suggestion_dataclass(self):
        s = OptimizationSuggestion(
            type="test", description="Test suggestion",
            impact="high", effort="low", target_id="t1",
        )
        assert s.type == "test"
        assert s.impact == "high"
        assert s.target_id == "t1"
