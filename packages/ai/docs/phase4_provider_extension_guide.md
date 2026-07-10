### Provider Extension Guide

- Implement the `ProviderAdapter` contract (`supports_model`, `invoke`, `stream`, and `metadata`).
- Use `ProviderAdapterBase` as a foundation when creating new provider adapters.
- Register providers via `RuntimeKernel.register_provider(...)` with matching `ModelMetadata` entries.
- Keep provider-specific payload shaping inside `PromptAssemblyEngine`; avoid leaking it elsewhere.
- Return `ProviderResponse` only; runtime will normalize to `UnifiedResponse`.
