### Extension Guide

- Add new retrieval/ranking behavior by implementing protocol-compatible engines and injecting them into `MemoryKernel`.
- Extend policy behavior by wrapping or replacing `DefaultMemoryPolicyEngine`.
- Add new memory kinds by extending `MemoryType` and adding space routing in `MemoryKernel`.
- Keep extensions domain-only; persistence and infrastructure adapters belong to later phases.
