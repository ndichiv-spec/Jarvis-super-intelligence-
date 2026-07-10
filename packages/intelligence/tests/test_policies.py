import pytest
from jarvis_intelligence.policies import PolicyEngine, ExecutionPolicy, PolicyConfig


class TestPolicyEngine:
    def test_default_policy(self):
        engine = PolicyEngine()
        assert engine.get_current_policy() == ExecutionPolicy.BALANCED

    def test_set_policy(self):
        engine = PolicyEngine(ExecutionPolicy.CONSERVATIVE)
        assert engine.get_current_policy() == ExecutionPolicy.CONSERVATIVE
        engine.set_policy(ExecutionPolicy.AGGRESSIVE)
        assert engine.get_current_policy() == ExecutionPolicy.AGGRESSIVE

    def test_get_config_conservative(self):
        engine = PolicyEngine(ExecutionPolicy.CONSERVATIVE)
        config = engine.get_config()
        assert config.max_concurrent_tasks == 2
        assert config.max_retries == 1
        assert config.allow_parallel is False
        assert config.require_approval is True
        assert config.risk_tolerance == "low"

    def test_get_config_balanced(self):
        engine = PolicyEngine(ExecutionPolicy.BALANCED)
        config = engine.get_config()
        assert config.max_concurrent_tasks == 4
        assert config.max_retries == 3
        assert config.allow_parallel is True
        assert config.confidence_threshold == 0.6

    def test_get_config_aggressive(self):
        engine = PolicyEngine(ExecutionPolicy.AGGRESSIVE)
        config = engine.get_config()
        assert config.max_concurrent_tasks == 8
        assert config.max_retries == 5
        assert config.risk_tolerance == "high"

    def test_get_config_experimental(self):
        engine = PolicyEngine(ExecutionPolicy.EXPERIMENTAL)
        config = engine.get_config()
        assert config.max_concurrent_tasks == 16
        assert config.max_retries == 10
        assert config.confidence_threshold == 0.2

    def test_validate_parallel_execution_ok(self):
        engine = PolicyEngine(ExecutionPolicy.BALANCED)
        ok, msg = engine.validate_parallel_execution(3)
        assert ok is True

    def test_validate_parallel_execution_exceeded(self):
        engine = PolicyEngine(ExecutionPolicy.CONSERVATIVE)
        ok, msg = engine.validate_parallel_execution(5)
        assert ok is False
        assert "max_concurrent_tasks" in msg

    def test_validate_parallel_execution_disabled(self):
        engine = PolicyEngine(ExecutionPolicy.CONSERVATIVE)
        ok, msg = engine.validate_parallel_execution(2)
        assert ok is False
        assert "disabled" in msg

    def test_validate_retry_ok(self):
        engine = PolicyEngine(ExecutionPolicy.BALANCED)
        ok, msg = engine.validate_retry(1)
        assert ok is True

    def test_validate_retry_exceeded(self):
        engine = PolicyEngine(ExecutionPolicy.CONSERVATIVE)
        ok, msg = engine.validate_retry(3)
        assert ok is False
        assert "max_retries" in msg

    def test_policy_config_dataclass(self):
        config = PolicyConfig(
            max_concurrent_tasks=10,
            max_retries=5,
            timeout_seconds=600.0,
            confidence_threshold=0.5,
            allow_parallel=True,
            allow_agent_auto_selection=True,
            allow_replanning=True,
            require_approval=False,
            risk_tolerance="medium",
        )
        assert config.max_concurrent_tasks == 10
        assert config.risk_tolerance == "medium"
