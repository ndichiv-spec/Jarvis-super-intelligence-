"""Tests for Scaling Policies."""

from jarvis_cloud.scaling.policies import (
    ScalingPolicyEngine,
    ScalingPolicySet,
    HorizontalScalingPolicy,
    DEFAULT_POLICIES,
)


class TestScalingPolicyEngine:
    def setup_method(self):
        self.engine = ScalingPolicyEngine()

    def test_default_policies(self):
        assert "api" in self.engine.list_policies()
        assert "brain" in self.engine.list_policies()

    def test_get_policy(self):
        policy = self.engine.get_policy("api")
        assert policy is not None
        assert policy.service == "api"

    def test_get_nonexistent(self):
        policy = self.engine.get_policy("nonexistent")
        assert policy is None

    def test_set_policy(self):
        policy = ScalingPolicySet(
            service="custom",
            horizontal=HorizontalScalingPolicy(min_replicas=1, max_replicas=5),
        )
        self.engine.set_policy("custom", policy)
        assert self.engine.get_policy("custom") is not None

    def test_validate_valid(self):
        issues = self.engine.validate()
        assert isinstance(issues, list)

    def test_validate_invalid_policy(self):
        policy = ScalingPolicySet(
            service="bad",
            horizontal=HorizontalScalingPolicy(min_replicas=10, max_replicas=5),
        )
        self.engine.set_policy("bad", policy)
        issues = self.engine.validate()
        bad = [i for i in issues if "bad" in i]
        assert len(bad) >= 1
