# Enterprise Administration Guide

## Administrator Roles

The Enterprise Platform supports several administrative roles through the existing `jarvis-security` RBAC model:

- **ENTERPRISE_ADMINISTRATOR** — Full platform access across all organizations
- **ORGANIZATION_ADMIN** — Administration within a specific organization
- **WORKSPACE_ADMIN** — Administration within a specific workspace
- **AUDITOR** — Read-only access to audit logs and compliance data

## Organization Administration

### Creating an Organization
```python
from jarvis_enterprise.organization.service import OrganizationService

org_service = OrganizationService(repository)
org = org_service.create_organization(
    name="acme-corp",
    display_name="Acme Corporation",
    description="Enterprise AI deployment"
)
```

### Managing Organizational Units
```python
unit = org_service.add_unit(
    org_id=org.id,
    name="Engineering",
    unit_type=OrgUnitType.department,
    parent_id=division_id  # Optional parent
)
```

### Suspending an Organization
```python
suspended = org_service.suspend_organization(org.id)
# All workspaces and resources become inaccessible
```

## Workspace Administration

### Creating Workspaces
```python
from jarvis_enterprise.workspace.service import WorkspaceAdministrationService

ws_service = WorkspaceAdministrationService(repository)
workspace = ws_service.create_workspace(
    org_id=org.id,
    name="ml-research",
    owner_id="user-123",
    visibility=WorkspaceVisibility.internal
)
```

### Resource Allocation
```python
# Set compute quota for a workspace
allocation = ws_service.set_resource_allocation(
    workspace_id=workspace.id,
    resource_type="compute",
    limit=100  # CPU core hours
)
```

## User Administration

### Inviting Users
```python
from jarvis_enterprise.user.service import UserAdministrationService

user_service = UserAdministrationService(repository)
invitation = user_service.invite_user(
    email="newuser@company.com",
    org_id=org.id,
    invited_by="admin@company.com",
    role="developer"
)
```

### Access Reviews
```python
review = user_service.create_access_review(
    org_id=org.id,
    reviewer_id="security-officer",
    target_user_id="user-456"
)
user_service.complete_access_review(review.id, approved=True)
```

## Platform Configuration

### Managing Configuration
```python
from jarvis_enterprise.admin_portal.service import AdministrationPortalService

admin_service = AdministrationPortalService()
config = admin_service.set_configuration(
    key="max_workspaces_per_org",
    value="50",
    category="limits",
    updated_by="sysadmin",
    description="Maximum workspaces an organization can create"
)
```

### Audit Trail
```python
# All administrative actions are automatically logged
entries = admin_service.get_audit_log(org_id=org.id)
for entry in entries:
    print(f"{entry.timestamp}: {entry.event_type} by {entry.actor_id}")
```

## Running the Platform

```python
from jarvis_enterprise.platform.kernel import EnterprisePlatform

platform = EnterprisePlatform(
    organization_service=org_service,
    workspace_service=ws_service,
    user_service=user_service,
    governance_service=governance_service,
    collaboration_service=collaboration_service,
    security_service=security_service,
    observability_service=observability_service,
    resource_service=resource_service,
    billing_service=billing_service,
    compliance_service=compliance_service,
    integration_service=integration_service,
    admin_service=admin_service,
    analytics_service=analytics_service,
    continuity_service=continuity_service,
)

state = platform.initialize()
print(f"Platform status: {platform.health()}")
```
