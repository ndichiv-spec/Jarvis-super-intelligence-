# Phase 14 Response Lifecycle

1. External route executor returns `GatewayResponse`.
2. Kernel normalizes body to a consistent envelope:
   - `ok`
   - `data`
   - `error`
   - `metadata`
3. Response middleware pipeline executes (headers/transforms).
4. Streaming payloads (if any) are wrapped by `StreamingEngine` into ordered envelopes.
5. Gateway sends protocol-appropriate response format to client.

## Response Metadata

- Request id
- Session id
- Resolved API version
- Route identifier
- Subsystem identifier
- Optional deprecation/migration guidance
