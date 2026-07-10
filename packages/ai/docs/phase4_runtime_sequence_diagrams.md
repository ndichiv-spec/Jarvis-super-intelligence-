### Runtime Sequence Diagrams

```text
Brain -> RuntimeKernel: RuntimeRequest(capability, instructions, input)
RuntimeKernel -> RoutingEngine: route(request)
RoutingEngine -> ProviderRegistry/ModelRegistry: candidates
RuntimeKernel -> PromptAssemblyEngine: assemble(provider-specific request)
RuntimeKernel -> RetryManager: execute(primary + fallbacks)
RetryManager -> ProviderAdapter: invoke/stream
RuntimeKernel -> ResponseNormalizer: normalize(provider response)
RuntimeKernel -> CostMonitor: record usage/cost/latency
RuntimeKernel -> Brain: UnifiedResponse
```
