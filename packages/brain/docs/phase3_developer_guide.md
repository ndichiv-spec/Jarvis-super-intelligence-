### Phase 3 Brain Developer Guide

### Local Development

- Package path: `packages/brain`
- Source package: `packages/brain/src/jarvis_brain`
- Tests: `packages/brain/tests`
- Docs: `packages/brain/docs`

### Run Tests

- `uv run pytest packages\brain\tests`

### Run Lint and Types

- `uv run ruff check packages\brain\src packages\brain\tests`
- `uv run mypy --package jarvis_brain` (executed from `packages/brain`)

### Implementation Notes

- Keep dataclasses and state immutable unless mutation is explicitly required.
- Use protocol interfaces for engine boundaries.
- Keep all orchestration in `BrainKernel`; keep engines single-purpose.
- Keep response output structured; natural-language generation is out of scope.
