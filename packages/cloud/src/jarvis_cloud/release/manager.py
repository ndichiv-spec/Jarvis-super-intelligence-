"""Release Manager - semantic versioning, release channels, rollback."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any


class ReleaseChannel(StrEnum):
    stable = "stable"
    beta = "beta"
    alpha = "alpha"
    nightly = "nightly"


class ReleaseStatus(StrEnum):
    drafted = "drafted"
    validated = "validated"
    deployed = "deployed"
    rolled_back = "rolled_back"
    failed = "failed"


@dataclass(frozen=True)
class SemVer:
    major: int
    minor: int
    patch: int
    pre_release: str | None = None
    build: str | None = None

    def __str__(self) -> str:
        base = f"{self.major}.{self.minor}.{self.patch}"
        if self.pre_release:
            base += f"-{self.pre_release}"
        if self.build:
            base += f"+{self.build}"
        return base

    @classmethod
    def parse(cls, version: str) -> SemVer:
        pattern = r"^(\d+)\.(\d+)\.(\d+)(?:-([\w.]+))?(?:\+([\w.]+))?$"
        m = re.match(pattern, version)
        if not m:
            raise ValueError(f"Invalid semantic version: {version}")
        return cls(
            major=int(m.group(1)),
            minor=int(m.group(2)),
            patch=int(m.group(3)),
            pre_release=m.group(4),
            build=m.group(5),
        )


@dataclass(frozen=True)
class ReleaseArtifact:
    service: str
    image: str
    tag: str
    digest: str | None = None
    checksum: str | None = None


@dataclass(frozen=True)
class Release:
    version: SemVer
    channel: ReleaseChannel
    artifacts: list[ReleaseArtifact] = field(default_factory=list)
    changelog: str = ""
    status: ReleaseStatus = ReleaseStatus.drafted
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    deployed_at: datetime | None = None
    deployed_by: str = ""


class ReleaseManager:
    def __init__(self) -> None:
        self._releases: list[Release] = []
        self._current: Release | None = None

    @property
    def current(self) -> Release | None:
        return self._current

    @property
    def releases(self) -> list[Release]:
        return list(self._releases)

    def create_release(self, version: str, channel: ReleaseChannel = ReleaseChannel.stable, changelog: str = "") -> Release:
        sv = SemVer.parse(version)
        release = Release(version=sv, channel=channel, changelog=changelog)
        self._releases.append(release)
        return release

    def promote(self, version: str, to_channel: ReleaseChannel) -> Release | None:
        for r in self._releases:
            if str(r.version) == version:
                promoted = Release(
                    version=r.version,
                    channel=to_channel,
                    artifacts=r.artifacts,
                    changelog=r.changelog,
                    status=r.status,
                    created_at=r.created_at,
                )
                self._releases = [promoted if str(rr.version) == version else rr for rr in self._releases]
                return promoted
        return None

    def deploy(self, version: str, deployed_by: str = "system") -> Release | None:
        for r in self._releases:
            if str(r.version) == version and r.status == ReleaseStatus.validated:
                deployed = Release(
                    version=r.version,
                    channel=r.channel,
                    artifacts=r.artifacts,
                    changelog=r.changelog,
                    status=ReleaseStatus.deployed,
                    created_at=r.created_at,
                    deployed_at=datetime.now(timezone.utc),
                    deployed_by=deployed_by,
                )
                self._releases = [deployed if str(rr.version) == version else rr for rr in self._releases]
                self._current = deployed
                return deployed
        return None

    def rollback(self, version: str, to_version: str) -> Release | None:
        target: Release | None = None
        for r in self._releases:
            if str(r.version) == version:
                rolled = Release(
                    version=r.version,
                    channel=r.channel,
                    artifacts=r.artifacts,
                    changelog=r.changelog,
                    status=ReleaseStatus.rolled_back,
                    created_at=r.created_at,
                    deployed_at=r.deployed_at,
                    deployed_by=r.deployed_by,
                )
                self._releases = [rolled if str(rr.version) == version else rr for rr in self._releases]
            if str(r.version) == to_version and r.status in (ReleaseStatus.deployed, ReleaseStatus.validated):
                target = r
        if target:
            self._current = target
            return target
        return None

    def list_releases(self, channel: ReleaseChannel | None = None) -> list[Release]:
        if channel is None:
            return self._releases
        return [r for r in self._releases if r.channel == channel]

    def validate(self, version: str) -> list[str]:
        issues: list[str] = []
        for r in self._releases:
            if str(r.version) == version:
                if not r.artifacts:
                    issues.append(f"Release {version}: no artifacts defined")
                return issues
        issues.append(f"Release {version} not found")
        return issues
