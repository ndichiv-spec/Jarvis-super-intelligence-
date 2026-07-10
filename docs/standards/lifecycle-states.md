# Lifecycle State Machine

The platform lifecycle is managed by `LifecycleManager` (`app/lifecycle.py`), a strict finite state machine with validated transitions and an append-only event history.

## States

| State | Value | Meaning |
|---|---|---|
| `CREATED` | `created` | Initial state after construction |
| `INITIALIZING` | `initializing` | Kernel initialization in progress |
| `STARTING` | `starting` | Platform services being started |
| `READY` | `ready` | All services running normally |
| `DEGRADED` | `degraded` | Running with reduced capability |
| `STOPPING` | `stopping` | Graceful shutdown in progress |
| `STOPPED` | `stopped` | Platform fully stopped (terminal) |
| `FAILED` | `failed` | Irrecoverable failure (terminal) |

## Valid Transitions

```
                    ┌─────────┐
                    │ CREATED │
                    └────┬────┘
                    ┌────┴────┐
                    ▼         ▼
             ┌──────────┐  ┌──────┐
             │INITIALIZING│  │FAILED│
             └─────┬─────┘  └──────┘
                   │           ▲
                   ▼           │
             ┌─────────┐       │
             │ STARTING├───────┘
             └──┬──┬───┘
          ┌─────┘  └──────┐
          ▼                ▼
      ┌───────┐      ┌─────────┐
      │ READY │◄────►│ DEGRADED│
      └───┬───┘      └──┬──┬───┘
          │             │  └──────┐
          └──────┐ ┌────┘        ▼
                 ▼ ▼          ┌──────┐
             ┌─────────┐      │FAILED│
             │STOPPING │      └──────┘
             └────┬────┘
                  ▼
             ┌─────────┐
             │ STOPPED │
             └─────────┘
```

### Transition Table (from source code)

| From | To |
|---|---|
| `CREATED` | `INITIALIZING`, `FAILED` |
| `INITIALIZING` | `STARTING`, `FAILED` |
| `STARTING` | `READY`, `DEGRADED`, `FAILED` |
| `READY` | `STOPPING`, `DEGRADED`, `FAILED` |
| `DEGRADED` | `READY`, `STOPPING`, `FAILED` |
| `STOPPING` | `STOPPED`, `FAILED` |
| `STOPPED` | _(none — terminal)_ |
| `FAILED` | _(none — terminal)_ |

## LifecycleManager API

```python
from app.lifecycle import LifecycleManager, LifecycleState, LifecycleEvent

mgr = LifecycleManager()
mgr.state                        # → LifecycleState.created
mgr.transition(LifecycleState.initializing, reason="booting")
mgr.can_transition_to(LifecycleState.ready)  # → False
mgr.history                      # → [LifecycleEvent(...)]
mgr.elapsed_in_state()           # → float seconds
```

### LifecycleEvent

A frozen dataclass recorded on every transition:

```python
@dataclass(frozen=True)
class LifecycleEvent:
    from_state: LifecycleState
    to_state: LifecycleState
    timestamp: datetime          # UTC
    reason: str                  # optional
```

## Invalid Transitions

Attempting an invalid transition raises `LifecycleError`:

```python
from app.lifecycle import LifecycleError

mgr = LifecycleManager()
# Created → ready is invalid:
mgr.transition(LifecycleState.ready)  # raises LifecycleError
# "Cannot transition from created to ready"
```

Both `STOPPED` and `FAILED` are terminal states — no further transitions are allowed from either.

## Standard Lifecycle

The normal happy-path sequence:

```
CREATED → INITIALIZING → STARTING → READY → STOPPING → STOPPED
```

## Degraded Lifecycle

When one or more services fail during startup or runtime:

```
CREATED → INITIALIZING → STARTING → DEGRADED → READY (if recovered)
                                            → STOPPING → STOPPED
                                            → FAILED
```
