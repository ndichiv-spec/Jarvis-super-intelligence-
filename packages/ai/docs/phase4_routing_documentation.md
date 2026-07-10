### Routing Documentation

- Manual routing: explicit `manual_model_id` or `manual_provider_id`.
- Automatic routing: quality/reliability/speed scoring from model metadata.
- Priority routing: explicit provider order with deterministic precedence.
- Policy routing: low-cost / low-latency preference, minimum quality, required/disallowed tags.
- Fallback routing: provider chain returned by routing and executed by `RetryManager`.
