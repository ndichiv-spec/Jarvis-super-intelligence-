# Agent Lifecycle

## State Machine

Every agent in the platform is governed by a strictly enforced state machine. Each transition must be explicitly allowed by the transition table.

## State Diagram

```
                CREATED
                   │
                   ▼
             INITIALIZING
               │      │
               ▼      ▼
            READY   FAILED
         ┌───│───┐     │
         ▼   ▼   ▼     ▼
       BUSY PAUSED WAITING
         │   │   │
         ▼   ▼   ▼
         SUSPENDED
            │
            ▼
        RECOVERING
         │      │
         ▼      ▼
       READY  FAILED
         │
         ▼
       RETIRED (terminal)
```

## Transition Table

| From | To |
|------|----|
| CREATED | INITIALIZING, RETIRED |
| INITIALIZING | READY, FAILED, RETIRED |
| READY | BUSY, PAUSED, SUSPENDED, RETIRED, WAITING |
| BUSY | READY, PAUSED, WAITING, FAILED, SUSPENDED |
| PAUSED | READY, BUSY, SUSPENDED, RETIRED |
| WAITING | READY, BUSY, PAUSED, SUSPENDED |
| SUSPENDED | READY, RECOVERING, RETIRED |
| RETIRED | *(terminal — no transitions out)* |
| FAILED | RECOVERING, RETIRED, READY |
| RECOVERING | READY, FAILED, RETIRED |

## Usage

```python
from jarvis_agents import InMemoryLifecycleManager

mgr = InMemoryLifecycleManager()
mgr.initialize("agent-001")
mgr.transition("agent-001", AgentStatus.INITIALIZING)
mgr.transition("agent-001", AgentStatus.READY)
```

Through the kernel:

```python
kernel.activate_agent("agent-001")
kernel.suspend_agent("agent-001")
kernel.recover_agent("agent-001")
kernel.retire_agent("agent-001")
```
