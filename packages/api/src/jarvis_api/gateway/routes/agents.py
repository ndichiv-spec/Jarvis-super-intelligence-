from __future__ import annotations

from fastapi import APIRouter, HTTPException

from jarvis_agents import DEFAULT_AGENT_DEFINITIONS, AgentManager
from jarvis_agents.agents import (
    AutomationAgent,
    CodingAgent,
    CommunicationAgent,
    DesktopAgent,
    MemoryAgent,
    PlannerAgent,
    ResearchAgent,
    VisionAgent,
    VoiceAgent,
    WebIntelligenceAgent,
)
from jarvis_agents.models import AgentDefinition, AgentTask, TaskPriority

router = APIRouter(prefix="/agents", tags=["agents"])

SYSTEM_AGENTS: dict[str, object] = {}
_manager: AgentManager | None = None


def _get_manager() -> AgentManager:
    global _manager
    if _manager is None:
        _manager = AgentManager()
    return _manager


def _ensure_system_agents() -> None:
    mgr = _get_manager()
    if SYSTEM_AGENTS:
        return

    all_agents: list[tuple[str, object]] = [
        ("planner", PlannerAgent(agent_id="sys-planner")),
        ("coding", CodingAgent(agent_id="sys-coding")),
        ("research", ResearchAgent(agent_id="sys-research")),
        ("memory", MemoryAgent(agent_id="sys-memory")),
        ("automation", AutomationAgent(agent_id="sys-automation")),
        ("desktop", DesktopAgent(agent_id="sys-desktop")),
        ("web_intelligence", WebIntelligenceAgent(agent_id="sys-webintel")),
        ("vision", VisionAgent(agent_id="sys-vision")),
        ("voice", VoiceAgent(agent_id="sys-voice")),
        ("communication", CommunicationAgent(agent_id="sys-communication")),
    ]

    for name, agent in all_agents:
        agent.initialize()
        agent.start()
        SYSTEM_AGENTS[name] = agent

    for name, agent in SYSTEM_AGENTS.items():
        defn = next((d for d in DEFAULT_AGENT_DEFINITIONS if d.role == name), None)
        if defn is None:
            caps = tuple(agent.capabilities)
            defn = AgentDefinition(
                role=name,
                description=agent.description,
                capabilities=caps,
                permissions=agent.permissions,
            )
        mgr.register_agent(defn, agent_id=agent.agent_id, name=agent.name, owner="system", workspace="default")
        mgr.activate_agent(agent.agent_id)


@router.get("/")
async def list_agents():
    _ensure_system_agents()
    mgr = _get_manager()
    agents = mgr.list_agents()
    return {
        "agents": [
            {
                "id": a.identifier,
                "name": a.name,
                "role": a.role,
                "description": a.description,
                "status": a.status.value,
                "capabilities": [{"name": c.name, "description": c.description} for c in a.capabilities],
                "version": a.version,
                "owner": a.owner,
                "workspace": a.workspace,
                "created_at": a.created_at.isoformat(),
                "updated_at": a.updated_at.isoformat(),
            }
            for a in agents
        ],
    }


@router.get("/system/status")
async def system_status():
    _ensure_system_agents()
    mgr = _get_manager()
    return {"status": mgr.get_system_status()}


@router.get("/health")
async def agent_health():
    _ensure_system_agents()
    mgr = _get_manager()
    return {"health": mgr.health_summary()}


@router.get("/metrics")
async def agent_metrics():
    _ensure_system_agents()
    mgr = _get_manager()
    return {"metrics": mgr.metrics_summary()}


@router.get("/{agent_id}")
async def get_agent(agent_id: str):
    _ensure_system_agents()
    mgr = _get_manager()
    agent = mgr.get_agent(agent_id)
    if agent is None:
        raise HTTPException(status_code=404, detail=f"Agent not found: {agent_id}")
    return {
        "id": agent.identifier,
        "name": agent.name,
        "role": agent.role,
        "description": agent.description,
        "status": agent.status.value,
        "capabilities": [{"name": c.name, "description": c.description} for c in agent.capabilities],
        "version": agent.version,
        "owner": agent.owner,
        "workspace": agent.workspace,
        "created_at": agent.created_at.isoformat(),
        "updated_at": agent.updated_at.isoformat(),
    }


@router.post("/register")
async def register_agent(body: dict):
    mgr = _get_manager()
    role = body.get("role", "")
    if not role:
        raise HTTPException(status_code=400, detail="role is required")
    defn = next((d for d in DEFAULT_AGENT_DEFINITIONS if d.role == role), None)
    if defn is None:
        raise HTTPException(status_code=400, detail=f"Unknown role: {role}")
    agent_id = body.get("agent_id")
    name = body.get("name")
    owner = body.get("owner", "user")
    workspace = body.get("workspace", "default")
    agent = mgr.register_agent(defn, agent_id=agent_id, name=name, owner=owner, workspace=workspace)
    mgr.activate_agent(agent.identifier)
    return {
        "id": agent.identifier,
        "name": agent.name,
        "role": agent.role,
        "status": agent.status.value,
    }


@router.post("/execute")
async def execute_agent(body: dict):
    _ensure_system_agents()
    agent_id = body.get("agent_id", "")
    description = body.get("description", "")
    if not agent_id or not description:
        raise HTTPException(status_code=400, detail="agent_id and description are required")
    mgr = _get_manager()
    task = AgentTask(
        task_id=f"task-{agent_id}",
        description=description,
        assigned_agent_id=agent_id,
        priority=TaskPriority.MEDIUM,
    )
    result = mgr.execute_task(task)
    return {
        "task_id": task.task_id,
        "agent_id": agent_id,
        "success": result.success,
        "output": result.output,
        "error": result.error_message,
    }
