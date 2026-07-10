# Phase 12 Extension Guide

## Security Contracts for Extensions

Extensions consume security services through:

- Security context
- Authorization requests
- Policy-governed execution
- Audit trace generation

## Extension Security Expectations

- Declare required capabilities and permissions.
- Execute only through authorized paths.
- Respect workspace isolation boundaries.
- Emit traceable activity via kernel-mediated operations.

## Future Integration

Authentication providers and secret management backends can be attached to
existing contracts without changing extension-facing APIs.
