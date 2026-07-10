### Memory Policy Documentation

- `MemoryPolicy` governs:
  - Short-term TTL
  - Archive window
  - Legal/workspace retention
  - Confidence and relevance decay
  - Manual/permanent deletion permissions

### Policy Scope Resolution

- Resolution precedence:
  1. Temporary session policy
  2. Agent policy
  3. Project policy
  4. Workspace policy
  5. Enterprise policy
  6. Default policy

### Safety Rule

- Permanent deletion is denied without explicit policy approval and policy capability.
