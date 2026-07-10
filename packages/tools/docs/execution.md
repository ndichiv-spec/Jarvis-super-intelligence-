# Execution Engine

The execution engine manages the full lifecycle of tool execution requests.

## Lifecycle States

```
QUEUED → RUNNING → COMPLETED
                 → FAILED
                 → CANCELLED
                 → TIMED_OUT
                 → RETRY_REQUESTED → RUNNING …
```

## Components

- **InMemoryExecutionEngine** — state machine that tracks requests, statuses,
  and results. Delegates actual tool work to a `ToolExecutor`.
- **InMemoryToolExecutor** — base executor that produces a mock result.
  Custom executors can be registered per tool identifier.

## Usage

```python
from jarvis_tools.execution import InMemoryExecutionEngine, InMemoryToolExecutor
from jarvis_tools.models import ToolExecutionRequest

engine = InMemoryExecutionEngine()
engine.register_executor("my.tool", InMemoryToolExecutor())

req = ToolExecutionRequest(
    request_id="req-1",
    tool_identifier="my.tool",
    agent_id="agent-1",
    parameters={"key": "value"},
)
result = engine.execute(req)
print(result.status)  # ExecutionStatus.COMPLETED
```
