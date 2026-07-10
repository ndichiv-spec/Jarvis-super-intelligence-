from jarvis_intelligence.strategies import Strategy, StrategySelector, StrategyType


class TestStrategy:
    def test_sequential_creation(self):
        s = Strategy.sequential()
        assert s.type == StrategyType.SEQUENTIAL
        assert s.name == "Sequential"
        assert s.id == "strat-seq"

    def test_parallel_creation(self):
        s = Strategy.parallel()
        assert s.type == StrategyType.PARALLEL
        assert s.name == "Parallel"

    def test_hierarchical_creation(self):
        s = Strategy.hierarchical()
        assert s.type == StrategyType.HIERARCHICAL
        assert s.name == "Hierarchical"

    def test_strategy_dataclass(self):
        s = Strategy(
            id="custom", type=StrategyType.CONDITIONAL,
            name="Custom", description="Custom strategy",
            parameters={"threshold": 0.5},
            conditions=("cond1",),
            risk_level="high",
            expected_duration_seconds=120.0,
        )
        assert s.type == StrategyType.CONDITIONAL
        assert s.risk_level == "high"
        assert s.expected_duration_seconds == 120.0


class TestStrategySelector:
    def test_select_simple(self):
        selector = StrategySelector()
        s = selector.select("Simple task", "simple", ())
        assert s.type == StrategyType.SEQUENTIAL

    def test_select_complex(self):
        selector = StrategySelector()
        s = selector.select("Complex task", "complex", ())
        assert s.type == StrategyType.HIERARCHICAL

    def test_select_concurrent(self):
        selector = StrategySelector()
        s = selector.select("Concurrent task", "concurrent", ())
        assert s.type == StrategyType.PARALLEL

    def test_select_moderate_defaults_to_sequential(self):
        selector = StrategySelector()
        s = selector.select("Moderate task", "moderate", ())
        assert s.type == StrategyType.SEQUENTIAL

    def test_select_with_capabilities(self):
        selector = StrategySelector()
        s = selector.select("Task", "moderate", ("engineering", "devops"))
        assert s is not None
