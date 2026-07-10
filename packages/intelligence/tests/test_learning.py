import pytest
from jarvis_intelligence.learning import LearningEngine, LearningRecord
from jarvis_intelligence.evaluator import EvaluationResult


def _make_eval(quality=0.95, efficiency=0.85, confidence=0.9, success=True):
    return EvaluationResult(
        task_id="test-task",
        success=success,
        quality_score=quality,
        efficiency_score=efficiency,
        confidence=confidence,
    )


class TestLearningEngine:
    def test_record_success(self):
        engine = LearningEngine()
        eval_result = _make_eval()
        record = engine.record_success("Deploy the app", "incremental", eval_result)
        assert isinstance(record, LearningRecord)
        assert "Success" in record.outcome
        assert record.confidence == 0.9
        assert len(engine.get_all()) == 1

    def test_record_failure(self):
        engine = LearningEngine()
        record = engine.record_failure("Deploy the app", "incremental", "Timeout error")
        assert "Failure" in record.outcome
        assert record.confidence == 0.3
        assert len(engine.get_all()) == 1

    def test_get_recommendation_found(self):
        engine = LearningEngine()
        eval_result = _make_eval()
        engine.record_success("Deploy the microservices", "rolling", eval_result)
        recommendation = engine.get_recommendation("Deploy the microservices")
        assert recommendation is not None
        assert "rolling" in recommendation

    def test_get_recommendation_not_found(self):
        engine = LearningEngine()
        assert engine.get_recommendation("Something completely novel") is None

    def test_get_recommendation_partial_match(self):
        engine = LearningEngine()
        eval_result = _make_eval()
        engine.record_success("Build authentication module", "waterfall", eval_result)
        recommendation = engine.get_recommendation("authentication")
        assert recommendation is not None
        assert "waterfall" in recommendation

    def test_apply_record(self):
        engine = LearningEngine()
        eval_result = _make_eval()
        record = engine.record_success("Test apply", "default", eval_result)
        assert record.applied_count == 0
        engine.apply_record(record.id)
        assert engine.get_all()[0].applied_count == 1

    def test_get_all_empty(self):
        engine = LearningEngine()
        assert engine.get_all() == []

    def test_get_all_multiple(self):
        engine = LearningEngine()
        engine.record_success("A", "s1", _make_eval())
        engine.record_failure("B", "s2", "error")
        engine.record_success("C", "s3", _make_eval())
        assert len(engine.get_all()) == 3
