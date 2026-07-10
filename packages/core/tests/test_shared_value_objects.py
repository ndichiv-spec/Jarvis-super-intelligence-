from datetime import UTC

from jarvis_core.domain.shared.value_objects import DomainIdentifier, Timestamp, Version


def test_identifier_creation_is_unique() -> None:
    assert DomainIdentifier.new() != DomainIdentifier.new()


def test_timestamp_now_is_timezone_aware() -> None:
    assert Timestamp.now().value.tzinfo is UTC


def test_version_string() -> None:
    assert str(Version(major=1, minor=2, patch=3)) == "1.2.3"
