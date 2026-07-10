### Sequence Diagram: Store + Retrieve

```text
Caller -> MemoryKernel: store(memory)
MemoryKernel -> MemoryPolicyEngine: resolve(scope)
MemoryKernel -> MemoryKernel: apply store policy (ttl/retention)
MemoryKernel -> MemorySpace: put(memory)
MemoryKernel -> Caller: stored memory

Caller -> MemoryKernel: retrieve(query, context)
MemoryKernel -> RetrievalEngine: search(memories, query)
MemoryKernel -> RankingEngine: rank(matches, context)
MemoryKernel -> Caller: scored memories
```

### Sequence Diagram: Consolidation + Forgetting

```text
Caller -> MemoryKernel: consolidate()
MemoryKernel -> ConsolidationEngine: consolidate(all memories)
MemoryKernel -> MemorySpaces: reset + repopulate

Caller -> MemoryKernel: apply_policies(now)
loop each memory
  MemoryKernel -> MemoryPolicyEngine: resolve(scope)
  MemoryKernel -> ForgettingEngine: evaluate(memory, policy, now)
  alt archive
    MemoryKernel -> MemorySpace: put(archived memory)
  alt delete (policy-approved)
    MemoryKernel -> MemorySpace: remove(memory)
end
```
