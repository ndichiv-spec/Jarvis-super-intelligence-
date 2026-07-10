from jarvis_planning.estimator import Complexity, Estimate, Estimator


class TestComplexity:
    def test_enum_values(self) -> None:
        assert Complexity.TRIVIAL.value == "trivial"
        assert Complexity.SIMPLE.value == "simple"
        assert Complexity.MODERATE.value == "moderate"
        assert Complexity.COMPLEX.value == "complex"
        assert Complexity.VERY_COMPLEX.value == "very_complex"


class TestEstimator:
    def test_estimate_simple(self) -> None:
        estimator = Estimator()
        est = estimator.estimate("Build a simple web page")
        assert est.complexity in (Complexity.TRIVIAL, Complexity.SIMPLE)
        assert est.effort_hours > 0
        assert est.confidence > 0

    def test_estimate_complex(self) -> None:
        estimator = Estimator()
        est = estimator.estimate(
            "Build a complex distributed enterprise platform with machine learning "
            "and real-time analytics across multiple regions"
        )
        assert est.complexity in (Complexity.COMPLEX, Complexity.VERY_COMPLEX)
        assert est.effort_hours >= 5.0
        assert est.duration_text in ("weeks", "months")

    def test_estimate_with_domain(self) -> None:
        estimator = Estimator()
        est = estimator.estimate("Build a payment processing system", domain="finance")
        assert est.complexity is not None

    def test_estimate_with_factors(self) -> None:
        estimator = Estimator()
        est = estimator.estimate("Build an API", domain="web", known_factors=["backend_development", "api_design"])
        assert len(est.factors) == 2

    def test_estimate_breakdown(self) -> None:
        estimator = Estimator()
        est = estimator.estimate("Build something")
        assert "objective_analysis" in est.breakdown
        assert est.breakdown["objective_analysis"] > 0

    def test_score_to_complexity(self) -> None:
        estimator = Estimator()
        assert estimator._score_to_complexity(1.0) == Complexity.TRIVIAL
        assert estimator._score_to_complexity(2.0) == Complexity.SIMPLE
        assert estimator._score_to_complexity(4.0) == Complexity.MODERATE
        assert estimator._score_to_complexity(8.0) == Complexity.COMPLEX
        assert estimator._score_to_complexity(15.0) == Complexity.VERY_COMPLEX

    def test_calculate_confidence(self) -> None:
        estimator = Estimator()
        conf = estimator._calculate_confidence(3.0, 3)
        assert 0 < conf <= 0.95

    def test_assess_risk(self) -> None:
        estimator = Estimator()
        assert estimator._assess_risk(Complexity.TRIVIAL, 0.9) == "low"
        assert estimator._assess_risk(Complexity.COMPLEX, 0.3) == "high"
        assert estimator._assess_risk(Complexity.MODERATE, 0.3) == "medium"

    def test_weighted_average_empty(self) -> None:
        avg = Estimator.weighted_average([])
        assert avg.complexity == Complexity.TRIVIAL
        assert avg.effort_hours == 0.0

    def test_weighted_average(self) -> None:
        e1 = Estimate(Complexity.MODERATE, 5.0, "days", 0.8, "low")
        e2 = Estimate(Complexity.COMPLEX, 13.0, "weeks", 0.6, "medium")
        avg = Estimator.weighted_average([e1, e2])
        assert avg.effort_hours > 0
        assert avg.complexity == Complexity.COMPLEX
        assert avg.risk_level == "medium"


class TestEstimate:
    def test_to_dict(self) -> None:
        est = Estimate(Complexity.MODERATE, 5.0, "days", 0.8, "low", factors=["a"], breakdown={"x": 1.0})
        d = est.to_dict()
        assert d["complexity"] == "moderate"
        assert d["effort_hours"] == 5.0
        assert d["risk_level"] == "low"
