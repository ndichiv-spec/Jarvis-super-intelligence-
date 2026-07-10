# Enterprise Compliance Guide

## Compliance Center Overview

The Compliance Center provides governance interfaces for audit, data retention, legal hold, and regional data policies. It supports multiple frameworks including GDPR, SOC2, ISO 27001, and HIPAA.

## Audit Exports

### Requesting an Export
```python
from jarvis_enterprise.compliance.service import ComplianceCenterService
from jarvis_enterprise.compliance.models import ExportFormat, ComplianceFramework

compliance = ComplianceCenterService()

request = compliance.request_audit_export(
    org_id=org.id,
    requested_by="auditor@company.com",
    format=ExportFormat.json
)
```

### Listing Export Requests
```python
exports = compliance.list_export_requests(org_id=org.id)
for export in exports:
    print(f"{export.id}: {export.status} — {export.format}")
```

## Data Retention Policies

### Creating Retention Policies
```python
policy = compliance.create_retention_policy(
    org_id=org.id,
    data_category="user_activity_logs",
    retention_days=90,      # Keep in active storage
    archival_days=365       # Archive for 1 year
)
```

## Legal Hold

### Applying a Hold
```python
hold = compliance.apply_legal_hold(
    org_id=org.id,
    case_name="Employment Litigation 2026-001",
    data_categories=("email", "chat", "documents"),
    applied_by="legal-team@company.com"
)
```

### Releasing a Hold
```python
released = compliance.release_legal_hold(hold_id=hold.id)
# Data now subject to normal retention/deletion policies
```

## Regional Data Policies

```python
policy = compliance.create_regional_policy(
    region="EU",
    data_categories=("personal_data", "financial_data", "health_data")
)
# Requires_local_storage=True, export_restricted=False by default
```

## Compliance Reporting

### Generating Reports
```python
report = compliance.generate_compliance_report(
    org_id=org.id,
    framework=ComplianceFramework.soc2
)
print(f"Status: {report.status}")
```

## Compliance Frameworks

| Framework | Focus | Key Controls |
|---|---|---|
| GDPR | Personal data protection | Right to erasure, data portability, consent management |
| SOC2 | Service organization controls | Security, availability, processing integrity |
| ISO 27001 | Information security management | Risk assessment, access control, incident management |
| HIPAA | Healthcare data privacy | PHI protection, breach notification, safeguards |

## Best Practices

1. **Define retention policies early** — apply to all data categories before ingestion
2. **Test audit exports regularly** — ensure format compatibility with external auditors
3. **Document legal holds** — maintain case reference numbers for audit trail
4. **Regional policy alignment** — configure data residency rules per deployment region
5. **Compliance reporting cadence** — generate reports monthly or per audit cycle
