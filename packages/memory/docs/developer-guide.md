### Developer Guide

- Entry point: `jarvis_memory.MemoryKernel`.
- Build `MemoryRecord` with complete `MemoryMetadata` and call `store`.
- Query via `retrieve(RetrievalQuery, RankingContext)` to get scored results.
- Use `apply_policies` for scheduled forgetting/archiving.
- Use `consolidate` to merge duplicate cognitive memories.

### Local Testing

- Run package tests:

```powershell
uv run pytest packages\memory\tests
```
