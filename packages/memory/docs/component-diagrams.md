### Component Diagram (Text)

```text
MemoryKernel
 ├─ Memory Spaces
 │   ├─ WorkingMemory
 │   ├─ ShortTermMemory
 │   ├─ LongTermMemory
 │   ├─ EpisodicMemory
 │   ├─ SemanticMemory
 │   ├─ ProceduralMemory
 │   ├─ ConversationMemory
 │   ├─ ProjectMemory
 │   ├─ WorkspaceMemory
 │   └─ AgentMemoryRegistry -> AgentMemory[*]
 └─ Engines
     ├─ RetrievalEngine
     ├─ RankingEngine
     ├─ ConsolidationEngine
     ├─ ForgettingEngine
     ├─ MemoryPolicyEngine
     └─ TimelineEngine
```

- `MemoryKernel` orchestrates all operations and enforces policy-aware lifecycle.
- All components are pure Python domain services with strict typing.
