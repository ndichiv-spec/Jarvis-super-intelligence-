from __future__ import annotations

import pytest
from jarvis_extensions.builtins import BUILT_IN_EXTENSIONS
from jarvis_extensions.capabilities import InMemoryCapabilityRegistry
from jarvis_extensions.compatibility import InMemoryCompatibilityEngine
from jarvis_extensions.dependency import InMemoryDependencyManager
from jarvis_extensions.events import InMemoryEventIntegration
from jarvis_extensions.health import InMemoryHealthMonitor
from jarvis_extensions.isolation import InMemoryIsolationManager
from jarvis_extensions.kernel import ExtensionKernel
from jarvis_extensions.lifecycle import InMemoryLifecycleManager
from jarvis_extensions.manifest import InMemoryManifestValidator
from jarvis_extensions.models import (
    CapabilityDefinition,
    CapabilityType,
    CompatibilityLevel,
    CompatibilityReport,
    DependencyDefinition,
    DependencyType,
    ExtensionHealth,
    ExtensionManifest,
    ExtensionMetadata,
    ExtensionStatus,
    ExtensionType,
    IsolationPolicy,
    PermissionRequest,
    PermissionScope,
    ResourceLimits,
    VersionInfo,
)
from jarvis_extensions.permissions import InMemoryPermissionManager
from jarvis_extensions.registry import InMemoryExtensionRegistry
from jarvis_extensions.version import InMemoryVersionManager

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def manifest() -> ExtensionManifest:
    return ExtensionManifest(
        extension_id="test.ext",
        name="Test Extension",
        version=VersionInfo(1, 0, 0),
        publisher="Test Publisher",
        description="A test extension",
        capabilities=(
            CapabilityDefinition(
                capability_type=CapabilityType.TOOL,
                identifier="test.cap.tool1",
                name="Tool 1",
            ),
        ),
        permissions=(
            PermissionRequest(
                permission_scope=PermissionScope.TOOL_REGISTRATION,
                reason="Register test tools",
            ),
        ),
    )


@pytest.fixture
def kernel() -> ExtensionKernel:
    return ExtensionKernel()


@pytest.fixture
def registry() -> InMemoryExtensionRegistry:
    return InMemoryExtensionRegistry()


# ---------------------------------------------------------------------------
# VersionInfo tests
# ---------------------------------------------------------------------------


class TestVersionInfo:
    def test_parse(self) -> None:
        v = VersionInfo.parse("1.2.3")
        assert v.major == 1
        assert v.minor == 2
        assert v.patch == 3

    def test_parse_with_pre_release(self) -> None:
        v = VersionInfo.parse("2.0.0-beta.1")
        assert v.major == 2
        assert v.pre_release == "beta.1"

    def test_parse_with_build(self) -> None:
        v = VersionInfo.parse("1.0.0+build42")
        assert v.build_metadata == "build42"

    def test_str(self) -> None:
        assert str(VersionInfo(1, 2, 3)) == "1.2.3"

    def test_str_with_pre_release(self) -> None:
        assert str(VersionInfo(2, 0, 0, pre_release="rc1")) == "2.0.0-rc1"

    def test_comparison_lt(self) -> None:
        assert VersionInfo(1, 0, 0) < VersionInfo(2, 0, 0)
        assert VersionInfo(1, 1, 0) < VersionInfo(1, 2, 0)
        assert VersionInfo(1, 0, 1) < VersionInfo(1, 0, 2)

    def test_satisfies_exact(self) -> None:
        assert VersionInfo(1, 0, 0).satisfies("==1.0.0")

    def test_satisfies_caret(self) -> None:
        assert VersionInfo(1, 5, 0).satisfies("^1.0.0")
        assert not VersionInfo(2, 0, 0).satisfies("^1.0.0")

    def test_satisfies_gte(self) -> None:
        assert VersionInfo(2, 0, 0).satisfies(">=1.0.0")
        assert not VersionInfo(0, 9, 0).satisfies(">=1.0.0")


# ---------------------------------------------------------------------------
# Enum tests
# ---------------------------------------------------------------------------


class TestEnums:
    def test_extension_status_values(self) -> None:
        assert ExtensionStatus.DISCOVERED is not None
        assert ExtensionStatus.INSTALLED is not None
        assert ExtensionStatus.VERIFIED is not None
        assert ExtensionStatus.ACTIVATED is not None
        assert ExtensionStatus.PAUSED is not None
        assert ExtensionStatus.DISABLED is not None
        assert ExtensionStatus.UPDATING is not None
        assert ExtensionStatus.FAILED is not None
        assert ExtensionStatus.REMOVED is not None

    def test_extension_type_values(self) -> None:
        assert ExtensionType.AI_PROVIDER is not None
        assert ExtensionType.KNOWLEDGE_CONNECTOR is not None
        assert ExtensionType.TOOL_PACK is not None
        assert ExtensionType.AUTOMATION_PACK is not None
        assert ExtensionType.UI_MODULE is not None
        assert ExtensionType.VOICE is not None
        assert ExtensionType.VISION is not None
        assert ExtensionType.ENTERPRISE_INTEGRATION is not None

    def test_capability_type_values(self) -> None:
        assert CapabilityType.TOOL is not None
        assert CapabilityType.AGENT is not None
        assert CapabilityType.AI_PROVIDER is not None
        assert CapabilityType.WORKFLOW_TEMPLATE is not None
        assert CapabilityType.KNOWLEDGE_CONNECTOR is not None
        assert CapabilityType.UI_COMPONENT is not None
        assert CapabilityType.INTEGRATION is not None
        assert CapabilityType.SERVICE is not None
        assert CapabilityType.COMMAND is not None
        assert CapabilityType.EVENT_HANDLER is not None

    def test_permission_scope_values(self) -> None:
        assert PermissionScope.MEMORY_ACCESS is not None
        assert PermissionScope.KNOWLEDGE_ACCESS is not None
        assert PermissionScope.TOOL_REGISTRATION is not None
        assert PermissionScope.WORKFLOW_REGISTRATION is not None
        assert PermissionScope.WORKSPACE_ACCESS is not None
        assert PermissionScope.EVENT_SUBSCRIPTION is not None
        assert PermissionScope.COMMAND_REGISTRATION is not None

    def test_compatibility_level_values(self) -> None:
        assert CompatibilityLevel.COMPATIBLE is not None
        assert CompatibilityLevel.INCOMPATIBLE is not None
        assert CompatibilityLevel.DEPRECATED is not None
        assert CompatibilityLevel.REQUIRES_UPDATE is not None

    def test_dependency_type_values(self) -> None:
        assert DependencyType.REQUIRED is not None
        assert DependencyType.OPTIONAL is not None


# ---------------------------------------------------------------------------
# Model tests
# ---------------------------------------------------------------------------


class TestExtensionManifest:
    def test_create(self) -> None:
        m = ExtensionManifest(
            extension_id="test.id",
            name="Test",
            version=VersionInfo(1, 0, 0),
        )
        assert m.extension_id == "test.id"
        assert m.name == "Test"

    def test_defaults(self) -> None:
        m = ExtensionManifest(
            extension_id="test.id",
            name="Test",
            version=VersionInfo(1, 0, 0),
        )
        assert m.publisher == ""
        assert m.capabilities == ()
        assert m.dependencies == ()
        assert m.permissions == ()
        assert m.extension_type == ExtensionType.TOOL_PACK
        assert m.tags == ()


class TestExtensionMetadata:
    def test_with_status(self) -> None:
        meta = ExtensionMetadata(
            extension_id="test.id",
            manifest=ExtensionManifest(
                extension_id="test.id",
                name="Test",
                version=VersionInfo(1, 0, 0),
            ),
        )
        updated = meta.with_status(ExtensionStatus.INSTALLED)
        assert updated.status == ExtensionStatus.INSTALLED
        assert updated.updated_at >= meta.updated_at

    def test_defaults(self) -> None:
        meta = ExtensionMetadata(
            extension_id="test.id",
            manifest=ExtensionManifest(
                extension_id="test.id",
                name="Test",
                version=VersionInfo(1, 0, 0),
            ),
        )
        assert meta.status == ExtensionStatus.DISCOVERED
        assert not meta.dependencies_resolved


class TestCompatibilityReport:
    def test_compatible(self) -> None:
        r = CompatibilityReport(level=CompatibilityLevel.COMPATIBLE)
        assert r.is_compatible
        assert r.issues == ()


class TestExtensionHealth:
    def test_defaults(self) -> None:
        h = ExtensionHealth(extension_id="test.id", status=ExtensionStatus.ACTIVATED)
        assert h.is_healthy
        assert h.activation_count == 0
        assert h.failure_count == 0


class TestIsolationPolicy:
    def test_defaults(self) -> None:
        p = IsolationPolicy()
        assert not p.sandbox_enabled
        assert isinstance(p.resource_limits, ResourceLimits)

    def test_resource_limits_defaults(self) -> None:
        r = ResourceLimits()
        assert r.max_memory_mb == 0
        assert r.max_concurrent_tasks == 1


# ---------------------------------------------------------------------------
# Registry tests
# ---------------------------------------------------------------------------


class TestInMemoryExtensionRegistry:
    def test_register_and_get(self, manifest: ExtensionManifest) -> None:
        r = InMemoryExtensionRegistry()
        meta = r.register(manifest)
        assert r.get("test.ext") is meta
        assert meta.status == ExtensionStatus.DISCOVERED

    def test_list(self, manifest: ExtensionManifest) -> None:
        r = InMemoryExtensionRegistry()
        r.register(manifest)
        assert len(r.list()) == 1

    def test_list_by_status(self, manifest: ExtensionManifest) -> None:
        r = InMemoryExtensionRegistry()
        r.register(manifest)
        assert len(r.list_by_status(ExtensionStatus.DISCOVERED)) == 1
        assert len(r.list_by_status(ExtensionStatus.INSTALLED)) == 0

    def test_list_by_type(self, manifest: ExtensionManifest) -> None:
        r = InMemoryExtensionRegistry()
        r.register(manifest)
        assert len(r.list_by_type(ExtensionType.TOOL_PACK)) == 1
        assert len(r.list_by_type(ExtensionType.AI_PROVIDER)) == 0

    def test_update(self, manifest: ExtensionManifest) -> None:
        r = InMemoryExtensionRegistry()
        meta = r.register(manifest)
        updated = meta.with_status(ExtensionStatus.INSTALLED)
        r.update(updated)
        assert r.get("test.ext").status == ExtensionStatus.INSTALLED

    def test_remove(self, manifest: ExtensionManifest) -> None:
        r = InMemoryExtensionRegistry()
        r.register(manifest)
        r.remove("test.ext")
        assert r.get("test.ext") is None

    def test_contains(self, manifest: ExtensionManifest) -> None:
        r = InMemoryExtensionRegistry()
        assert not r.contains("test.ext")
        r.register(manifest)
        assert r.contains("test.ext")


# ---------------------------------------------------------------------------
# Manifest validation tests
# ---------------------------------------------------------------------------


class TestInMemoryManifestValidator:
    def test_valid_manifest(self, manifest: ExtensionManifest) -> None:
        v = InMemoryManifestValidator()
        issues = v.validate(manifest)
        assert len(issues) == 0

    def test_empty_id(self) -> None:
        v = InMemoryManifestValidator()
        m = ExtensionManifest(
            extension_id="",
            name="Test",
            version=VersionInfo(1, 0, 0),
        )
        issues = v.validate(m)
        assert any(i.code == "EMPTY_ID" for i in issues)

    def test_empty_name(self) -> None:
        v = InMemoryManifestValidator()
        m = ExtensionManifest(
            extension_id="test.id",
            name="",
            version=VersionInfo(1, 0, 0),
        )
        issues = v.validate(m)
        assert any(i.code == "EMPTY_NAME" for i in issues)

    def test_invalid_version(self) -> None:
        v = InMemoryManifestValidator()
        m = ExtensionManifest(
            extension_id="test.id",
            name="Test",
            version=VersionInfo(0, 0, 0),
        )
        issues = v.validate(m)
        assert any(i.code == "INVALID_VERSION" for i in issues)

    def test_duplicate_capability(self) -> None:
        v = InMemoryManifestValidator()
        cap = CapabilityDefinition(
            capability_type=CapabilityType.TOOL,
            identifier="dup.id",
            name="Dup",
        )
        m = ExtensionManifest(
            extension_id="test.id",
            name="Test",
            version=VersionInfo(1, 0, 0),
            capabilities=(cap, cap),
        )
        issues = v.validate(m)
        assert any(i.code == "DUPLICATE_CAPABILITY" for i in issues)

    def test_platform_compatibility(self) -> None:
        v = InMemoryManifestValidator()
        m = ExtensionManifest(
            extension_id="test.id",
            name="Test",
            version=VersionInfo(1, 0, 0),
            min_platform_version=VersionInfo(3, 0, 0),
        )
        report = v.validate_platform_compatibility(m, VersionInfo(2, 0, 0))
        assert not report.is_compatible
        assert report.level == CompatibilityLevel.INCOMPATIBLE

    def test_platform_max_version(self) -> None:
        v = InMemoryManifestValidator()
        m = ExtensionManifest(
            extension_id="test.id",
            name="Test",
            version=VersionInfo(1, 0, 0),
            max_platform_version=VersionInfo(1, 0, 0),
        )
        report = v.validate_platform_compatibility(m, VersionInfo(2, 0, 0))
        assert not report.is_compatible

    def test_platform_compatible(self) -> None:
        v = InMemoryManifestValidator()
        m = ExtensionManifest(
            extension_id="test.id",
            name="Test",
            version=VersionInfo(1, 0, 0),
            min_platform_version=VersionInfo(1, 0, 0),
        )
        report = v.validate_platform_compatibility(m, VersionInfo(1, 5, 0))
        assert report.is_compatible


# ---------------------------------------------------------------------------
# Dependency manager tests
# ---------------------------------------------------------------------------


class TestInMemoryDependencyManager:
    def test_resolve_success(self, registry: InMemoryExtensionRegistry) -> None:
        dep_manifest = ExtensionManifest(
            extension_id="dep.ext",
            name="Dependency",
            version=VersionInfo(2, 0, 0),
        )
        registry.register(dep_manifest)
        dm = InMemoryDependencyManager()
        deps = (
            DependencyDefinition(
                extension_id="dep.ext",
                version_constraint=">=1.0.0",
            ),
        )
        issues = dm.resolve("test.ext", deps, registry)
        assert len(issues) == 0

    def test_resolve_missing_required(self, registry: InMemoryExtensionRegistry) -> None:
        dm = InMemoryDependencyManager()
        deps = (
            DependencyDefinition(
                extension_id="missing.ext",
                version_constraint=">=1.0.0",
            ),
        )
        issues = dm.resolve("test.ext", deps, registry)
        assert any(i.code == "MISSING_DEPENDENCY" for i in issues)

    def test_resolve_version_mismatch(self, registry: InMemoryExtensionRegistry) -> None:
        dep_manifest = ExtensionManifest(
            extension_id="dep.ext",
            name="Dependency",
            version=VersionInfo(1, 0, 0),
        )
        registry.register(dep_manifest)
        dm = InMemoryDependencyManager()
        deps = (
            DependencyDefinition(
                extension_id="dep.ext",
                version_constraint=">=2.0.0",
            ),
        )
        issues = dm.resolve("test.ext", deps, registry)
        assert any(i.code == "VERSION_MISMATCH" for i in issues)

    def test_validate_circular(self, registry: InMemoryExtensionRegistry) -> None:
        a_manifest = ExtensionManifest(
            extension_id="a.ext",
            name="A",
            version=VersionInfo(1, 0, 0),
            dependencies=(DependencyDefinition(extension_id="b.ext"),),
        )
        b_manifest = ExtensionManifest(
            extension_id="b.ext",
            name="B",
            version=VersionInfo(1, 0, 0),
            dependencies=(DependencyDefinition(extension_id="a.ext"),),
        )
        registry.register(a_manifest)
        registry.register(b_manifest)
        dm = InMemoryDependencyManager()
        issues = dm.validate_circular("a.ext", a_manifest.dependencies, registry)
        assert any(i.code == "CIRCULAR_DEPENDENCY" for i in issues)

    def test_optional_dependency_missing(self, registry: InMemoryExtensionRegistry) -> None:
        dm = InMemoryDependencyManager()
        deps = (
            DependencyDefinition(
                extension_id="missing.ext",
                dependency_type=DependencyType.OPTIONAL,
            ),
        )
        issues = dm.resolve("test.ext", deps, registry)
        assert len(issues) == 0


# ---------------------------------------------------------------------------
# Compatibility engine tests
# ---------------------------------------------------------------------------


class TestInMemoryCompatibilityEngine:
    def test_check_compatible(self) -> None:
        ce = InMemoryCompatibilityEngine()
        m = ExtensionManifest(
            extension_id="test.ext",
            name="Test",
            version=VersionInfo(1, 0, 0),
            min_platform_version=VersionInfo(1, 0, 0),
        )
        report = ce.check_extension_compatibility(m, VersionInfo(1, 5, 0))
        assert report.is_compatible

    def test_check_incompatible_platform_low(self) -> None:
        ce = InMemoryCompatibilityEngine()
        m = ExtensionManifest(
            extension_id="test.ext",
            name="Test",
            version=VersionInfo(1, 0, 0),
            min_platform_version=VersionInfo(2, 0, 0),
        )
        report = ce.check_extension_compatibility(m, VersionInfo(1, 0, 0))
        assert not report.is_compatible

    def test_check_incompatible_platform_high(self) -> None:
        ce = InMemoryCompatibilityEngine()
        m = ExtensionManifest(
            extension_id="test.ext",
            name="Test",
            version=VersionInfo(1, 0, 0),
            max_platform_version=VersionInfo(1, 0, 0),
        )
        report = ce.check_extension_compatibility(m, VersionInfo(2, 0, 0))
        assert not report.is_compatible

    def test_version_compatibility(self) -> None:
        ce = InMemoryCompatibilityEngine()
        assert (
            ce.check_version_compatibility(
                VersionInfo(1, 5, 0),
                ">=1.0.0",
            )
            == CompatibilityLevel.COMPATIBLE
        )
        assert (
            ce.check_version_compatibility(
                VersionInfo(0, 9, 0),
                ">=1.0.0",
            )
            == CompatibilityLevel.INCOMPATIBLE
        )

    def test_contract_compatibility(self) -> None:
        ce = InMemoryCompatibilityEngine()
        provided = CapabilityDefinition(
            capability_type=CapabilityType.TOOL,
            identifier="test.cap",
            name="Test",
            version=VersionInfo(2, 0, 0),
        )
        expected = CapabilityDefinition(
            capability_type=CapabilityType.TOOL,
            identifier="test.cap",
            name="Test",
            version=VersionInfo(1, 0, 0),
        )
        assert (
            ce.check_contract_compatibility(
                provided,
                expected,
            )
            == CompatibilityLevel.COMPATIBLE
        )

    def test_contract_incompatible_type(self) -> None:
        ce = InMemoryCompatibilityEngine()
        provided = CapabilityDefinition(
            capability_type=CapabilityType.TOOL,
            identifier="test.cap",
            name="Test",
        )
        expected = CapabilityDefinition(
            capability_type=CapabilityType.AGENT,
            identifier="test.cap",
            name="Test",
        )
        assert (
            ce.check_contract_compatibility(
                provided,
                expected,
            )
            == CompatibilityLevel.INCOMPATIBLE
        )


# ---------------------------------------------------------------------------
# Capability registry tests
# ---------------------------------------------------------------------------


class TestInMemoryCapabilityRegistry:
    def test_register_and_get(self) -> None:
        cr = InMemoryCapabilityRegistry()
        cap = CapabilityDefinition(
            capability_type=CapabilityType.TOOL,
            identifier="test.cap",
            name="Test",
        )
        cr.register_capability("ext1", cap)
        assert cr.get_capability("test.cap") is cap

    def test_unregister(self) -> None:
        cr = InMemoryCapabilityRegistry()
        cap = CapabilityDefinition(
            capability_type=CapabilityType.TOOL,
            identifier="test.cap",
            name="Test",
        )
        cr.register_capability("ext1", cap)
        cr.unregister_capability("ext1", "test.cap")
        assert cr.get_capability("test.cap") is None

    def test_list_capabilities_filter(self) -> None:
        cr = InMemoryCapabilityRegistry()
        cr.register_capability(
            "ext1",
            CapabilityDefinition(CapabilityType.TOOL, "t1", "Tool 1"),
        )
        cr.register_capability(
            "ext1",
            CapabilityDefinition(CapabilityType.AGENT, "a1", "Agent 1"),
        )
        tools = cr.list_capabilities(CapabilityType.TOOL)
        assert len(tools) == 1
        assert tools[0][1].identifier == "t1"

    def test_list_extension_capabilities(self) -> None:
        cr = InMemoryCapabilityRegistry()
        cr.register_capability(
            "ext1",
            CapabilityDefinition(CapabilityType.TOOL, "t1", "Tool 1"),
        )
        cr.register_capability(
            "ext2",
            CapabilityDefinition(CapabilityType.TOOL, "t2", "Tool 2"),
        )
        caps = cr.list_extension_capabilities("ext1")
        assert len(caps) == 1
        assert caps[0].identifier == "t1"

    def test_clear_extension(self) -> None:
        cr = InMemoryCapabilityRegistry()
        cr.register_capability(
            "ext1",
            CapabilityDefinition(CapabilityType.TOOL, "t1", "Tool 1"),
        )
        cr.clear_extension("ext1")
        assert cr.list_capabilities() == ()


# ---------------------------------------------------------------------------
# Lifecycle manager tests
# ---------------------------------------------------------------------------


class TestInMemoryLifecycleManager:
    def test_valid_transition(self) -> None:
        lm = InMemoryLifecycleManager()
        meta = ExtensionMetadata(
            extension_id="test.id",
            manifest=ExtensionManifest(
                extension_id="test.id",
                name="Test",
                version=VersionInfo(1, 0, 0),
            ),
        )
        result = lm.transition(meta, ExtensionStatus.INSTALLED)
        assert result.status == ExtensionStatus.INSTALLED

    def test_invalid_transition_raises(self) -> None:
        lm = InMemoryLifecycleManager()
        meta = ExtensionMetadata(
            extension_id="test.id",
            manifest=ExtensionManifest(
                extension_id="test.id",
                name="Test",
                version=VersionInfo(1, 0, 0),
            ),
        )
        with pytest.raises(ValueError, match="Cannot transition"):
            lm.transition(meta, ExtensionStatus.ACTIVATED)

    def test_can_transition(self) -> None:
        lm = InMemoryLifecycleManager()
        assert lm.can_transition(ExtensionStatus.DISCOVERED, ExtensionStatus.INSTALLED)
        assert not lm.can_transition(ExtensionStatus.DISCOVERED, ExtensionStatus.ACTIVATED)
        assert not lm.can_transition(ExtensionStatus.REMOVED, ExtensionStatus.INSTALLED)

    def test_valid_transitions(self) -> None:
        lm = InMemoryLifecycleManager()
        transitions = lm.valid_transitions(ExtensionStatus.DISCOVERED)
        assert ExtensionStatus.INSTALLED in transitions
        assert ExtensionStatus.REMOVED in transitions


# ---------------------------------------------------------------------------
# Permission manager tests
# ---------------------------------------------------------------------------


class TestInMemoryPermissionManager:
    def test_grant_and_check(self) -> None:
        pm = InMemoryPermissionManager()
        perm = PermissionRequest(permission_scope=PermissionScope.TOOL_REGISTRATION)
        pm.grant("ext1", perm)
        assert pm.check("ext1", PermissionScope.TOOL_REGISTRATION)
        assert not pm.check("ext1", PermissionScope.MEMORY_ACCESS)

    def test_revoke(self) -> None:
        pm = InMemoryPermissionManager()
        pm.grant(
            "ext1",
            PermissionRequest(
                permission_scope=PermissionScope.TOOL_REGISTRATION,
            ),
        )
        pm.revoke("ext1", PermissionScope.TOOL_REGISTRATION)
        assert not pm.check("ext1", PermissionScope.TOOL_REGISTRATION)

    def test_list_permissions(self) -> None:
        pm = InMemoryPermissionManager()
        perm = PermissionRequest(permission_scope=PermissionScope.MEMORY_ACCESS)
        pm.grant("ext1", perm)
        assert len(pm.list_permissions("ext1")) == 1

    def test_revoke_all(self) -> None:
        pm = InMemoryPermissionManager()
        pm.grant(
            "ext1",
            PermissionRequest(
                permission_scope=PermissionScope.TOOL_REGISTRATION,
            ),
        )
        pm.grant(
            "ext1",
            PermissionRequest(
                permission_scope=PermissionScope.MEMORY_ACCESS,
            ),
        )
        pm.revoke_all("ext1")
        assert pm.list_permissions("ext1") == ()


# ---------------------------------------------------------------------------
# Isolation manager tests
# ---------------------------------------------------------------------------


class TestInMemoryIsolationManager:
    def test_set_and_get_policy(self) -> None:
        im = InMemoryIsolationManager()
        policy = IsolationPolicy(sandbox_enabled=True)
        im.set_policy("ext1", policy)
        assert im.get_policy("ext1") is policy

    def test_capability_allowed_by_default(self) -> None:
        im = InMemoryIsolationManager()
        assert im.check_capability_allowed("ext1", CapabilityType.TOOL)

    def test_capability_denied(self) -> None:
        im = InMemoryIsolationManager()
        policy = IsolationPolicy(
            denied_capabilities=(CapabilityType.TOOL,),
        )
        im.set_policy("ext1", policy)
        assert not im.check_capability_allowed("ext1", CapabilityType.TOOL)
        assert im.check_capability_allowed("ext1", CapabilityType.AGENT)

    def test_capability_allowed_list(self) -> None:
        im = InMemoryIsolationManager()
        policy = IsolationPolicy(
            allowed_capabilities=(CapabilityType.AGENT,),
        )
        im.set_policy("ext1", policy)
        assert im.check_capability_allowed("ext1", CapabilityType.AGENT)
        assert not im.check_capability_allowed("ext1", CapabilityType.TOOL)

    def test_remove_policy(self) -> None:
        im = InMemoryIsolationManager()
        im.set_policy("ext1", IsolationPolicy(sandbox_enabled=True))
        im.remove_policy("ext1")
        assert im.get_policy("ext1") is None


# ---------------------------------------------------------------------------
# Version manager tests
# ---------------------------------------------------------------------------


class TestInMemoryVersionManager:
    def test_compare(self) -> None:
        vm = InMemoryVersionManager()
        assert vm.compare(VersionInfo(1, 0, 0), VersionInfo(2, 0, 0)) == -1
        assert vm.compare(VersionInfo(2, 0, 0), VersionInfo(1, 0, 0)) == 1
        assert vm.compare(VersionInfo(1, 0, 0), VersionInfo(1, 0, 0)) == 0

    def test_is_compatible(self) -> None:
        vm = InMemoryVersionManager()
        assert vm.is_compatible(VersionInfo(1, 5, 0), ">=1.0.0")
        assert not vm.is_compatible(VersionInfo(0, 9, 0), ">=1.0.0")

    def test_suggest_upgrade(self) -> None:
        vm = InMemoryVersionManager()
        current = VersionInfo(1, 0, 0)
        available = (VersionInfo(1, 1, 0), VersionInfo(2, 0, 0), VersionInfo(0, 9, 0))
        suggestion = vm.suggest_upgrade(current, available)
        assert suggestion == VersionInfo(2, 0, 0)

    def test_suggest_upgrade_none(self) -> None:
        vm = InMemoryVersionManager()
        current = VersionInfo(2, 0, 0)
        available = (VersionInfo(1, 0, 0),)
        assert vm.suggest_upgrade(current, available) is None


# ---------------------------------------------------------------------------
# Health monitor tests
# ---------------------------------------------------------------------------


class TestInMemoryHealthMonitor:
    def test_record_activation(self) -> None:
        hm = InMemoryHealthMonitor()
        health = hm.record_activation("ext1")
        assert health.activation_count == 1
        assert health.is_healthy

    def test_record_failure(self) -> None:
        hm = InMemoryHealthMonitor()
        health = hm.record_failure("ext1", "Something went wrong")
        assert health.failure_count == 1
        assert not health.is_healthy
        assert health.last_failure_message == "Something went wrong"

    def test_get_health(self) -> None:
        hm = InMemoryHealthMonitor()
        hm.record_activation("ext1")
        assert hm.get_health("ext1") is not None
        assert hm.get_health("nonexistent") is None

    def test_list_unhealthy(self) -> None:
        hm = InMemoryHealthMonitor()
        hm.record_failure("ext1", "Error")
        hm.record_activation("ext2")
        unhealthy = hm.list_unhealthy()
        assert len(unhealthy) == 1
        assert unhealthy[0].extension_id == "ext1"

    def test_reset_health(self) -> None:
        hm = InMemoryHealthMonitor()
        hm.record_activation("ext1")
        hm.reset_health("ext1")
        assert hm.get_health("ext1") is None


# ---------------------------------------------------------------------------
# Event integration tests
# ---------------------------------------------------------------------------


class TestInMemoryEventIntegration:
    def test_subscribe_and_list(self) -> None:
        ei = InMemoryEventIntegration()
        ei.subscribe("ext1", "workflow.completed", "handler1")
        subs = ei.list_subscriptions("ext1")
        assert len(subs) == 1
        assert subs[0] == ("workflow.completed", "handler1")

    def test_unsubscribe(self) -> None:
        ei = InMemoryEventIntegration()
        ei.subscribe("ext1", "workflow.completed", "handler1")
        ei.unsubscribe("ext1", "workflow.completed")
        assert ei.list_subscriptions("ext1") == ()

    def test_unsubscribe_all(self) -> None:
        ei = InMemoryEventIntegration()
        ei.subscribe("ext1", "event.a", "h1")
        ei.subscribe("ext1", "event.b", "h2")
        ei.unsubscribe_all("ext1")
        assert ei.list_subscriptions("ext1") == ()


# ---------------------------------------------------------------------------
# Kernel tests
# ---------------------------------------------------------------------------


class TestExtensionKernel:
    def test_discover(self, kernel: ExtensionKernel, manifest: ExtensionManifest) -> None:
        meta = kernel.discover(manifest)
        assert meta.status == ExtensionStatus.DISCOVERED
        assert kernel.get_metadata("test.ext") is not None

    def test_discover_invalid_manifest(self, kernel: ExtensionKernel) -> None:
        bad = ExtensionManifest(
            extension_id="",
            name="",
            version=VersionInfo(0, 0, 0),
        )
        meta = kernel.discover(bad)
        assert meta.status == ExtensionStatus.FAILED

    def test_discover_to_install(
        self,
        kernel: ExtensionKernel,
        manifest: ExtensionManifest,
    ) -> None:
        kernel.discover(manifest)
        meta = kernel.install("test.ext")
        assert meta.status == ExtensionStatus.INSTALLED
        assert meta.installed_version == VersionInfo(1, 0, 0)

    def test_install_missing_dependency(self, kernel: ExtensionKernel) -> None:
        ext = ExtensionManifest(
            extension_id="test.ext",
            name="Test",
            version=VersionInfo(1, 0, 0),
            dependencies=(
                DependencyDefinition(
                    extension_id="missing.ext",
                    version_constraint=">=1.0.0",
                ),
            ),
        )
        kernel.discover(ext)
        meta = kernel.install("test.ext")
        assert meta.status == ExtensionStatus.INSTALLED
        assert not meta.dependencies_resolved

    def test_activate(self, kernel: ExtensionKernel, manifest: ExtensionManifest) -> None:
        kernel.discover(manifest)
        kernel.install("test.ext")
        meta = kernel.activate("test.ext")
        assert meta.status == ExtensionStatus.ACTIVATED
        cap = kernel.capability_registry.get_capability("test.cap.tool1")
        assert cap is not None
        assert kernel.permissions.check(
            "test.ext",
            PermissionScope.TOOL_REGISTRATION,
        )

    def test_activate_to_deactivate(
        self,
        kernel: ExtensionKernel,
        manifest: ExtensionManifest,
    ) -> None:
        kernel.discover(manifest)
        kernel.install("test.ext")
        kernel.activate("test.ext")
        meta = kernel.deactivate("test.ext")
        assert meta.status == ExtensionStatus.PAUSED
        assert kernel.capability_registry.get_capability("test.cap.tool1") is None

    def test_disable(self, kernel: ExtensionKernel, manifest: ExtensionManifest) -> None:
        kernel.discover(manifest)
        kernel.install("test.ext")
        kernel.activate("test.ext")
        meta = kernel.disable("test.ext")
        assert meta.status == ExtensionStatus.DISABLED
        assert not kernel.permissions.check(
            "test.ext",
            PermissionScope.TOOL_REGISTRATION,
        )

    def test_enable(self, kernel: ExtensionKernel, manifest: ExtensionManifest) -> None:
        kernel.discover(manifest)
        kernel.install("test.ext")
        kernel.activate("test.ext")
        kernel.disable("test.ext")
        meta = kernel.enable("test.ext")
        assert meta.status == ExtensionStatus.ACTIVATED

    def test_remove(self, kernel: ExtensionKernel, manifest: ExtensionManifest) -> None:
        kernel.discover(manifest)
        kernel.remove("test.ext")
        assert kernel.get_metadata("test.ext") is None

    def test_update(self, kernel: ExtensionKernel, manifest: ExtensionManifest) -> None:
        kernel.discover(manifest)
        kernel.install("test.ext")
        new_manifest = ExtensionManifest(
            extension_id="test.ext",
            name="Test Updated",
            version=VersionInfo(1, 1, 0),
        )
        meta = kernel.update("test.ext", new_manifest)
        assert meta.manifest.version == VersionInfo(1, 1, 0)
        assert meta.manifest.name == "Test Updated"

    def test_list_extensions(self, kernel: ExtensionKernel, manifest: ExtensionManifest) -> None:
        kernel.discover(manifest)
        assert len(kernel.list_extensions()) == 1
        assert len(kernel.list_extensions(ExtensionStatus.DISCOVERED)) == 1
        assert len(kernel.list_extensions(ExtensionStatus.INSTALLED)) == 0

    def test_get_health(self, kernel: ExtensionKernel, manifest: ExtensionManifest) -> None:
        kernel.discover(manifest)
        health = kernel.get_health("test.ext")
        assert health is not None
        assert health.is_healthy

    def test_get_metadata_nonexistent(self, kernel: ExtensionKernel) -> None:
        assert kernel.get_metadata("nonexistent") is None

    def test_install_nonexistent_raises(self, kernel: ExtensionKernel) -> None:
        with pytest.raises(ValueError, match="Extension not found"):
            kernel.install("nonexistent")

    def test_activate_invalid_transition(
        self,
        kernel: ExtensionKernel,
        manifest: ExtensionManifest,
    ) -> None:
        kernel.discover(manifest)
        with pytest.raises(ValueError, match="Cannot transition"):
            kernel.activate("test.ext")

    def test_full_lifecycle(self, kernel: ExtensionKernel, manifest: ExtensionManifest) -> None:
        kernel.discover(manifest)
        kernel.install("test.ext")
        kernel.activate("test.ext")
        kernel.deactivate("test.ext")
        kernel.activate("test.ext")
        kernel.disable("test.ext")
        health = kernel.get_health("test.ext")
        assert health is not None
        assert health.activation_count >= 2


# ---------------------------------------------------------------------------
# Built-in extension definition tests
# ---------------------------------------------------------------------------


class TestBuiltInExtensions:
    def test_builtin_count(self) -> None:
        assert len(BUILT_IN_EXTENSIONS) == 8

    def test_ai_providers(self) -> None:
        ext = [e for e in BUILT_IN_EXTENSIONS if e.extension_id == "jarvis.builtin.ai_providers"]
        assert len(ext) == 1
        assert ext[0].extension_type == ExtensionType.AI_PROVIDER

    def test_knowledge_connectors(self) -> None:
        ext = [
            e
            for e in BUILT_IN_EXTENSIONS
            if e.extension_id == "jarvis.builtin.knowledge_connectors"
        ]
        assert len(ext) == 1
        assert ext[0].extension_type == ExtensionType.KNOWLEDGE_CONNECTOR

    def test_tool_pack(self) -> None:
        ext = [e for e in BUILT_IN_EXTENSIONS if e.extension_id == "jarvis.builtin.tool_pack"]
        assert len(ext) == 1
        caps = ext[0].capabilities
        assert any(c.capability_type == CapabilityType.TOOL for c in caps)

    def test_automation_pack(self) -> None:
        ext = [e for e in BUILT_IN_EXTENSIONS if e.extension_id == "jarvis.builtin.automation_pack"]
        assert len(ext) == 1
        assert len(ext[0].dependencies) == 1

    def test_ui_module(self) -> None:
        ext = [e for e in BUILT_IN_EXTENSIONS if e.extension_id == "jarvis.builtin.ui_module"]
        assert len(ext) == 1
        assert ext[0].extension_type == ExtensionType.UI_MODULE

    def test_voice(self) -> None:
        ext = [e for e in BUILT_IN_EXTENSIONS if e.extension_id == "jarvis.builtin.voice"]
        assert len(ext) == 1
        assert ext[0].extension_type == ExtensionType.VOICE

    def test_vision(self) -> None:
        ext = [e for e in BUILT_IN_EXTENSIONS if e.extension_id == "jarvis.builtin.vision"]
        assert len(ext) == 1
        assert ext[0].extension_type == ExtensionType.VISION

    def test_enterprise(self) -> None:
        ext = [e for e in BUILT_IN_EXTENSIONS if e.extension_id == "jarvis.builtin.enterprise"]
        assert len(ext) == 1
        assert ext[0].extension_type == ExtensionType.ENTERPRISE_INTEGRATION

    def test_all_are_built_in(self) -> None:
        for ext in BUILT_IN_EXTENSIONS:
            assert ext.is_built_in

    def test_all_have_publisher(self) -> None:
        for ext in BUILT_IN_EXTENSIONS:
            assert ext.publisher == "JARVIS Core"


# ---------------------------------------------------------------------------
# Edge case tests
# ---------------------------------------------------------------------------


class TestEdgeCases:
    def test_empty_registry(self) -> None:
        r = InMemoryExtensionRegistry()
        assert r.list() == ()
        assert r.get("nonexistent") is None
        r.remove("nonexistent")

    def test_duplicate_registration(self, manifest: ExtensionManifest) -> None:
        r = InMemoryExtensionRegistry()
        m1 = r.register(manifest)
        m2 = r.register(manifest)
        assert m1 is m2
        assert len(r.list()) == 1

    def test_isolation_default_policy(self) -> None:
        im = InMemoryIsolationManager()
        assert im.get_policy("unknown") is None

    def test_health_nonexistent(self) -> None:
        hm = InMemoryHealthMonitor()
        assert hm.get_health("nonexistent") is None

    def test_permissions_nonexistent(self) -> None:
        pm = InMemoryPermissionManager()
        assert not pm.check("nonexistent", PermissionScope.MEMORY_ACCESS)
        assert pm.list_permissions("nonexistent") == ()

    def test_event_integration_nonexistent(self) -> None:
        ei = InMemoryEventIntegration()
        assert ei.list_subscriptions("nonexistent") == ()

    def test_version_compare_equal(self) -> None:
        vm = InMemoryVersionManager()
        assert vm.compare(VersionInfo(1, 2, 3), VersionInfo(1, 2, 3)) == 0

    def test_compatibility_report_default(self) -> None:
        r = CompatibilityReport(level=CompatibilityLevel.COMPATIBLE)
        assert r.is_compatible
        assert r.level == CompatibilityLevel.COMPATIBLE
