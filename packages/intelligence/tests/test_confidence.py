from jarvis_intelligence.confidence import ConfidenceEngine, ConfidenceScore


class TestConfidenceEngine:
    def test_compute_defaults(self):
        engine = ConfidenceEngine()
        score = engine.compute()
        assert isinstance(score, ConfidenceScore)
        assert 0 <= score.overall <= 1
        assert score.reasoning_quality == 0.7
        assert score.historical_success == 0.5

    def test_compute_high_confidence(self):
        engine = ConfidenceEngine()
        score = engine.compute(
            reasoning_quality=0.95,
            agent_capability=0.95,
            historical_success=0.95,
            data_completeness=0.95,
            risk_assessment=0.95,
        )
        assert score.overall >= 0.9

    def test_compute_low_confidence(self):
        engine = ConfidenceEngine()
        score = engine.compute(
            reasoning_quality=0.1,
            agent_capability=0.1,
            historical_success=0.1,
            data_completeness=0.1,
            risk_assessment=0.1,
        )
        assert score.overall < 0.3

    def test_compute_custom_weights(self):
        engine = ConfidenceEngine()
        score = engine.compute(
            reasoning_quality=1.0,
            agent_capability=0.0,
            historical_success=0.0,
            data_completeness=0.0,
            risk_assessment=0.0,
            weights={"reasoning_quality": 1.0, "agent_capability": 0.0, "historical_success": 0.0, "data_completeness": 0.0, "risk_assessment": 0.0},
        )
        assert score.overall == 1.0

    def test_classify_high(self):
        engine = ConfidenceEngine()
        score = ConfidenceScore(overall=0.9)
        assert engine.classify(score) == "high"

    def test_classify_medium(self):
        engine = ConfidenceEngine()
        score = ConfidenceScore(overall=0.65)
        assert engine.classify(score) == "medium"

    def test_classify_low(self):
        engine = ConfidenceEngine()
        score = ConfidenceScore(overall=0.3)
        assert engine.classify(score) == "low"

    def test_should_proceed_above_threshold(self):
        engine = ConfidenceEngine()
        score = ConfidenceScore(overall=0.7)
        assert engine.should_proceed(score, threshold=0.5) is True

    def test_should_proceed_below_threshold(self):
        engine = ConfidenceEngine()
        score = ConfidenceScore(overall=0.3)
        assert engine.should_proceed(score, threshold=0.5) is False

    def test_should_proceed_default_threshold(self):
        engine = ConfidenceEngine()
        high_score = ConfidenceScore(overall=0.8)
        low_score = ConfidenceScore(overall=0.3)
        assert engine.should_proceed(high_score) is True
        assert engine.should_proceed(low_score) is False

    def test_confidence_score_dataclass(self):
        score = ConfidenceScore(
            overall=0.85,
            reasoning_quality=0.9,
            agent_capability=0.8,
            factors={"experience": 0.7},
        )
        assert score.overall == 0.85
        assert score.factors["experience"] == 0.7
