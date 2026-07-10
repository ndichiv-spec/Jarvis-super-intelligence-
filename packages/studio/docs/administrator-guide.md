# Administrator Guide

## Platform Overview

JARVIS Studio is a multi-tenant AI agent management platform. It runs as a Next.js frontend that communicates with a Service Gateway (`NEXT_PUBLIC_GATEWAY_URL`). Administrators manage users, security, infrastructure, configuration, and observability through the Studio workspace.

## Security Center

**Route:** `/studio/security`

### Users

The Users tab displays all platform users with role assignments and authentication status.

| Column | Description |
|---|---|
| User | Avatar initials + name + email |
| Role | Badge: Admin / Engineer / Viewer |
| Status | StatusDot: active / inactive / suspended |
| Last Active | Relative timestamp |
| MFA | Checkmark (enabled) or X (disabled) |

**Administrative actions available:**
- Invite new users (via header "Invite User" button)
- Change user roles
- Suspend / activate user accounts
- View last active timestamp

### Roles

Role-based access control with three built-in tiers:

| Role | Description |
|---|---|
| Admin | Full platform access, user management, security configuration |
| Engineer | Workspace operations, agent/workflow/tool management |
| Viewer | Read-only access to all workspace data |

Each role displays:
- Description
- Permission count
- User count

### Policies

Security policies control platform-wide safety rules. Each policy shows its name, description, rules count, and an enabled/disabled toggle.

### Audit Log

Chronological record of all security-relevant actions:

| Column | Description |
|---|---|
| Actor | User who performed the action |
| Action | Specific operation (mono badge) |
| Resource | Target resource |
| Details | Action description |
| IP | Source IP (mono) |
| Timestamp | When it occurred |

## Configuration Center

**Route:** `/studio/config`

### Feature Flags

Toggle platform features on/off across environments. Each flag has:
- Key (mono string identifier)
- Name (human-readable)
- Description
- Enabled/disabled state
- Environment badge (Dev/Staging/Production)

### Runtime Configuration

Key-value configuration entries for platform behavior:
- Key/value pairs (both mono)
- Type badge (string/number/boolean/json)
- Description
- Last updated timestamp
- **Edit button** per row (inline editing)

### Configuration Profiles

Named groups of configuration entries:
- Profile name (FileJson icon)
- Description
- Config key count
- Active/Inactive status badge

## Infrastructure Monitor

**Route:** `/studio/infrastructure`

### Component Health Grid

Dashboard-style cards showing each infrastructure component:

| Component | Type | Status Indicators |
|---|---|---|
| API Gateway | Gateway | StatusDot + latency + uptime % |
| Database | Database | StatusDot + latency + uptime % |
| Cache | Cache | StatusDot + latency + upCheck |
| Vector Store | Vector Store | StatusDot + latency + uptime % |
| Message Broker | Message Broker | StatusDot + latency + upCheck |

Each card shows: type icon, component name, type badge, status dot + status badge, latency, uptime %, last checked time.

### Health Summary

- **StatCards**: Total components, healthy count, degraded count, critical count
- **Status breakdown**: List of component statuses with counts
- **Type breakdown**: Cards per component type with status dot indicators

### Known Infrastructure States

| State | Meaning | Recommended Action |
|---|---|---|
| Active | Component operational | — |
| Degraded | Partial functionality | Investigate latency/errors |
| Critical | Component unavailable | Immediate escalation |
| Maintenance | Scheduled downtime | Monitor maintenance window |

## AI Runtime Manager

**Route:** `/studio/ai`

### Providers

Configured AI providers with connection status:

| Detail | Description |
|---|---|
| Name | Provider name |
| Type | Provider type/category |
| Status | StatusDot (connected/error/rate-limited) |
| Models | Count of available models |
| Avg Latency | Response time (mono) |
| Total Calls | Cumulative usage |

### Model Catalog

All models available across providers:

| Detail | Description |
|---|---|
| Model | Model identifier (mono) |
| Provider | Source provider |
| Capabilities | Badges (chat, completion, embedding, vision) |
| Status | Active / Experimental / Deprecated |
| Tokens In/Out | Usage tracking |
| Cost | Per-token cost |

### Routing Configuration

Default routing strategy:
- Default provider
- Fallback strategy
- Health check interval
- Circuit breaker settings
- Per-model routing priority table

### Usage Monitoring

Token consumption tracking:
- Total tokens in / out
- Estimated cost
- Daily token usage bar chart (recharts)

## Observability Center

**Route:** `/studio/observability`

### Metrics

Platform-wide performance metrics:
- API calls over time (bar chart)
- Error rate over time (bar chart)
- Metric cards: Avg response time, total requests, error count, uptime

### Logs

Structured log viewer:
- Level badge (debug/info/warn/error)
- Source (mono)
- Message
- Timestamp

### Traces

Distributed tracing across services:
- **Top-level**: Trace name (mono), duration, status badge, span count, timestamp
- **Expandable rows**: Click to show span-level details

### Alerts

Alert management:
- Severity icon + badge
- Source (mono)
- Message
- Timestamp
- Acknowledgment status

## Event Monitor

**Route:** `/studio/events`

### Live Stream

Real-time event stream with:
- Event type icons
- Severity badges
- Source identification
- Summary text
- CorrelationId
- Timestamps
- Pulsing "Live" indicator

### Diagnostics

Event platform health:
- Metric cards: Total events, errors, warnings, info/debug
- Top event types distribution bar
- Severity distribution grid

## Automation Monitor

**Route:** `/studio/automation`

- **Running Workflows**: Currently executing with progress bars
- **History**: Completed executions with timing
- **Performance**: Execution time chart + avg duration
- **Failures**: Failed workflow details with error messages and timing

## Configuration Checklist

### Initial Setup
- [ ] Set `NEXT_PUBLIC_GATEWAY_URL` environment variable
- [ ] Configure AI providers in AI Runtime Manager
- [ ] Set up security policies and roles
- [ ] Create configuration profiles for each environment
- [ ] Verify infrastructure component connectivity

### Ongoing Operations
- [ ] Monitor audit log for suspicious activity
- [ ] Review token usage and cost trends
- [ ] Check infrastructure component health daily
- [ ] Review and acknowledge alerts
- [ ] Update feature flags as needed
- [ ] Manage extension versions and updates
- [ ] Review workflow failure patterns

### Security Best Practices
1. Assign least-privilege roles (Viewer > Engineer > Admin)
2. Enable MFA for all Admin users
3. Review audit log regularly
4. Rotate configuration secrets through runtime config
5. Monitor failed login attempts via audit log
6. Use environment-specific configuration profiles

## Troubleshooting

| Symptom | Check |
|---|---|
| Studio won't load | Verify `NEXT_PUBLIC_GATEWAY_URL` is reachable |
| Users can't log in | Check user status in Security Center |
| AI models unavailable | Check provider status in AI Runtime Manager |
| High error rate | Review Observability → Alerts and Logs |
| Slow performance | Check Infrastructure Monitor latency metrics |
| Workflows failing | Review Automation Monitor → Failures tab |
| Data inconsistencies | Check Vector Store health in Infrastructure |
