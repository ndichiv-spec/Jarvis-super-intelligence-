from jarvis_planning.state_machine import (
    TaskState,
    TaskStateMachine,
    TransitionError,
    validate_transition,
)


class TestTaskState:
    def test_terminal_states(self) -> None:
        assert TaskState.COMPLETED.terminal is True
        assert TaskState.FAILED.terminal is True
        assert TaskState.CANCELLED.terminal is True
        assert TaskState.PLANNED.terminal is False
        assert TaskState.RUNNING.terminal is False

    def test_active_states(self) -> None:
        assert TaskState.RUNNING.active is True
        assert TaskState.WAITING.active is True
        assert TaskState.COMPLETED.active is False
        assert TaskState.PLANNED.active is False


class TestValidateTransition:
    def test_valid_transition(self) -> None:
        validate_transition("t1", TaskState.PLANNED, TaskState.READY)

    def test_invalid_transition(self) -> None:
        try:
            validate_transition("t1", TaskState.PLANNED, TaskState.COMPLETED)
            assert False
        except TransitionError as e:
            assert e.task_id == "t1"
            assert e.current == TaskState.PLANNED
            assert e.target == TaskState.COMPLETED

    def test_terminal_has_no_outgoing(self) -> None:
        for terminal in (TaskState.COMPLETED, TaskState.FAILED, TaskState.CANCELLED):
            try:
                validate_transition("t1", terminal, TaskState.PLANNED)
                assert False, f"{terminal} should not allow transitions"
            except TransitionError:
                pass


class TestTaskStateMachine:
    def test_initial_state(self) -> None:
        sm = TaskStateMachine("t1")
        assert sm.state == TaskState.PLANNED

    def test_transition_to_valid(self) -> None:
        sm = TaskStateMachine("t1")
        sm.transition_to(TaskState.READY)
        assert sm.state == TaskState.READY
        assert len(sm.history) == 1
        assert sm.history[0].from_state == TaskState.PLANNED
        assert sm.history[0].to_state == TaskState.READY

    def test_transition_to_invalid(self) -> None:
        sm = TaskStateMachine("t1")
        try:
            sm.transition_to(TaskState.COMPLETED)
            assert False
        except TransitionError:
            pass
        assert sm.state == TaskState.PLANNED

    def test_can_transition_to(self) -> None:
        sm = TaskStateMachine("t1")
        assert sm.can_transition_to(TaskState.READY) is True
        assert sm.can_transition_to(TaskState.COMPLETED) is False

    def test_full_workflow(self) -> None:
        sm = TaskStateMachine("t1")
        sm.transition_to(TaskState.READY)
        sm.transition_to(TaskState.RUNNING)
        sm.transition_to(TaskState.COMPLETED)
        assert sm.state == TaskState.COMPLETED

    def test_full_workflow_with_waiting(self) -> None:
        sm = TaskStateMachine("t1")
        sm.transition_to(TaskState.READY)
        sm.transition_to(TaskState.WAITING)
        sm.transition_to(TaskState.READY)
        sm.transition_to(TaskState.RUNNING)
        sm.transition_to(TaskState.COMPLETED)
        assert sm.state == TaskState.COMPLETED
        assert len(sm.history) == 5

    def test_failure_path(self) -> None:
        sm = TaskStateMachine("t1")
        sm.transition_to(TaskState.READY)
        sm.transition_to(TaskState.RUNNING)
        sm.transition_to(TaskState.FAILED)
        assert sm.state == TaskState.FAILED

    def test_cancellation_path(self) -> None:
        sm = TaskStateMachine("t1")
        sm.transition_to(TaskState.CANCELLED)
        assert sm.state == TaskState.CANCELLED

    def test_elapsed_in_state(self) -> None:
        sm = TaskStateMachine("t1")
        assert sm.elapsed_in_state == 0.0
        sm.transition_to(TaskState.READY)
        elapsed = sm.elapsed_in_state
        assert elapsed >= 0.0

    def test_summary(self) -> None:
        sm = TaskStateMachine("t1")
        sm.transition_to(TaskState.READY, "proceed")
        s = sm.summary()
        assert s["task_id"] == "t1"
        assert s["state"] == "READY"
        assert len(s["history"]) == 1
        assert s["history"][0]["reason"] == "proceed"
