### Model Registry Documentation

- `ModelRegistry` stores immutable model metadata: provider, capabilities, token limits, context window, streaming support, cost, and performance scores.
- Models are indexed for provider-level and capability-level lookup.
- Runtime routing consumes registry metadata for manual, policy-based, priority, and fallback selection.
- Registry validation rejects duplicate model identifiers and invalid token/context limits.
