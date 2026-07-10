from __future__ import annotations

from jarvis_extensions.models import (
    BuiltInExtensionDefinition,
    CapabilityDefinition,
    CapabilityType,
    DependencyDefinition,
    DependencyType,
    ExtensionType,
    PermissionRequest,
    PermissionScope,
    VersionInfo,
)

BUILT_IN_EXTENSIONS: tuple[BuiltInExtensionDefinition, ...] = (
    BuiltInExtensionDefinition(
        extension_id="jarvis.builtin.ai_providers",
        name="AI Provider Extension",
        description="Registers AI provider connectors for model access",
        extension_type=ExtensionType.AI_PROVIDER,
        version=VersionInfo(1, 0, 0),
        capabilities=(
            CapabilityDefinition(
                capability_type=CapabilityType.AI_PROVIDER,
                identifier="jarvis.capability.ai.openai",
                name="OpenAI Provider",
                description="OpenAI model provider integration",
            ),
            CapabilityDefinition(
                capability_type=CapabilityType.AI_PROVIDER,
                identifier="jarvis.capability.ai.anthropic",
                name="Anthropic Provider",
                description="Anthropic model provider integration",
            ),
        ),
        permissions=(
            PermissionRequest(
                permission_scope=PermissionScope.COMMAND_REGISTRATION,
                reason="Register AI provider commands",
                required=True,
            ),
        ),
    ),
    BuiltInExtensionDefinition(
        extension_id="jarvis.builtin.knowledge_connectors",
        name="Knowledge Connector Extension",
        description="Connects to external knowledge sources",
        extension_type=ExtensionType.KNOWLEDGE_CONNECTOR,
        version=VersionInfo(1, 0, 0),
        capabilities=(
            CapabilityDefinition(
                capability_type=CapabilityType.KNOWLEDGE_CONNECTOR,
                identifier="jarvis.capability.knowledge.web",
                name="Web Connector",
                description="Web-based knowledge source connector",
            ),
            CapabilityDefinition(
                capability_type=CapabilityType.KNOWLEDGE_CONNECTOR,
                identifier="jarvis.capability.knowledge.file",
                name="File Connector",
                description="File-based knowledge source connector",
            ),
        ),
        permissions=(
            PermissionRequest(
                permission_scope=PermissionScope.KNOWLEDGE_ACCESS,
                reason="Access knowledge sources",
                required=True,
            ),
        ),
    ),
    BuiltInExtensionDefinition(
        extension_id="jarvis.builtin.tool_pack",
        name="Tool Pack Extension",
        description="Registers collections of tools for the Tool Platform",
        extension_type=ExtensionType.TOOL_PACK,
        version=VersionInfo(1, 0, 0),
        capabilities=(
            CapabilityDefinition(
                capability_type=CapabilityType.TOOL,
                identifier="jarvis.capability.tool.core",
                name="Core Tools",
                description="Core system tool collection",
            ),
        ),
        permissions=(
            PermissionRequest(
                permission_scope=PermissionScope.TOOL_REGISTRATION,
                reason="Register tools with the Tool Platform",
                required=True,
            ),
            PermissionRequest(
                permission_scope=PermissionScope.WORKSPACE_ACCESS,
                reason="Access workspace for tool execution",
                required=False,
            ),
        ),
    ),
    BuiltInExtensionDefinition(
        extension_id="jarvis.builtin.automation_pack",
        name="Automation Pack Extension",
        description="Provides workflow templates and automation patterns",
        extension_type=ExtensionType.AUTOMATION_PACK,
        version=VersionInfo(1, 0, 0),
        capabilities=(
            CapabilityDefinition(
                capability_type=CapabilityType.WORKFLOW_TEMPLATE,
                identifier="jarvis.capability.automation.templates",
                name="Workflow Templates",
                description="Pre-built workflow automation templates",
            ),
        ),
        permissions=(
            PermissionRequest(
                permission_scope=PermissionScope.WORKFLOW_REGISTRATION,
                reason="Register workflow templates",
                required=True,
            ),
        ),
        dependencies=(
            DependencyDefinition(
                extension_id="jarvis.builtin.tool_pack",
                version_constraint=">=1.0.0",
                dependency_type=DependencyType.REQUIRED,
            ),
        ),
    ),
    BuiltInExtensionDefinition(
        extension_id="jarvis.builtin.ui_module",
        name="UI Module Extension",
        description="Provides user interface components and contributions",
        extension_type=ExtensionType.UI_MODULE,
        version=VersionInfo(1, 0, 0),
        capabilities=(
            CapabilityDefinition(
                capability_type=CapabilityType.UI_COMPONENT,
                identifier="jarvis.capability.ui.components",
                name="UI Components",
                description="Reusable UI component library",
            ),
        ),
    ),
    BuiltInExtensionDefinition(
        extension_id="jarvis.builtin.voice",
        name="Voice Extension",
        description="Adds voice input and output capabilities",
        extension_type=ExtensionType.VOICE,
        version=VersionInfo(1, 0, 0),
        capabilities=(
            CapabilityDefinition(
                capability_type=CapabilityType.SERVICE,
                identifier="jarvis.capability.voice.speech",
                name="Speech Service",
                description="Speech-to-text and text-to-speech",
            ),
        ),
    ),
    BuiltInExtensionDefinition(
        extension_id="jarvis.builtin.vision",
        name="Vision Extension",
        description="Adds image and video processing capabilities",
        extension_type=ExtensionType.VISION,
        version=VersionInfo(1, 0, 0),
        capabilities=(
            CapabilityDefinition(
                capability_type=CapabilityType.SERVICE,
                identifier="jarvis.capability.vision.analysis",
                name="Vision Analysis",
                description="Image and video analysis service",
            ),
        ),
    ),
    BuiltInExtensionDefinition(
        extension_id="jarvis.builtin.enterprise",
        name="Enterprise Integration Extension",
        description="Provides enterprise system integration connectors",
        extension_type=ExtensionType.ENTERPRISE_INTEGRATION,
        version=VersionInfo(1, 0, 0),
        capabilities=(
            CapabilityDefinition(
                capability_type=CapabilityType.INTEGRATION,
                identifier="jarvis.capability.integration.ldap",
                name="LDAP Integration",
                description="LDAP directory service integration",
            ),
            CapabilityDefinition(
                capability_type=CapabilityType.INTEGRATION,
                identifier="jarvis.capability.integration.saml",
                name="SAML Integration",
                description="SAML-based authentication integration",
            ),
        ),
        permissions=(
            PermissionRequest(
                permission_scope=PermissionScope.COMMAND_REGISTRATION,
                reason="Register enterprise integration commands",
                required=True,
            ),
        ),
    ),
)
