# Phase 5 — Developer Guide

## Quick Start

1. Create an `ExecutionContext` at request boundary.
2. Instantiate `MessageBus` (or individual `EventBus`, `CommandBus`, `QueryBus`).
3. Register command/query handlers and event subscriptions.
4. Publish/dispatch messages through async APIs.

## Example

```python
from jarvis_communication import CommandBus, CommandMessage, ExecutionContext

bus = CommandBus()

async def create_user(command: CommandMessage[dict], context: ExecutionContext) -> dict:
    return {"id": command.payload["id"], "source": context.source}

bus.register_handler("command.user.create", create_user)
context = ExecutionContext.new(source="api")
result = await bus.dispatch(CommandMessage(message_name="command.user.create", payload={"id": "u-1"}), context=context)
```

## Best Practices

- Keep handlers pure and side-effect aware.
- Use middleware for cross-cutting concerns (logging, retries, policy checks).
- Use `ExecutionContext.child()` when invoking nested operations.
- Prefer events for decoupled asynchronous propagation.
- Reserve commands for state changes and queries for reads.
