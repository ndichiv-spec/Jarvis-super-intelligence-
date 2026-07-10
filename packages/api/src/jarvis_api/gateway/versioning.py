from __future__ import annotations

from dataclasses import dataclass

from jarvis_api.gateway.errors import GatewayException


@dataclass(frozen=True, order=True, slots=True)
class ApiVersion:
    major: int
    minor: int
    patch: int

    @classmethod
    def parse(cls, raw_version: str) -> ApiVersion:
        parts = raw_version.split(".")
        if len(parts) != 3 or not all(part.isdigit() for part in parts):
            raise GatewayException.validation(
                "API version must follow semantic format MAJOR.MINOR.PATCH",
                details={"version": raw_version},
            )
        return cls(major=int(parts[0]), minor=int(parts[1]), patch=int(parts[2]))

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"


@dataclass(frozen=True, slots=True)
class VersionRecord:
    version: ApiVersion
    deprecated: bool = False
    replacement: ApiVersion | None = None
    documentation_reference: str = ""
    migration_guidance: str = ""


@dataclass(frozen=True, slots=True)
class VersionResolution:
    requested: ApiVersion
    resolved: ApiVersion
    compatibility: bool
    deprecation_notice: str | None = None
    migration_guidance: str | None = None


class ApiVersionManager:
    def __init__(self) -> None:
        self._records: dict[ApiVersion, VersionRecord] = {}

    def register(
        self,
        version: str | ApiVersion,
        *,
        deprecated: bool = False,
        replacement: str | ApiVersion | None = None,
        documentation_reference: str = "",
        migration_guidance: str = "",
    ) -> None:
        resolved_version = ApiVersion.parse(version) if isinstance(version, str) else version
        replacement_version: ApiVersion | None
        if isinstance(replacement, str):
            replacement_version = ApiVersion.parse(replacement)
        else:
            replacement_version = replacement

        self._records[resolved_version] = VersionRecord(
            version=resolved_version,
            deprecated=deprecated,
            replacement=replacement_version,
            documentation_reference=documentation_reference,
            migration_guidance=migration_guidance,
        )

    def resolve(self, requested_version: str) -> VersionResolution:
        if not self._records:
            raise GatewayException.infrastructure("No API versions have been registered")

        requested = ApiVersion.parse(requested_version)
        exact_record = self._records.get(requested)

        if exact_record is not None:
            return self._to_resolution(requested, exact_record)

        same_major_records = [
            record
            for record in self._records.values()
            if record.version.major == requested.major
        ]
        if not same_major_records:
            raise GatewayException.policy_violation(
                "Requested API major version is not supported",
                details={"requested": requested_version},
            )

        compatible_candidates = [
            record
            for record in same_major_records
            if record.version <= requested
        ]
        selected = max(compatible_candidates or same_major_records, key=lambda record: record.version)
        return self._to_resolution(requested, selected)

    def list_versions(self) -> tuple[VersionRecord, ...]:
        return tuple(sorted(self._records.values(), key=lambda record: record.version))

    def _to_resolution(self, requested: ApiVersion, record: VersionRecord) -> VersionResolution:
        compatibility = requested.major == record.version.major
        if not compatibility:
            raise GatewayException.policy_violation(
                "Incompatible API major version",
                details={"requested": str(requested), "resolved": str(record.version)},
            )

        deprecation_notice: str | None = None
        if record.deprecated:
            replacement = str(record.replacement) if record.replacement is not None else "n/a"
            deprecation_notice = (
                f"API version {record.version} is deprecated; replacement: {replacement}"
            )

        return VersionResolution(
            requested=requested,
            resolved=record.version,
            compatibility=compatibility,
            deprecation_notice=deprecation_notice,
            migration_guidance=record.migration_guidance or None,
        )
