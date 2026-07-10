# JARVIS Communication Developer Guide

## Getting Started

### Installation

```bash
cd packages/communication
uv sync
```

### Running Tests

```bash
cd packages/communication
$env:PYTHONPATH = "src"; uv run --no-project pytest tests/ -v
```

## Usage Examples

### Send a Message

```python
from jarvis_communication.engine import CommunicationEngine
from jarvis_communication.models import CommunicationMessage
from jarvis_communication.context import ExecutionContext

engine = CommunicationEngine()
context = ExecutionContext.new(source="my-app")

msg = CommunicationMessage(
    sender="user-1",
    receiver="JARVIS",
    body="Hello, JARVIS!",
    subject="Greeting",
)

sent = await engine.send_message(msg, context=context)
print(f"Sent: {sent.message_id}")
```

### Create a Conversation

```python
conv = await engine.conversations.create(
    "Project Discussion",
    ("user-1", "user-2", "JARVIS"),
    context=context,
)
```

### Send a Notification

```python
from jarvis_communication.models import Notification, NotificationLevel

notification = Notification(
    title="Task Completed",
    body="Your analysis task has finished",
    level=NotificationLevel.SUCCESS,
    source="agents",
    target_user="user-1",
)

result = await engine.send_notification(notification, context=context)
```

### Stream AI Responses

```python
async def my_response_generator():
    words = ["I", "think", "therefore", "I", "am"]
    for word in words:
        yield word
        await asyncio.sleep(0.1)

await engine.streaming.stream_ai_response(
    "stream-1",
    my_response_generator(),
    context=context,
)

async for chunk in engine.streaming.subscribe("stream-1", context=context):
    print(chunk)
```

### Track Presence

```python
from jarvis_communication.models import PresenceStatus

await engine.presence.set_online("user-1", context=context)
await engine.presence.set_busy("user-1", current_activity="Analyzing data", context=context)
```

### Send Email

```python
from jarvis_communication.email import EmailMessage

email = EmailMessage(
    to_addresses=("user@example.com",),
    subject="JARVIS Report",
    body_text="Your report is ready.",
    sender="jarvis@system.local",
)
await engine.email.send(email, context=context)
```

### Use Templates

```python
engine.templates.register_email_template(
    "task_complete",
    "Task Complete: {task_name}",
    "Hello {user}, your task '{task_name}' has been completed.",
)
result = engine.templates.render_email("task_complete", task_name="Data Analysis", user="Alice")
print(result["subject"])  # "Task Complete: Data Analysis"
```

### Audit Logging

```python
await engine.audit.log(
    action="message.sent",
    actor="user-1",
    target="message-123",
    details={"channel": "internal", "size": 1024},
    context=context,
)
```

## Architecture Extensions

### Adding a New Channel Type

1. Add the value to `ChannelType` enum in `models.py`
2. Implement channel-specific logic in the appropriate service
3. Add the channel to the `SUPPORTED_CHANNELS` in the communication architecture document

### Adding a New Notification Type

1. Add a helper method in `NotificationService` (e.g., `send_workflow_completion`)
2. The method creates a `Notification` with the appropriate source and level
3. Register the notification type in the documentation

### Adding a New Template Category

1. Use `register_*_template` methods in `TemplateEngine`
2. Add corresponding `render_*` methods
3. Templates use Python string `.format()` syntax
