## Phase 13 Deployment Guide

### Deployment Steps
- Provision runtime environment variables and secrets.
- Load profile-based infrastructure configuration.
- Register adapters in the `InfrastructureKernel`.
- Start kernel and verify metadata + health snapshots.

### Recommended Runtime Profiles
- `development`: SQLite, in-memory cache/vector/search, local storage.
- `staging`: PostgreSQL-ready, Redis-ready, cloud-object storage, OpenTelemetry.
- `production`: managed providers with secret manager integration and strict authorization.

### Startup Checklist
- All required secret references resolve successfully.
- Dependency graph is acyclic.
- Health status for critical adapters is `RUNNING`/available.
