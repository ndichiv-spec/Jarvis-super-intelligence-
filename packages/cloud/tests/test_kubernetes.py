"""Tests for Kubernetes Platform."""

from jarvis_cloud.deployment.profiles import ProfileLoader
from jarvis_cloud.kubernetes.platform import KubernetesPlatform


class TestKubernetesPlatform:
    def setup_method(self):
        profile = ProfileLoader().load("production")
        self.k8s = KubernetesPlatform(profile)

    def test_namespace(self):
        assert self.k8s.namespace == "jarvis-production"

    def test_generate_all(self):
        resources = self.k8s.generate_all()
        kinds = {r.kind for r in resources}
        assert "Namespace" in kinds
        assert "Deployment" in kinds
        assert "Service" in kinds
        assert "HorizontalPodAutoscaler" in kinds
        assert "PodDisruptionBudget" in kinds

    def test_deployment_count(self):
        resources = self.k8s.generate_all()
        deployments = [r for r in resources if r.kind == "Deployment"]
        assert len(deployments) == 8

    def test_service_count(self):
        resources = self.k8s.generate_all()
        services = [r for r in resources if r.kind == "Service"]
        assert len(services) == 8

    def test_deployment_replicas(self):
        resources = self.k8s.generate_all()
        api_deploy = [r for r in resources if r.kind == "Deployment" and r.name == "api"][0]
        assert api_deploy.spec["replicas"] == 3

    def test_hpa_present(self):
        resources = self.k8s.generate_all()
        hpas = [r for r in resources if r.kind == "HorizontalPodAutoscaler"]
        assert len(hpas) == 8

    def test_pdb_present(self):
        resources = self.k8s.generate_all()
        pdbs = [r for r in resources if r.kind == "PodDisruptionBudget"]
        assert len(pdbs) == 8

    def test_to_yaml(self):
        resources = self.k8s.generate_all()
        yaml = self.k8s.to_yaml(resources[:1])
        assert "apiVersion:" in yaml
        assert "kind:" in yaml
