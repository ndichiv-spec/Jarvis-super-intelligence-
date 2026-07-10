# Enterprise Operations Handbook

## Platform Health Monitoring

### Service Health Reporting
```python
from jarvis_enterprise.observability.service import EnterpriseObservabilityService
from jarvis_enterprise.observability.models import ServiceStatus

observability = EnterpriseObservabilityService()

# Report health for each service
observability.report_service_health("api", ServiceStatus.healthy, latency_ms=12.5)
observability.report_service_health("brain", ServiceStatus.healthy, latency_ms=45.2)
observability.report_service_health("memory", ServiceStatus.degraded, latency_ms=250.0)
```

### Platform Health Summary
```python
platform_health = observability.get_platform_health(org_id=org.id)
print(f"Overall: {platform_health.overall_status}")
print(f"Healthy: {platform_health.healthy_services}/{platform_health.total_services}")
```

## Usage Tracking

### Recording Usage Metrics
```python
metric = observability.record_usage(
    metric_name="api_requests",
    org_id=org.id,
    total=1000,
    by_service={"api": 800, "agents": 200}
)
```

### Performance Trends
```python
trend = observability.get_performance_trend("api_requests")
if trend:
    print(f"Change: {trend.change_pct:+.1f}% — {trend.trend}")
```

## Availability Tracking

```python
observability.record_availability("api", availability_pct=99.95, downtime_minutes=2)
observability.record_availability("brain", availability_pct=99.99)
```

## Security Incident Response

### Reporting Incidents
```python
from jarvis_enterprise.security_center.service import SecurityCenterService
from jarvis_enterprise.security_center.models import IncidentSeverity

security = SecurityCenterService()

incident = security.report_incident(
    org_id=org.id,
    title="Suspicious API access pattern",
    description="Multiple failed auth attempts from unknown IP",
    severity=IncidentSeverity.high,
    reported_by="security-bot"
)
```

### Resolving Incidents
```python
resolved = security.resolve_incident(
    incident_id=incident.id,
    resolution="IP blocked, MFA enforcement verified"
)
```

## Resource Management

### Setting Quotas
```python
from jarvis_enterprise.resource_management.service import ResourceManagementService
from jarvis_enterprise.resource_management.models import ResourceType, QuotaPeriod

resources = ResourceManagementService(repository)

quota = resources.set_quota(
    org_id=org.id,
    resource_type=ResourceType.ai_provider,
    resource_name="openai-gpt4",
    limit=1000000,  # tokens per month
    period=QuotaPeriod.monthly
)
```

### Checking Quota Before Operations
```python
ok, remaining = resources.check_quota(
    org_id=org.id,
    resource_type="ai_provider",
    resource_name="openai-gpt4"
)
if ok:
    # Proceed with operation
    pass
else:
    # Block or warn
    print(f"Quota exceeded, remaining: {remaining}")
```

## Business Continuity

### Incident Response Plans
```python
from jarvis_enterprise.continuity.service import BusinessContinuityService

continuity = BusinessContinuityService()

plan = continuity.create_incident_plan(
    name="Service Outage Response",
    description="Steps to recover from service degradation",
    severity="critical",
    owners=("oncall-team",)
)
```

### Recovery Procedures
```python
procedure = continuity.create_recovery_procedure(
    name="Database Recovery",
    target="postgres-primary",
    steps=(
        "1. Stop application services",
        "2. Restore from latest backup",
        "3. Verify data integrity",
        "4. Restart application services",
    ),
    estimated_rto_minutes=30,
    estimated_rpo_minutes=15
)

# After testing
continuity.verify_recovery_procedure(procedure.id)
```

## Runbooks

```python
runbook = continuity.create_runbook(
    title="Weekly Backup Verification",
    category=RunbookCategory.backup,
    description="Validate all backup integrity",
    steps=(
        "1. Check backup completion status",
        "2. Verify checksums",
        "3. Test restore on staging",
        "4. Document results",
    ),
    owner="infra-team"
)
```

## Operational Dashboards

### Admin Dashboard
```python
dashboard = admin_service.get_dashboard(
    org_count=len(platform.organizations.list_organizations()),
    ws_count=sum(len(ws_service.list_workspaces(o.id)) for o in orgs),
    user_count=total_users
)
```

### Security Dashboard
```python
security_dash = security.get_dashboard(org_id=org.id)
print(f"Open incidents: {security_dash.open_incidents}")
print(f"Critical: {security_dash.critical_incidents}")
```
