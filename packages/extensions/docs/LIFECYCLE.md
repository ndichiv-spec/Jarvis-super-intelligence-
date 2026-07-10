# Extension Lifecycle

## State Machine

The extension lifecycle is governed by a strict state machine defined in `lifecycle.py`. Each transition is explicitly enumerated; invalid transitions raise `ValueError`.

```
                    ┌──────────────────────────────────────┐
                    │                                      │
                    v                                      │
              ┌──────────┐     INSTALL    ┌──────────┐    │
              │DISCOVERED│───────────────>│ INSTALLED │────┘
              └──────────┘                └──────────┘
                    │                          │
                    │                     ┌────┼────┐
                    │                     │    │    │
                    │                     v    v    v
                    │               ┌─────────┐ │ ┌──────────┐
                    └──────────────>│ REMOVED │ │ │ UPDATING │
                                   └─────────┘ │ └──────────┘
                                               │       │
                                               │       v
                                               │  ┌──────────┐
                                               │  │ VERIFIED │
                                               │  └──────────┘
                                               │       │
                                               │       v
                                               │  ┌──────────┐
                                               │  │ACTIVATED │
                                               │  └──────────┘
                                               │    │    │
                                               │    │    v
                                               │    │  ┌───────┐
                                               │    │  │ PAUSED│
                                               │    │  └───────┘
                                               │    │    │
                                               │    v    v
                                               │  ┌──────────┐
                                               │  │ DISABLED │
                                               │  └──────────┘
                                               │
                                               v
                                         ┌──────────┐
                                         │  FAILED  │
                                         └──────────┘
```

## Transition Table

| From | To | Description |
|------|-----|-------------|
| DISCOVERED | INSTALLED | Extension discovered → ready for installation |
| DISCOVERED | REMOVED | Abandon discovery |
| INSTALLED | VERIFIED | Dependencies resolved, platform compatibility confirmed |
| INSTALLED | ACTIVATED | Direct activation (when no verification needed) |
| INSTALLED | DISABLED | Mark as disabled after install |
| INSTALLED | UPDATING | Begin update process |
| INSTALLED | REMOVED | Remove before activation |
| VERIFIED | ACTIVATED | Activate verified extension |
| VERIFIED | DISABLED | Disable verified extension |
| VERIFIED | REMOVED | Remove verified extension |
| ACTIVATED | PAUSED | Temporarily suspend (capabilities unregistered) |
| ACTIVATED | DISABLED | Permanently disable (capabilities, permissions, events revoked) |
| ACTIVATED | UPDATING | Begin update while active |
| ACTIVATED | REMOVED | Remove active extension |
| PAUSED | ACTIVATED | Resume from paused |
| PAUSED | DISABLED | Disable from paused |
| PAUSED | REMOVED | Remove while paused |
| DISABLED | ACTIVATED | Re-enable (return to activated) |
| DISABLED | UPDATING | Begin update while disabled |
| DISABLED | REMOVED | Remove while disabled |
| UPDATING | VERIFIED | Update complete, re-verify |
| UPDATING | FAILED | Update failed |
| UPDATING | DISABLED | Revert to disabled after failed update |
| FAILED | DISABLED | Acknowledge failure, disable |
| FAILED | REMOVED | Remove failed extension |
| REMOVED | *(none)* | Terminal state |

## Key Behavior

- **Activation** registers all declared capabilities in the `CapabilityRegistry` and grants all declared permissions.
- **Deactivation** (→ PAUSED) clears registered capabilities but retains permissions.
- **Disable** clears capabilities, revokes all permissions, and unsubscribes from all events.
- **Update** transitions through `UPDATING → VERIFIED`, replacing the manifest with an updated version.
- **Remove** transitions to `REMOVED` (terminal), then cleans up all subsystem state.

## Valid Transitions API

```python
lm = InMemoryLifecycleManager()
lm.can_transition(DISCOVERED, INSTALLED)   # True
lm.can_transition(DISCOVERED, ACTIVATED)   # False
lm.valid_transitions(DISCOVERED)           # (INSTALLED, REMOVED)
```

## Edge Cases

- A transition from `REMOVED` to any other state is **always invalid** — removal is terminal.
- `INSTALLED → ACTIVATED` is allowed when no explicit verification step is needed.
- `DISABLED → ACTIVATED` is allowed (re-enable without going through INSTALLED).
