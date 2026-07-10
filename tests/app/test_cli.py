"""Tests for CLI commands."""

from __future__ import annotations

from app.cli import main


class TestCLI:
    def test_version(self) -> None:
        rc = main(["version"])
        assert rc == 0

    def test_unknown_command(self) -> None:
        rc = main(["unknown-cmd"])
        assert rc != 0

    def test_no_command(self) -> None:
        rc = main([])
        assert rc == 2

    def test_start(self) -> None:
        rc = main(["start", "--no-apps"])
        assert rc == 0

    def test_status(self) -> None:
        rc = main(["status"])
        assert rc == 0

    def test_health(self) -> None:
        rc = main(["health"])
        assert rc == 0

    def test_version_output(self, capsys: pytest.CaptureFixture[str]) -> None:
        main(["version"])
        captured = capsys.readouterr()
        assert "JARVIS" in captured.out

    def test_config(self) -> None:
        rc = main(["config"])
        assert rc == 0

    def test_config_show_all(self) -> None:
        rc = main(["config", "--show-all"])
        assert rc == 0

    def test_doctor(self) -> None:
        rc = main(["doctor"])
        assert rc == 0

    def test_test_command(self) -> None:
        rc = main(["test"])
        assert rc == 0

    def test_restart(self) -> None:
        rc = main(["restart", "--no-apps"])
        assert rc == 0

    def test_stop(self) -> None:
        rc = main(["stop"])
        assert rc == 0

    def test_logs_when_running(self) -> None:
        rc = main(["logs", "--tail", "5"])
        assert rc in (0, 1)
