from __future__ import annotations

from fastapi import APIRouter, HTTPException

from jarvis_studio.studio_service import StudioService

router = APIRouter(prefix="/studio", tags=["studio"])

_service: StudioService | None = None


def _get_service() -> StudioService:
    global _service
    if _service is None:
        _service = StudioService()
    return _service


def _ok(data: object) -> dict:
    return {"ok": True, "data": data, "error": None, "metadata": {}}


def _error(status: int, message: str) -> HTTPException:
    return HTTPException(status_code=status, detail=message)


@router.get("/shell")
async def get_shell():
    svc = _get_service()
    return _ok(svc.get_shell_config().__dict__)


@router.get("/workspaces")
async def list_workspaces():
    svc = _get_service()
    return _ok([w.__dict__ for w in svc.list_workspaces()])


@router.get("/workspaces/{workspace_id}")
async def get_workspace(workspace_id: str):
    svc = _get_service()
    ws = svc.get_workspace(workspace_id)
    if ws is None:
        raise _error(404, f"Workspace not found: {workspace_id}")
    return _ok(ws.__dict__)


@router.post("/workspaces/{workspace_id}/activate")
async def activate_workspace(workspace_id: str):
    svc = _get_service()
    ws = svc.set_current_workspace(workspace_id)
    if ws is None:
        raise _error(404, f"Workspace not found: {workspace_id}")
    return _ok(ws.__dict__)


@router.get("/organizations")
async def list_organizations():
    svc = _get_service()
    return _ok([o.__dict__ for o in svc.list_organizations()])


@router.get("/dashboard/stats")
async def get_dashboard_stats():
    svc = _get_service()
    return _ok(svc.get_dashboard_stats().__dict__)


@router.get("/dashboard/metrics")
async def get_dashboard_metrics():
    svc = _get_service()
    return _ok([m.__dict__ for m in svc.get_metrics()])


@router.get("/agents")
async def list_agents():
    svc = _get_service()
    return _ok([a.__dict__ for a in svc.list_agents()])


@router.get("/agents/{agent_id}")
async def get_agent(agent_id: str):
    svc = _get_service()
    agent = svc.get_agent(agent_id)
    if agent is None:
        raise _error(404, f"Agent not found: {agent_id}")
    return _ok(agent.__dict__)


@router.get("/agents/health")
async def get_agent_health():
    svc = _get_service()
    return _ok(svc.get_agent_health())


@router.get("/workflows")
async def list_workflows():
    svc = _get_service()
    return _ok([w.__dict__ for w in svc.list_workflows()])


@router.get("/workflows/{workflow_id}")
async def get_workflow(workflow_id: str):
    svc = _get_service()
    wf = svc.get_workflow(workflow_id)
    if wf is None:
        raise _error(404, f"Workflow not found: {workflow_id}")
    return _ok(wf.__dict__)


@router.get("/workflows/{workflow_id}/executions")
async def list_workflow_executions(workflow_id: str):
    svc = _get_service()
    return _ok([e.__dict__ for e in svc.list_workflow_executions(workflow_id)])


@router.get("/workflows/executions/{execution_id}")
async def get_workflow_execution(execution_id: str):
    svc = _get_service()
    return _ok({"id": execution_id, "status": "completed"})


@router.get("/tools")
async def list_tools():
    svc = _get_service()
    return _ok([t.__dict__ for t in svc.list_tools()])


@router.get("/tools/{tool_id}")
async def get_tool(tool_id: str):
    svc = _get_service()
    tool = svc.get_tool(tool_id)
    if tool is None:
        raise _error(404, f"Tool not found: {tool_id}")
    return _ok(tool.__dict__)


@router.get("/tools/{tool_id}/executions")
async def list_tool_executions(tool_id: str):
    svc = _get_service()
    return _ok([e.__dict__ for e in svc.list_tool_executions(tool_id)])


@router.get("/extensions")
async def list_extensions():
    svc = _get_service()
    return _ok([e.__dict__ for e in svc.list_extensions()])


@router.get("/extensions/{ext_id}")
async def get_extension(ext_id: str):
    svc = _get_service()
    ext = svc.get_extension(ext_id)
    if ext is None:
        raise _error(404, f"Extension not found: {ext_id}")
    return _ok(ext.__dict__)


@router.post("/extensions/{ext_id}/install")
async def install_extension(ext_id: str):
    svc = _get_service()
    ext = svc.install_extension(ext_id)
    if ext is None:
        raise _error(404, f"Extension not found: {ext_id}")
    return _ok(ext.__dict__)


@router.delete("/extensions/{ext_id}")
async def uninstall_extension(ext_id: str):
    svc = _get_service()
    svc.uninstall_extension(ext_id)
    return _ok({"success": True})


@router.post("/extensions/{ext_id}/update")
async def update_extension(ext_id: str):
    svc = _get_service()
    ext = svc.update_extension(ext_id)
    if ext is None:
        raise _error(404, f"Extension not found: {ext_id}")
    return _ok(ext.__dict__)


@router.get("/knowledge/collections")
async def list_knowledge_collections():
    svc = _get_service()
    return _ok([c.__dict__ for c in svc.list_knowledge_collections()])


@router.get("/knowledge/collections/{collection_id}")
async def get_knowledge_collection(collection_id: str):
    svc = _get_service()
    coll = svc.get_knowledge_collection(collection_id)
    if coll is None:
        raise _error(404, f"Collection not found: {collection_id}")
    return _ok(coll.__dict__)


@router.get("/knowledge/collections/{collection_id}/documents")
async def list_knowledge_documents(collection_id: str):
    svc = _get_service()
    return _ok([d.__dict__ for d in svc.list_knowledge_documents(collection_id)])


@router.get("/knowledge/search")
async def search_knowledge(q: str = ""):
    svc = _get_service()
    return _ok([d.__dict__ for d in svc.search_knowledge(q)])


@router.get("/memory")
async def list_memory():
    svc = _get_service()
    return _ok([m.__dict__ for m in svc.list_memory_items()])


@router.get("/memory/policies")
async def list_memory_policies():
    svc = _get_service()
    return _ok([p.__dict__ for p in svc.list_memory_policies()])


@router.post("/memory/{item_id}/archive")
async def archive_memory(item_id: str):
    svc = _get_service()
    return _ok({"success": True})


@router.delete("/memory/{item_id}")
async def delete_memory(item_id: str):
    svc = _get_service()
    return _ok({"success": True})


@router.get("/events/stream")
async def stream_events():
    svc = _get_service()
    return _ok([e.__dict__ for e in svc.list_events()])


@router.get("/events")
async def search_events(severity: str = "", type: str = ""):
    svc = _get_service()
    params = {}
    if severity:
        params["severity"] = severity
    if type:
        params["type"] = type
    return _ok([e.__dict__ for e in svc.search_events(params)])


@router.get("/events/{event_id}")
async def get_event(event_id: str):
    svc = _get_service()
    evt = svc.get_event(event_id)
    if evt is None:
        raise _error(404, f"Event not found: {event_id}")
    return _ok(evt.__dict__)


@router.get("/ai/providers")
async def list_ai_providers():
    svc = _get_service()
    return _ok([p.__dict__ for p in svc.list_ai_providers()])


@router.get("/ai/providers/{provider_id}/models")
async def list_ai_models(provider_id: str):
    svc = _get_service()
    return _ok(svc.list_ai_models(provider_id))


@router.get("/ai/usage")
async def get_ai_usage():
    svc = _get_service()
    return _ok(svc.get_ai_usage())


@router.get("/security/users")
async def list_security_users():
    svc = _get_service()
    return _ok([u.__dict__ for u in svc.list_security_users()])


@router.get("/security/roles")
async def list_security_roles():
    svc = _get_service()
    return _ok([r.__dict__ for r in svc.list_security_roles()])


@router.get("/security/policies")
async def list_security_policies():
    svc = _get_service()
    return _ok([p.__dict__ for p in svc.list_security_policies()])


@router.get("/security/audit")
async def list_audit_logs():
    svc = _get_service()
    return _ok([a.__dict__ for a in svc.list_audit_logs()])


@router.get("/infrastructure")
async def list_infrastructure():
    svc = _get_service()
    return _ok([c.__dict__ for c in svc.list_infrastructure_components()])


@router.get("/infrastructure/health")
async def get_infrastructure_health():
    svc = _get_service()
    return _ok(svc.get_infrastructure_health())


@router.get("/observability/metrics")
async def get_observability_metrics():
    svc = _get_service()
    return _ok([m.__dict__ for m in svc.list_observability_metrics()])


@router.get("/observability/logs")
async def get_observability_logs():
    svc = _get_service()
    return _ok([l.__dict__ for l in svc.list_observability_logs()])


@router.get("/observability/traces")
async def get_observability_traces():
    svc = _get_service()
    return _ok([t.__dict__ for t in svc.list_observability_traces()])


@router.get("/observability/alerts")
async def get_observability_alerts():
    svc = _get_service()
    return _ok([a.__dict__ for a in svc.list_observability_alerts()])


@router.get("/api-explorer/endpoints")
async def list_api_endpoints():
    svc = _get_service()
    return _ok([e.__dict__ for e in svc.list_api_endpoints()])


@router.post("/api-explorer/execute")
async def execute_api_explorer(body: dict):
    svc = _get_service()
    method = body.get("method", "GET")
    path = body.get("path", "")
    return _ok({"method": method, "path": path, "status": "success", "result": {}})


@router.get("/config/feature-flags")
async def list_feature_flags():
    svc = _get_service()
    return _ok([f.__dict__ for f in svc.list_feature_flags()])


@router.get("/config/runtime")
async def list_runtime_configs():
    svc = _get_service()
    return _ok([c.__dict__ for c in svc.list_runtime_configs()])


@router.get("/config/profiles")
async def list_profiles():
    svc = _get_service()
    return _ok([p.__dict__ for p in svc.list_profiles()])


@router.get("/console/logs")
async def list_console_logs():
    svc = _get_service()
    return _ok([c.__dict__ for c in svc.list_console_logs()])


@router.post("/console/execute")
async def execute_console_command(body: dict):
    svc = _get_service()
    command = body.get("command", "")
    if not command:
        raise _error(400, "command is required")
    result = svc.execute_console_command(command)
    return _ok(result.__dict__)


@router.get("/communication/analytics")
async def get_communication_analytics():
    svc = _get_service()
    return _ok(svc.get_communication_analytics().__dict__)


@router.get("/communication/conversations")
async def list_communication_conversations():
    svc = _get_service()
    return _ok([c.__dict__ for c in svc.list_communication_conversations()])


@router.get("/communication/messages")
async def list_communication_messages(conversation_id: str | None = None):
    svc = _get_service()
    return _ok([m.__dict__ for m in svc.list_communication_messages(conversation_id)])


@router.get("/communication/streams")
async def list_communication_streams():
    svc = _get_service()
    return _ok([s.__dict__ for s in svc.list_communication_streams()])
