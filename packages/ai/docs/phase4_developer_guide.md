### Developer Guide

- Add providers by implementing `ProviderAdapter` and registering models/capabilities through the kernel.
- Keep all provider interaction behind the runtime; Brain code must only use runtime interfaces.
- Use `RuntimeKernel.execute(...)` for request/response workflows.
- Use `RuntimeKernel.stream(...)` with `CancellationToken` for streaming workflows.
- Use `CostMonitor.snapshot()` for provider/model usage and cost reporting.
