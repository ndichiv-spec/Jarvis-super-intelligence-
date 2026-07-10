# Enterprise Platform Deployment Guide

## Prerequisites

- Python 3.13+
- `jarvis-enterprise` package installed
- Access to repository implementations (in-memory, SQL, cloud backends)
- Existing JARVIS platform packages (security, core, infrastructure)

## Installation

```bash
# From workspace root
uv pip install -e packages/enterprise
```

## Package Structure

```
packages/enterprise/
├── pyproject.toml
├── src/
│   └── jarvis_enterprise/
│       ├── platform/kernel.py       # EnterprisePlatform orchestrator
│       ├── organization/            # Organization models, repository, service
│       ├── workspace/               # Workspace administration
│       ├── user/                    # User lifecycle and invitations
│       ├── governance/              # Policy engine and rules
│       ├── collaboration/           # Shared projects, discussions, reviews
│       ├── security_center/         # Incident tracking, security dashboards
│       ├── observability/           # Health, usage, availability monitoring
│       ├── resource_management/     # Quotas, allocation, usage policies
│       ├── billing/                 # Subscription plans, licenses, cost tracking
│       ├── compliance/              # Audit exports, legal hold, retention
│       ├── integration/             # Adapter-based external system integration
│       ├── admin_portal/            # Audit log, configuration, dashboards
│       ├── analytics/               # Reports, metrics, dashboards
│       └── continuity/              # Runbooks, recovery procedures
└── tests/                           # Full test suite (123+ tests)
```

## Configuration

The platform uses constructor injection for all dependencies. Configure your repository implementations based on deployment scale:

### Development (In-Memory)
```python
from jarvis_enterprise.platform.kernel import EnterprisePlatform
from jarvis_enterprise.organization.service import OrganizationService
from tests.test_organization import InMemoryOrgRepository

platform = EnterprisePlatform(
    organization_service=OrganizationService(InMemoryOrgRepository()),
    # ... configure other services similarly
)
```

### Production (SQL/Cloud)
Implement each repository protocol against your chosen backend (PostgreSQL, Redis, etc.) following the existing `jarvis-infrastructure` adapter patterns.

## Service Dependencies

```
EnterprisePlatform
├── OrganizationService → OrganizationRepository
├── WorkspaceService    → WorkspaceRepository
├── UserService         → EnterpriseUserRepository
├── GovernanceService   → GovernanceRepository
├── CollaborationService → CollaborationRepository
├── ResourceService     → ResourceRepository
├── BillingService      → BillingRepository
├── IntegrationService  → IntegrationRepository
├── AnalyticsService    → AnalyticsRepository
├── SecurityService     → (in-memory by default)
├── ObservabilityService → (in-memory by default)
├── ComplianceService   → (in-memory by default)
├── AdminService        → (in-memory by default)
└── ContinuityService   → (in-memory by default)
```

## Testing

```bash
cd packages/enterprise
$env:PYTHONPATH = "src"; uv run --no-project pytest tests/ -v
```

Expected: 123+ tests passing, covering all 14 domain modules.

## Verification Checklist

- [ ] Package installs without errors
- [ ] All 123 tests pass
- [ ] Organization isolation verified (org1 cannot access org2 data)
- [ ] Workspace isolation verified
- [ ] Governance policies correctly evaluate actions
- [ ] Collaboration workflows create, approve, reject
- [ ] Incident reporting and resolution works
- [ ] Quota enforcement blocks when exceeded
- [ ] Subscription/license lifecycle works
- [ ] Audit trail captures all administrative actions
- [ ] Compliance export generates correctly
- [ ] Integration adapters register and configure
- [ ] Analytics metrics record and query
- [ ] Business continuity runbooks store and retrieve
