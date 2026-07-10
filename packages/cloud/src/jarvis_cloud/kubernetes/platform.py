"""Kubernetes Platform - generate manifests and manage K8s deployments."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from jarvis_cloud.deployment.profiles import DeploymentEnvironment, DeploymentProfile


@dataclass(frozen=True)
class K8sResource:
    api_version: str
    kind: str
    name: str
    namespace: str
    spec: dict[str, Any] = field(default_factory=dict)
    labels: dict[str, str] = field(default_factory=dict)
    annotations: dict[str, str] = field(default_factory=dict)


class KubernetesPlatform:
    def __init__(self, profile: DeploymentProfile) -> None:
        self._profile = profile
        self._namespace = f"jarvis-{profile.environment.value}"

    @property
    def namespace(self) -> str:
        return self._namespace

    def generate_all(self) -> list[K8sResource]:
        resources: list[K8sResource] = []
        resources.append(self._namespace_resource())
        for name in self._profile.services:
            resources.append(self.deployment_resource(name))
            resources.append(self.service_resource(name))
            resources.append(self.hpa_resource(name))
            resources.append(self.pdb_resource(name))
            resources.append(self.service_monitor_resource(name))
        if self._profile.network.get("ingress"):
            resources.append(self.ingress_resource())
        return resources

    def _namespace_resource(self) -> K8sResource:
        return K8sResource(
            api_version="v1",
            kind="Namespace",
            name=self._namespace,
            namespace=self._namespace,
            labels={"app.kubernetes.io/name": "jarvis", "app.kubernetes.io/environment": self._profile.environment.value},
        )

    def deployment_resource(self, service_name: str) -> K8sResource:
        svc = self._profile.services[service_name]
        container = {
            "name": service_name,
            "image": f"{svc.image}:{svc.tag}",
            "ports": [{"containerPort": p} for p in svc.ports],
            "env": [{"name": k, "value": v} for k, v in svc.env.items()],
            "resources": {
                "limits": {"cpu": svc.cpu_limit, "memory": svc.memory_limit},
                "requests": {"cpu": svc.cpu_request, "memory": svc.memory_request},
            },
            "livenessProbe": {
                "httpGet": {"path": svc.health_check.get("path", "/health"), "port": svc.ports[0] if svc.ports else 8000},
                "initialDelaySeconds": svc.health_check.get("initial_delay", 30),
                "periodSeconds": svc.health_check.get("interval", 30),
                "timeoutSeconds": svc.health_check.get("timeout", 10),
                "failureThreshold": svc.health_check.get("retries", 3),
            },
            "readinessProbe": {
                "httpGet": {"path": svc.health_check.get("path", "/health"), "port": svc.ports[0] if svc.ports else 8000},
                "initialDelaySeconds": 10,
                "periodSeconds": 15,
                "timeoutSeconds": 5,
            },
        }
        if svc.volumes:
            container["volumeMounts"] = [{"name": v.split(":")[0], "mountPath": v.split(":")[1]} for v in svc.volumes]
        if svc.config_refs:
            container["envFrom"] = [{"configMapRef": {"name": r}} for r in svc.config_refs]
        if svc.secret_refs:
            container.setdefault("envFrom", [])
            container["envFrom"].extend({"secretRef": {"name": r}} for r in svc.secret_refs)

        spec: dict[str, Any] = {
            "replicas": svc.replicas,
            "selector": {"matchLabels": {"app": service_name}},
            "template": {
                "metadata": {
                    "labels": {"app": service_name, "service": service_name, "environment": self._profile.environment.value},
                },
                "spec": {
                    "containers": [container],
                    "imagePullSecrets": [{"name": "jarvis-registry"}] if self._profile.environment == DeploymentEnvironment.production else [],
                    "securityContext": {"runAsNonRoot": True, "runAsUser": 1000},
                },
            },
        }
        return K8sResource(
            api_version="apps/v1",
            kind="Deployment",
            name=service_name,
            namespace=self._namespace,
            spec=spec,
            labels={"app": service_name, "environment": self._profile.environment.value},
        )

    def service_resource(self, service_name: str) -> K8sResource:
        svc = self._profile.services[service_name]
        spec: dict[str, Any] = {
            "selector": {"app": service_name},
            "ports": [{"protocol": "TCP", "port": p, "targetPort": p} for p in svc.ports],
            "type": "ClusterIP",
        }
        return K8sResource(
            api_version="v1",
            kind="Service",
            name=service_name,
            namespace=self._namespace,
            spec=spec,
            labels={"app": service_name},
        )

    def hpa_resource(self, service_name: str) -> K8sResource:
        spec: dict[str, Any] = {
            "scaleTargetRef": {"apiVersion": "apps/v1", "kind": "Deployment", "name": service_name},
            "minReplicas": 1,
            "maxReplicas": 10,
            "metrics": [
                {"type": "Resource", "resource": {"name": "cpu", "target": {"type": "Utilization", "averageUtilization": 70}}},
                {"type": "Resource", "resource": {"name": "memory", "target": {"type": "Utilization", "averageUtilization": 80}}},
            ],
        }
        return K8sResource(
            api_version="autoscaling/v2",
            kind="HorizontalPodAutoscaler",
            name=service_name,
            namespace=self._namespace,
            spec=spec,
        )

    def pdb_resource(self, service_name: str) -> K8sResource:
        svc = self._profile.services[service_name]
        min_available = max(1, svc.replicas - 1) if svc.replicas > 1 else 1
        return K8sResource(
            api_version="policy/v1",
            kind="PodDisruptionBudget",
            name=service_name,
            namespace=self._namespace,
            spec={
                "minAvailable": min_available,
                "selector": {"matchLabels": {"app": service_name}},
            },
        )

    def service_monitor_resource(self, service_name: str) -> K8sResource:
        svc = self._profile.services[service_name]
        return K8sResource(
            api_version="monitoring.coreos.com/v1",
            kind="ServiceMonitor",
            name=service_name,
            namespace=self._namespace,
            spec={
                "selector": {"matchLabels": {"app": service_name}},
                "endpoints": [{"port": "http", "interval": "30s", "path": "/metrics"}],
                "namespaceSelector": {"matchNames": [self._namespace]},
            },
            labels={"release": "prometheus"},
        )

    def ingress_resource(self) -> K8sResource:
        domain = f"jarvis.{self._profile.environment.value}.local"
        if self._profile.network.get("tls"):
            tls = [{"hosts": [domain], "secretName": "jarvis-tls"}]
        else:
            tls = []
        rules = []
        for name, svc in self._profile.services.items():
            for port in svc.ports:
                rules.append({
                    "host": domain,
                    "http": {
                        "paths": [{
                            "path": f"/{name}(/|$)(.*)",
                            "pathType": "Prefix",
                            "backend": {"service": {"name": name, "port": {"number": port}}},
                        }],
                    },
                })
        return K8sResource(
            api_version="networking.k8s.io/v1",
            kind="Ingress",
            name="jarvis",
            namespace=self._namespace,
            spec={"tls": tls, "rules": rules} if tls else {"rules": rules},
            annotations={
                "nginx.ingress.kubernetes.io/rewrite-target": "/$2",
                "nginx.ingress.kubernetes.io/ssl-redirect": "true" if self._profile.network.get("tls") else "false",
            },
        )

    def to_yaml(self, resources: list[K8sResource] | None = None) -> str:
        lines: list[str] = []
        for rsrc in resources or self.generate_all():
            lines.append("---")
            lines.append(f"apiVersion: {rsrc.api_version}")
            lines.append(f"kind: {rsrc.kind}")
            lines.append("metadata:")
            lines.append(f"  name: {rsrc.name}")
            lines.append(f"  namespace: {rsrc.namespace}")
            if rsrc.labels:
                lines.append("  labels:")
                for k, v in rsrc.labels.items():
                    lines.append(f"    {k}: {v}")
            if rsrc.annotations:
                lines.append("  annotations:")
                for k, v in rsrc.annotations.items():
                    lines.append(f"    {k}: {v}")
            lines.append("spec:")
            for k, v in rsrc.spec.items():
                lines.extend(_yaml_dump(k, v, indent=4))
            lines.append("")
        return "\n".join(lines)


def _yaml_dump(key: str, value: Any, indent: int = 0) -> list[str]:
    prefix = " " * indent
    if isinstance(value, dict):
        lines = [f"{prefix}{key}:"]
        for k, v in value.items():
            lines.extend(_yaml_dump(k, v, indent + 2))
        return lines
    elif isinstance(value, list):
        lines = [f"{prefix}{key}:"]
        for item in value:
            if isinstance(item, dict):
                lines.append(f"{prefix}  -")
                for k, v in item.items():
                    lines.extend(_yaml_dump(k, v, indent + 4))
            else:
                lines.append(f"{prefix}  - {_yaml_value(item)}")
        return lines
    else:
        return [f"{prefix}{key}: {_yaml_value(value)}"]


def _yaml_value(v: Any) -> str:
    if isinstance(v, bool):
        return str(v).lower()
    if isinstance(v, str) and (":" in v or v.startswith(("{", "["))):
        return f'"{v}"'
    return str(v)
