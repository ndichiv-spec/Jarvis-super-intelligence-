# Phase 12 Developer Guide

## Using the Security Platform

1. Instantiate `SecurityKernel`.
2. Register identities, organization units, and workspace boundaries.
3. Register any custom roles, permissions, and policy rules.
4. Issue `SecurityContext` for each execution.
5. Build `AuthorizationRequest` and call kernel authorization.

## Extension Points

- Authentication provider contracts
- Secret manager contracts
- Compliance registry/export contracts

## Design Rules

- Keep integrations framework-agnostic.
- Do not bypass policy or authorization engines.
- Use metadata-backed domain objects for all security state.
