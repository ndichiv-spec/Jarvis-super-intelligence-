from __future__ import annotations

from jarvis_agents.models import (
    AgentCapability,
    AgentDefinition,
    AgentPermission,
    AgentPermissionResource,
    PermissionAccess,
)

_CAP_RESEARCH = AgentCapability(
    name="research",
    description="Conduct research and gather information",
)
_CAP_PROGRAMMING = AgentCapability(
    name="programming",
    description="Write and review code",
)
_CAP_ARCHITECTURE = AgentCapability(
    name="architecture",
    description="Design software architecture",
)
_CAP_AUTOMATION = AgentCapability(
    name="automation",
    description="Automate workflows and processes",
)
_CAP_PLANNING = AgentCapability(
    name="planning",
    description="Create and manage plans",
)
_CAP_SUMMARIZATION = AgentCapability(
    name="summarization",
    description="Summarize information",
)
_CAP_ANALYSIS = AgentCapability(
    name="analysis",
    description="Analyze data and patterns",
)
_CAP_DESIGN = AgentCapability(
    name="design",
    description="Design systems and interfaces",
)
_CAP_TRANSLATION = AgentCapability(
    name="translation",
    description="Translate between languages",
)
_CAP_VISION = AgentCapability(
    name="vision",
    description="Process visual information",
)
_CAP_VOICE = AgentCapability(
    name="voice",
    description="Process voice and audio",
)
_CAP_REASONING = AgentCapability(
    name="reasoning",
    description="Perform logical reasoning",
)
_CAP_DOCUMENTATION = AgentCapability(
    name="documentation",
    description="Create and maintain documentation",
)
_CAP_TESTING = AgentCapability(
    name="testing",
    description="Write and execute tests",
)
_CAP_CODE_REVIEW = AgentCapability(
    name="code_review",
    description="Review code for quality",
)
_CAP_DEBUGGING = AgentCapability(
    name="debugging",
    description="Debug issues in code",
)
_CAP_OPTIMIZATION = AgentCapability(
    name="optimization",
    description="Optimize performance",
)
_CAP_MONITORING = AgentCapability(
    name="monitoring",
    description="Monitor systems and health",
)
_CAP_COMMUNICATION = AgentCapability(
    name="communication",
    description="Handle communications",
)
_CAP_REPORTING = AgentCapability(
    name="reporting",
    description="Generate reports",
)

_READ_MEM = AgentPermission(
    resource=AgentPermissionResource.MEMORY,
    access=PermissionAccess.READ,
)
_READ_KNOWLEDGE = AgentPermission(
    resource=AgentPermissionResource.KNOWLEDGE,
    access=PermissionAccess.READ,
)
_READ_WRITE_MEM = AgentPermission(
    resource=AgentPermissionResource.MEMORY,
    access=PermissionAccess.WRITE,
)
_READ_WRITE_KNOWLEDGE = AgentPermission(
    resource=AgentPermissionResource.KNOWLEDGE,
    access=PermissionAccess.WRITE,
)
_TOOL_ACCESS = AgentPermission(
    resource=AgentPermissionResource.TOOL,
    access=PermissionAccess.READ,
)
_COMM_ACCESS = AgentPermission(
    resource=AgentPermissionResource.COMMUNICATION,
    access=PermissionAccess.WRITE,
)

DEFAULT_AGENT_DEFINITIONS: tuple[AgentDefinition, ...] = (
    AgentDefinition(
        role="research",
        description="Conducts research, gathers information, and synthesizes findings",
        capabilities=(_CAP_RESEARCH, _CAP_ANALYSIS, _CAP_SUMMARIZATION, _CAP_REASONING),
        permissions=(_READ_MEM, _READ_KNOWLEDGE, _COMM_ACCESS),
    ),
    AgentDefinition(
        role="engineering",
        description="Writes code, reviews implementations, and solves engineering problems",
        capabilities=(
            _CAP_PROGRAMMING,
            _CAP_ARCHITECTURE,
            _CAP_CODE_REVIEW,
            _CAP_DEBUGGING,
            _CAP_OPTIMIZATION,
            _CAP_TESTING,
        ),
        permissions=(_READ_WRITE_MEM, _READ_WRITE_KNOWLEDGE, _TOOL_ACCESS, _COMM_ACCESS),
    ),
    AgentDefinition(
        role="planning",
        description="Creates plans, decomposes work, and tracks progress",
        capabilities=(_CAP_PLANNING, _CAP_ANALYSIS, _CAP_REASONING, _CAP_REPORTING),
        permissions=(_READ_MEM, _READ_KNOWLEDGE, _COMM_ACCESS),
    ),
    AgentDefinition(
        role="documentation",
        description="Creates, maintains, and organizes documentation",
        capabilities=(_CAP_DOCUMENTATION, _CAP_SUMMARIZATION, _CAP_ANALYSIS),
        permissions=(_READ_MEM, _READ_WRITE_KNOWLEDGE, _COMM_ACCESS),
    ),
    AgentDefinition(
        role="automation",
        description="Automates workflows, pipelines, and repetitive tasks",
        capabilities=(_CAP_AUTOMATION, _CAP_PLANNING, _CAP_MONITORING, _CAP_ANALYSIS),
        permissions=(_READ_WRITE_MEM, _READ_KNOWLEDGE, _TOOL_ACCESS, _COMM_ACCESS),
    ),
    AgentDefinition(
        role="vision",
        description="Processes and analyzes visual information and images",
        capabilities=(_CAP_VISION, _CAP_ANALYSIS, _CAP_REASONING),
        permissions=(_READ_MEM, _READ_KNOWLEDGE, _COMM_ACCESS),
    ),
    AgentDefinition(
        role="voice",
        description="Processes voice and audio, handles speech interactions",
        capabilities=(_CAP_VOICE, _CAP_TRANSLATION, _CAP_COMMUNICATION),
        permissions=(_READ_MEM, _READ_KNOWLEDGE, _COMM_ACCESS),
    ),
    AgentDefinition(
        role="testing",
        description="Writes and executes tests, ensures quality",
        capabilities=(_CAP_TESTING, _CAP_ANALYSIS, _CAP_PROGRAMMING),
        permissions=(_READ_WRITE_MEM, _READ_KNOWLEDGE, _TOOL_ACCESS, _COMM_ACCESS),
    ),
    AgentDefinition(
        role="design",
        description="Designs systems, interfaces, and architecture",
        capabilities=(_CAP_DESIGN, _CAP_ARCHITECTURE, _CAP_ANALYSIS, _CAP_REASONING),
        permissions=(_READ_MEM, _READ_WRITE_KNOWLEDGE, _COMM_ACCESS),
    ),
)
