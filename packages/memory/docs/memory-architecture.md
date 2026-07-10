### Memory Architecture

- `MemoryKernel` is the central coordinator for store, retrieve, update, rank, consolidate, relationship, policy, forgetting, and timeline workflows.
- The package is domain-only and framework-independent: no database, HTTP, OS, hardware, browser, or desktop APIs are referenced.
- Cognitive memory is modeled as immutable `MemoryRecord` aggregates with explicit `MemoryMetadata`.
- Storage is in-memory and policy-driven by design, preparing later adapter-based persistence.

### Core Components

- Memory spaces:
  - `WorkingMemory`
  - `ShortTermMemory`
  - `LongTermMemory`
  - `EpisodicMemory`
  - `SemanticMemory`
  - `ProceduralMemory`
  - `ConversationMemory`
  - `ProjectMemory`
  - `WorkspaceMemory`
  - `AgentMemoryRegistry` + isolated `AgentMemory`
- Engines:
  - `DefaultRetrievalEngine`
  - `DefaultRankingEngine`
  - `DefaultConsolidationEngine`
  - `DefaultForgettingEngine`
  - `DefaultMemoryPolicyEngine`
  - `DefaultTimelineEngine`

### Architectural Constraints

- Clean Architecture and Dependency Inversion are enforced through protocols and engine/store abstractions.
- No persistence adapters are implemented in this phase.
- No filesystem/system scanning or device telemetry is performed.
