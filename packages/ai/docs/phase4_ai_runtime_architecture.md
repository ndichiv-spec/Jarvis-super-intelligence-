### AI Runtime Architecture

- The `RuntimeKernel` is the permanent orchestration layer between Brain and all AI providers.
- The Brain requests capabilities (`conversation`, `reasoning`, `embeddings`, etc.) and never calls provider SDKs directly.
- The runtime is composed of independent modules: registries, routing, prompt assembly, retries, streaming, normalization, and cost monitoring.
- Provider integrations implement runtime contracts and are registered dynamically through `ProviderRegistry`.
- Responses are normalized into one unified runtime format before being returned upstream.
