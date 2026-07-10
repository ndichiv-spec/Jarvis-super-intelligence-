"""jarvis - JARVIS AI Platform.

Public API:
  runtime      — Runtime facade (start/stop/restart/health/status/diagnostics)
  health       — HealthReport, HealthCheck, HealthStatus
  lifecycle    — LifecycleManager, LifecycleState, LifecycleEvent
  registry     — ServiceRegistry, ServiceHandle, ServiceStatus
  configuration — ConfigurationLoader, AppConfig
  environment  — EnvironmentValidator, EnvCheck
  diagnostics  — DiagnosticReport, generate_report
"""

from app.runtime import Runtime

__all__ = [
    "Runtime",
]
