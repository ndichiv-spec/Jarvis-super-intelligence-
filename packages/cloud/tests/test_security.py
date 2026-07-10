"""Tests for Cloud Security Integration."""

from jarvis_cloud.security.integration import (
    CloudSecurityIntegration,
    SecretInjectionMethod,
    NetworkPolicyMode,
)


class TestCloudSecurityIntegration:
    def setup_method(self):
        self.security = CloudSecurityIntegration()

    def test_default_network_policies(self):
        assert len(self.security.config.network_policies) > 0

    def test_default_mode(self):
        assert self.security.config.network_policy_mode == NetworkPolicyMode.default_deny

    def test_add_secret(self):
        self.security.add_secret("db", "password", "DB_PASSWORD")
        assert len(self.security.config.secrets) == 1

    def test_generate_network_policy(self):
        yaml = self.security.generate_network_policy_yaml()
        assert "NetworkPolicy" in yaml
        assert "jarvis-network-policy" in yaml

    def test_validate(self):
        issues = self.security.validate()
        assert isinstance(issues, list)
