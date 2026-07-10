### Lifecycle Documentation

1. **Creation**
   - Memory is created in the JARVIS ecosystem or approved user interaction.
2. **Storage**
   - `MemoryKernel.store` resolves policy scope and applies TTL/retention constraints.
3. **Retrieval**
   - Query filtering (`RetrievalQuery`) + relevance ranking (`RankingContext`).
4. **Reinforcement**
   - Access and updates increment memory freshness and usage signals.
5. **Consolidation**
   - Duplicate records are merged and lineage preserved.
6. **Forgetting/Archiving**
   - Policy engine + forgetting engine archive or delete based on approved policy.
7. **Timeline Reconstruction**
   - Memory history is projected into chronological `TimelineEvent` records.
