from pathlib import Path


def test_all_required_packages_present() -> None:
    required = {
        "core",
        "brain",
        "ai",
        "memory",
        "knowledge",
        "automation",
        "orchestration",
        "webintel",
        "desktopintel",
        "vision",
        "voice",
        "security",
        "api",
        "infrastructure",
    }
    present = {p.name for p in Path("packages").iterdir() if p.is_dir()}
    assert required.issubset(present)
