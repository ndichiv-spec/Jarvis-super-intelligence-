from jarvis_intelligence.evaluator import EvaluationEngine, EvaluationResult
from jarvis_intelligence.tasks import TaskState


class TestEvaluationEngine:
    def test_evaluate_success(self):
        engine = EvaluationEngine()
        result = engine.evaluate(
            "Build the module",
            result={"duration_seconds": 2.5, "errors": []},
            state=TaskState.COMPLETED,
        )
        assert result.success is True
        assert result.confidence > 0.5

    def test_evaluate_failure(self):
        engine = EvaluationEngine()
        result = engine.evaluate(
            "Build the module",
            result={"duration_seconds": 10, "errors": ["timeout"]},
            state=TaskState.FAILED,
        )
        assert result.success is False
        assert result.quality_score == 0.0

    def test_evaluate_no_result(self):
        engine = EvaluationEngine()
        result = engine.evaluate("Simple task")
        assert result.success is True
        assert result.quality_score == 0.7
        assert result.efficiency_score == 0.7

    def test_quality_with_errors(self):
        engine = EvaluationEngine()
        result = engine.evaluate(
            "Task with errors",
            result={"errors": ["err1", "err2", "err3", "err4"], "warnings": ["w1"]},
            state=TaskState.COMPLETED,
        )
        assert result.quality_score < 1.0
        assert result.quality_score >= 0.1

    def test_efficiency_duration_under_1s(self):
        engine = EvaluationEngine()
        result = engine.evaluate(
            "Fast task",
            result={"duration_seconds": 0.5},
            state=TaskState.COMPLETED,
        )
        assert result.efficiency_score == 1.0

    def test_efficiency_duration_under_5s(self):
        engine = EvaluationEngine()
        result = engine.evaluate(
            "Moderate task",
            result={"duration_seconds": 3},
            state=TaskState.COMPLETED,
        )
        assert result.efficiency_score == 0.9

    def test_efficiency_duration_under_30s(self):
        engine = EvaluationEngine()
        result = engine.evaluate(
            "Slow task",
            result={"duration_seconds": 15},
            state=TaskState.COMPLETED,
        )
        assert result.efficiency_score == 0.7

    def test_efficiency_duration_over_30s(self):
        engine = EvaluationEngine()
        result = engine.evaluate(
            "Very slow task",
            result={"duration_seconds": 60},
            state=TaskState.COMPLETED,
        )
        assert result.efficiency_score == 0.5

    def test_generate_suggestions_low_quality(self):
        engine = EvaluationEngine()
        result = engine.evaluate(
            "Poor quality",
            result={"errors": ["err1", "err2", "err3"], "duration_seconds": 60},
            state=TaskState.COMPLETED,
        )
        has_quality_hint = any("quality" in s.lower() for s in result.suggestions)
        assert has_quality_hint is True

    def test_generate_suggestions_errors(self):
        engine = EvaluationEngine()
        result = engine.evaluate(
            "With errors",
            result={"errors": ["err1", "err2"]},
            state=TaskState.COMPLETED,
        )
        has_error_hint = any("error" in s.lower() for s in result.suggestions)
        assert has_error_hint is True

    def test_get_results(self):
        engine = EvaluationEngine()
        assert engine.get_results() == []
        engine.evaluate("A")
        engine.evaluate("B")
        assert len(engine.get_results()) == 2

    def test_evaluation_result_dataclass(self):
        result = EvaluationResult(
            task_id="t1",
            success=True,
            confidence=0.9,
            quality_score=0.85,
            efficiency_score=0.75,
        )
        assert result.task_id == "t1"
        assert result.suggestions == []
