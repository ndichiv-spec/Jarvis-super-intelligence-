import pytest
from jarvis_intelligence.reasoning import ReasoningEngine, ReasoningMode, ReasoningResult


class TestReasoningEngine:
    def test_reason_analytical(self):
        engine = ReasoningEngine()
        result = engine.reason("Analyze system performance", ReasoningMode.ANALYTICAL)
        assert isinstance(result, ReasoningResult)
        assert result.mode == ReasoningMode.ANALYTICAL
        assert result.confidence == 0.85
        assert len(result.steps) == 3

    def test_reason_sequential(self):
        engine = ReasoningEngine()
        result = engine.reason("Plan deployment", ReasoningMode.SEQUENTIAL)
        assert result.mode == ReasoningMode.SEQUENTIAL
        assert result.confidence == 0.80

    def test_reason_strategic(self):
        engine = ReasoningEngine()
        result = engine.reason("Strategic planning", ReasoningMode.STRATEGIC)
        assert result.mode == ReasoningMode.STRATEGIC
        assert len(result.alternatives) == 2
        assert len(result.risks) > 0

    def test_reason_comparative(self):
        engine = ReasoningEngine()
        result = engine.reason("Compare solutions", ReasoningMode.COMPARATIVE)
        assert result.mode == ReasoningMode.COMPARATIVE
        assert result.confidence == 0.70

    def test_reason_reflective(self):
        engine = ReasoningEngine()
        result = engine.reason("Review past decisions", ReasoningMode.REFLECTIVE)
        assert result.mode == ReasoningMode.REFLECTIVE
        assert result.confidence == 0.60

    def test_reason_constraint_based(self):
        engine = ReasoningEngine()
        result = engine.reason("Find solution within constraints", ReasoningMode.CONSTRAINT_BASED)
        assert result.mode == ReasoningMode.CONSTRAINT_BASED
        assert result.confidence == 0.65

    def test_reason_multi_step(self):
        engine = ReasoningEngine()
        result = engine.reason("Complex multi-step task", ReasoningMode.MULTI_STEP)
        assert result.mode == ReasoningMode.MULTI_STEP
        assert result.confidence == 0.72

    def test_reason_defaults_to_analytical(self):
        engine = ReasoningEngine()
        result = engine.reason("Some context")
        assert result.mode == ReasoningMode.ANALYTICAL

    def test_get_history(self):
        engine = ReasoningEngine()
        assert engine.get_history() == []
        engine.reason("First", ReasoningMode.ANALYTICAL)
        engine.reason("Second", ReasoningMode.STRATEGIC)
        assert len(engine.get_history()) == 2

    def test_reason_result_frozen(self):
        result = ReasoningResult(
            mode=ReasoningMode.ANALYTICAL,
            conclusion="Test",
            confidence=0.9,
        )
        with pytest.raises(AttributeError):
            result.conclusion = "changed"  # type: ignore[misc]
