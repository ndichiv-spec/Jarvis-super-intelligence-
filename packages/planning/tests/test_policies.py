from jarvis_planning.policies import CompletionCriteria, ExecutionPolicy, RetryPolicy


class TestRetryPolicy:
    def test_defaults(self) -> None:
        p = RetryPolicy()
        assert p.max_retries == 3
        assert p.delay_seconds == 1.0
        assert p.backoff_multiplier == 2.0

    def test_next_delay(self) -> None:
        p = RetryPolicy()
        assert p.next_delay(0) == 1.0
        assert p.next_delay(1) == 2.0
        assert p.next_delay(2) == 4.0

    def test_next_delay_capped(self) -> None:
        p = RetryPolicy(max_delay_seconds=5.0)
        assert p.next_delay(5) == 5.0

    def test_should_retry_under_limit(self) -> None:
        p = RetryPolicy(max_retries=3)
        assert p.should_retry(0) is True
        assert p.should_retry(2) is True

    def test_should_retry_at_limit(self) -> None:
        p = RetryPolicy(max_retries=3)
        assert p.should_retry(3) is False

    def test_retryable_on_filter(self) -> None:
        p = RetryPolicy(max_retries=3, retryable_on={"timeout", "network"})
        assert p.should_retry(0, "timeout") is True
        assert p.should_retry(0, "permission") is False

    def test_to_dict(self) -> None:
        p = RetryPolicy(max_retries=3, retryable_on={"timeout"})
        d = p.to_dict()
        assert d["max_retries"] == 3
        assert d["retryable_on"] == ["timeout"]


class TestCompletionCriteria:
    def test_default_is_satisfied_with_outputs(self) -> None:
        c = CompletionCriteria()
        assert c.is_satisfied({"result": "ok"}, {}) is True

    def test_require_all_outputs(self) -> None:
        c = CompletionCriteria(require_all_outputs=True)
        assert c.is_satisfied({}, {}) is False
        assert c.is_satisfied({"data": "value"}, {}) is True

    def test_min_confidence(self) -> None:
        c = CompletionCriteria(min_confidence=0.8)
        assert c.is_satisfied({"data": "v"}, {"confidence": 0.9}) is True
        assert c.is_satisfied({"data": "v"}, {"confidence": 0.5}) is False

    def test_custom_check(self) -> None:
        c = CompletionCriteria(custom_check=lambda d: d.get("status") == "ok")
        assert c.is_satisfied({"status": "ok"}, {}) is True
        assert c.is_satisfied({"status": "fail"}, {}) is False

    def test_to_dict(self) -> None:
        c = CompletionCriteria(require_verification=True)
        d = c.to_dict()
        assert d["require_verification"] is True


class TestExecutionPolicy:
    def test_defaults(self) -> None:
        p = ExecutionPolicy()
        assert p.max_concurrent_tasks == 5
        assert p.allow_parallel is True

    def test_custom(self) -> None:
        p = ExecutionPolicy(max_concurrent_tasks=2, allow_parallel=False)
        assert p.max_concurrent_tasks == 2
        assert p.allow_parallel is False

    def test_to_dict(self) -> None:
        p = ExecutionPolicy(timeout_seconds=30.0)
        d = p.to_dict()
        assert d["timeout_seconds"] == 30.0
