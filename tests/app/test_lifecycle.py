"""Tests for lifecycle manager."""

from __future__ import annotations

import pytest

from app.lifecycle import LifecycleError, LifecycleManager, LifecycleState


class TestLifecycleManager:
    def test_initial_state(self) -> None:
        mgr = LifecycleManager()
        assert mgr.state == LifecycleState.created

    def test_initial_history_empty(self) -> None:
        mgr = LifecycleManager()
        assert mgr.history == []

    def test_initial_elapsed_zero(self) -> None:
        mgr = LifecycleManager()
        assert mgr.elapsed_in_state() == 0.0

    def test_valid_transition(self) -> None:
        mgr = LifecycleManager()
        mgr.transition(LifecycleState.initializing)
        assert mgr.state == LifecycleState.initializing

    def test_transition_appends_history(self) -> None:
        mgr = LifecycleManager()
        mgr.transition(LifecycleState.initializing, reason="booting")
        assert len(mgr.history) == 1
        assert mgr.history[0].from_state == LifecycleState.created
        assert mgr.history[0].to_state == LifecycleState.initializing
        assert mgr.history[0].reason == "booting"

    def test_invalid_transition_raises(self) -> None:
        mgr = LifecycleManager()
        with pytest.raises(LifecycleError) as exc:
            mgr.transition(LifecycleState.ready)
        assert "created" in str(exc.value)
        assert "ready" in str(exc.value)

    def test_transition_from_stopped_raises(self) -> None:
        mgr = LifecycleManager()
        mgr.transition(LifecycleState.initializing)
        mgr.transition(LifecycleState.starting)
        mgr.transition(LifecycleState.ready)
        mgr.transition(LifecycleState.stopping)
        mgr.transition(LifecycleState.stopped)
        with pytest.raises(LifecycleError):
            mgr.transition(LifecycleState.ready)

    def test_transition_from_failed_raises(self) -> None:
        mgr = LifecycleManager()
        mgr.transition(LifecycleState.failed)
        with pytest.raises(LifecycleError):
            mgr.transition(LifecycleState.initializing)

    def test_can_transition_to(self) -> None:
        mgr = LifecycleManager()
        assert mgr.can_transition_to(LifecycleState.initializing)
        assert mgr.can_transition_to(LifecycleState.failed)
        assert not mgr.can_transition_to(LifecycleState.ready)

    def test_full_lifecycle(self) -> None:
        mgr = LifecycleManager()
        assert mgr.state == LifecycleState.created
        mgr.transition(LifecycleState.initializing)
        assert mgr.state == LifecycleState.initializing
        mgr.transition(LifecycleState.starting)
        assert mgr.state == LifecycleState.starting
        mgr.transition(LifecycleState.ready)
        assert mgr.state == LifecycleState.ready
        mgr.transition(LifecycleState.degraded)
        assert mgr.state == LifecycleState.degraded
        mgr.transition(LifecycleState.ready)
        assert mgr.state == LifecycleState.ready
        mgr.transition(LifecycleState.stopping)
        assert mgr.state == LifecycleState.stopping
        mgr.transition(LifecycleState.stopped)
        assert mgr.state == LifecycleState.stopped

    def test_elapsed_in_state_increases(self) -> None:
        mgr = LifecycleManager()
        mgr.transition(LifecycleState.initializing)
        import time
        time.sleep(0.01)
        assert mgr.elapsed_in_state() > 0.0

    def test_transition_with_reason_empty(self) -> None:
        mgr = LifecycleManager()
        mgr.transition(LifecycleState.initializing)
        assert mgr.history[-1].reason == ""

    def test_degraded_to_failed(self) -> None:
        mgr = LifecycleManager()
        mgr.transition(LifecycleState.initializing)
        mgr.transition(LifecycleState.starting)
        mgr.transition(LifecycleState.degraded)
        mgr.transition(LifecycleState.failed)
        assert mgr.state == LifecycleState.failed

    def test_failed_only_to_stopping(self) -> None:
        mgr = LifecycleManager()
        mgr.transition(LifecycleState.failed)
        for s in LifecycleState:
            if s == LifecycleState.stopping:
                assert mgr.can_transition_to(s)
            elif s != LifecycleState.failed:
                assert not mgr.can_transition_to(s)

    def test_stopped_no_transitions(self) -> None:
        mgr = LifecycleManager()
        mgr.transition(LifecycleState.initializing)
        mgr.transition(LifecycleState.starting)
        mgr.transition(LifecycleState.ready)
        mgr.transition(LifecycleState.stopping)
        mgr.transition(LifecycleState.stopped)
        for s in LifecycleState:
            if s != LifecycleState.stopped:
                assert not mgr.can_transition_to(s)
