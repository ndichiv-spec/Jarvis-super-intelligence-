"""Tests for Release Management."""

from jarvis_cloud.release.manager import ReleaseManager, ReleaseChannel, SemVer


class TestSemVer:
    def test_parse_stable(self):
        v = SemVer.parse("1.2.3")
        assert v.major == 1
        assert v.minor == 2
        assert v.patch == 3

    def test_parse_pre_release(self):
        v = SemVer.parse("2.0.0-beta.1")
        assert v.pre_release == "beta.1"

    def test_parse_build(self):
        v = SemVer.parse("1.0.0+build123")
        assert v.build == "build123"

    def test_parse_full(self):
        v = SemVer.parse("1.0.0-alpha+001")
        assert v.pre_release == "alpha"
        assert v.build == "001"

    def test_str(self):
        v = SemVer(1, 2, 3)
        assert str(v) == "1.2.3"

    def test_str_pre_release(self):
        v = SemVer(2, 0, 0, pre_release="beta.1")
        assert str(v) == "2.0.0-beta.1"

    def test_invalid(self):
        try:
            SemVer.parse("invalid")
            assert False, "Should raise ValueError"
        except ValueError:
            pass


class TestReleaseManager:
    def setup_method(self):
        self.mgr = ReleaseManager()

    def test_create_release(self):
        release = self.mgr.create_release("1.0.0", ReleaseChannel.stable, "Initial release")
        assert str(release.version) == "1.0.0"
        assert release.channel == ReleaseChannel.stable
        assert release.status.value == "drafted"

    def test_promote(self):
        self.mgr.create_release("1.0.0-beta", ReleaseChannel.beta)
        promoted = self.mgr.promote("1.0.0-beta", ReleaseChannel.stable)
        assert promoted is not None
        assert promoted.channel == ReleaseChannel.stable

    def test_list_releases(self):
        self.mgr.create_release("1.0.0", ReleaseChannel.stable)
        self.mgr.create_release("1.1.0-beta", ReleaseChannel.beta)
        assert len(self.mgr.list_releases()) == 2
        assert len(self.mgr.list_releases(ReleaseChannel.stable)) == 1
        assert len(self.mgr.list_releases(ReleaseChannel.beta)) == 1

    def test_validate(self):
        release = self.mgr.create_release("1.0.0")
        issues = self.mgr.validate("1.0.0")
        assert isinstance(issues, list)

    def test_validate_nonexistent(self):
        issues = self.mgr.validate("9.9.9")
        assert len(issues) > 0
