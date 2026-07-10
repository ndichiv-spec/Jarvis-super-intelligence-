from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum, auto


class ExtensionStatus(Enum):
    DISCOVERED = auto()
    INSTALLED = auto()
    VERIFIED = auto()
    ACTIVATED = auto()
    PAUSED = auto()
    DISABLED = auto()
    UPDATING = auto()
    FAILED = auto()
    REMOVED = auto()


class ExtensionType(Enum):
    AI_PROVIDER = auto()
    KNOWLEDGE_CONNECTOR = auto()
    TOOL_PACK = auto()
    AUTOMATION_PACK = auto()
    UI_MODULE = auto()
    VOICE = auto()
    VISION = auto()
    ENTERPRISE_INTEGRATION = auto()


class CapabilityType(Enum):
    TOOL = auto()
    AGENT = auto()
    AI_PROVIDER = auto()
    WORKFLOW_TEMPLATE = auto()
    KNOWLEDGE_CONNECTOR = auto()
    UI_COMPONENT = auto()
    INTEGRATION = auto()
    SERVICE = auto()
    COMMAND = auto()
    EVENT_HANDLER = auto()


class PermissionScope(Enum):
    MEMORY_ACCESS = auto()
    KNOWLEDGE_ACCESS = auto()
    TOOL_REGISTRATION = auto()
    WORKFLOW_REGISTRATION = auto()
    WORKSPACE_ACCESS = auto()
    EVENT_SUBSCRIPTION = auto()
    COMMAND_REGISTRATION = auto()


class DependencyType(Enum):
    REQUIRED = auto()
    OPTIONAL = auto()


class CompatibilityLevel(Enum):
    COMPATIBLE = auto()
    INCOMPATIBLE = auto()
    DEPRECATED = auto()
    REQUIRES_UPDATE = auto()


@dataclass(frozen=True, slots=True)
class VersionInfo:
    major: int = 0
    minor: int = 0
    patch: int = 0
    pre_release: str | None = None
    build_metadata: str | None = None

    def __str__(self) -> str:
        base = f"{self.major}.{self.minor}.{self.patch}"
        if self.pre_release:
            base = f"{base}-{self.pre_release}"
        if self.build_metadata:
            base = f"{base}+{self.build_metadata}"
        return base

    @classmethod
    def parse(cls, version: str) -> VersionInfo:
        parts = version.split("+", 1)
        build = parts[1] if len(parts) > 1 else None
        parts = parts[0].split("-", 1)
        pre = parts[1] if len(parts) > 1 else None
        nums = parts[0].split(".")
        major = int(nums[0]) if len(nums) > 0 else 0
        minor = int(nums[1]) if len(nums) > 1 else 0
        patch = int(nums[2]) if len(nums) > 2 else 0
        return cls(major=major, minor=minor, patch=patch, pre_release=pre, build_metadata=build)

    def is_compatible_with(self, other: VersionInfo) -> bool:
        return self.major == other.major and self.minor >= other.minor

    def satisfies(self, constraint: str) -> bool:
        constraint = constraint.strip()
        if constraint.startswith(">="):
            min_version = VersionInfo.parse(constraint[2:].strip())
            if self.major != min_version.major:
                return self.major > min_version.major
            if self.minor != min_version.minor:
                return self.minor > min_version.minor
            return self.patch >= min_version.patch
        if constraint.startswith("^"):
            min_version = VersionInfo.parse(constraint[1:].strip())
            return self.major == min_version.major and (
                self.minor > min_version.minor
                or (self.minor == min_version.minor and self.patch >= min_version.patch)
            )
        if constraint.startswith("~"):
            min_version = VersionInfo.parse(constraint[1:].strip())
            return (
                self.major == min_version.major
                and self.minor == min_version.minor
                and self.patch >= min_version.patch
            )
        if constraint.startswith("=="):
            expected = VersionInfo.parse(constraint[2:].strip())
            return self == expected
        if constraint.startswith(">"):
            min_version = VersionInfo.parse(constraint[1:].strip())
            return self > min_version
        if constraint.startswith("<="):
            max_version = VersionInfo.parse(constraint[2:].strip())
            return self <= max_version
        if constraint.startswith("<"):
            max_version = VersionInfo.parse(constraint[1:].strip())
            return self < max_version
        return self == VersionInfo.parse(constraint)

    def __lt__(self, other: VersionInfo) -> bool:
        if self.major != other.major:
            return self.major < other.major
        if self.minor != other.minor:
            return self.minor < other.minor
        if self.patch != other.patch:
            return self.patch < other.patch
        if self.pre_release and not other.pre_release:
            return True
        if not self.pre_release and other.pre_release:
            return False
        return False

    def __le__(self, other: VersionInfo) -> bool:
        return self < other or self == other

    def __gt__(self, other: VersionInfo) -> bool:
        return not (self < other) and not (self == other)

    def __ge__(self, other: VersionInfo) -> bool:
        return not (self < other)
        return False


@dataclass(frozen=True, slots=True)
class CapabilityDefinition:
    capability_type: CapabilityType
    identifier: str
    name: str
    description: str = ""
    version: VersionInfo = field(default_factory=VersionInfo)


@dataclass(frozen=True, slots=True)
class DependencyDefinition:
    extension_id: str
    version_constraint: str = ">=0.0.0"
    dependency_type: DependencyType = DependencyType.REQUIRED


@dataclass(frozen=True, slots=True)
class PermissionRequest:
    permission_scope: PermissionScope
    reason: str = ""
    required: bool = True


@dataclass(frozen=True, slots=True)
class ResourceLimits:
    max_memory_mb: int = 0
    max_cpu_percent: int = 0
    max_storage_mb: int = 0
    max_network_requests: int = 0
    max_concurrent_tasks: int = 1


@dataclass(frozen=True, slots=True)
class IsolationPolicy:
    sandbox_enabled: bool = False
    resource_limits: ResourceLimits = field(default_factory=ResourceLimits)
    allowed_capabilities: tuple[CapabilityType, ...] = ()
    denied_capabilities: tuple[CapabilityType, ...] = ()
    security_policy_ref: str = ""


@dataclass(frozen=True, slots=True)
class ExtensionManifest:
    extension_id: str
    name: str
    version: VersionInfo
    publisher: str = ""
    description: str = ""
    license: str = ""
    capabilities: tuple[CapabilityDefinition, ...] = ()
    dependencies: tuple[DependencyDefinition, ...] = ()
    permissions: tuple[PermissionRequest, ...] = ()
    min_platform_version: VersionInfo = field(default_factory=VersionInfo)
    max_platform_version: VersionInfo | None = None
    extension_type: ExtensionType = ExtensionType.TOOL_PACK
    tags: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class CompatibilityIssue:
    code: str
    message: str
    severity: CompatibilityLevel


@dataclass(frozen=True, slots=True)
class CompatibilityReport:
    level: CompatibilityLevel
    issues: tuple[CompatibilityIssue, ...] = ()
    is_compatible: bool = True


@dataclass(frozen=True, slots=True)
class ExtensionMetadata:
    extension_id: str
    manifest: ExtensionManifest
    status: ExtensionStatus = ExtensionStatus.DISCOVERED
    installed_version: VersionInfo | None = None
    available_update: VersionInfo | None = None
    dependencies_resolved: bool = False
    compatibility: CompatibilityReport | None = None
    isolation_policy: IsolationPolicy = field(default_factory=IsolationPolicy)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    metadata: dict[str, str] = field(default_factory=dict)

    def with_status(self, status: ExtensionStatus) -> ExtensionMetadata:
        return ExtensionMetadata(
            extension_id=self.extension_id,
            manifest=self.manifest,
            status=status,
            installed_version=self.installed_version,
            available_update=self.available_update,
            dependencies_resolved=self.dependencies_resolved,
            compatibility=self.compatibility,
            isolation_policy=self.isolation_policy,
            created_at=self.created_at,
            updated_at=datetime.now(UTC),
            metadata=self.metadata,
        )


@dataclass(frozen=True, slots=True)
class ExtensionHealth:
    extension_id: str
    status: ExtensionStatus
    is_healthy: bool = True
    activation_count: int = 0
    failure_count: int = 0
    last_activated_at: datetime | None = None
    last_failure_at: datetime | None = None
    last_failure_message: str = ""
    total_runtime_ms: int = 0
    performance_metadata: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class BuiltInExtensionDefinition:
    extension_id: str
    name: str
    description: str
    extension_type: ExtensionType
    version: VersionInfo = field(default_factory=lambda: VersionInfo(1, 0, 0))
    publisher: str = "JARVIS Core"
    capabilities: tuple[CapabilityDefinition, ...] = ()
    permissions: tuple[PermissionRequest, ...] = ()
    dependencies: tuple[DependencyDefinition, ...] = ()
    is_built_in: bool = True
