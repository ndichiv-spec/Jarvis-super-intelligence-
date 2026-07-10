from __future__ import annotations

import asyncio
import json
from collections.abc import Mapping
from typing import Any

from jarvis_api.gateway.app import create_gateway_app


async def _invoke(
    app: Any,
    *,
    method: str,
    path: str,
    body: bytes = b"",
    headers: Mapping[str, str] | None = None,
) -> tuple[int, Mapping[str, str], str]:
    sent_messages: list[dict[str, object]] = []
    payload_sent = False

    req_headers = headers or {}
    if body and "content-type" not in {k.lower() for k in req_headers}:
        req_headers = {**req_headers, "content-type": "application/json"}

    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": method,
        "scheme": "http",
        "path": path,
        "raw_path": path.encode(),
        "query_string": b"",
        "headers": [
            (key.lower().encode(), value.encode())
            for key, value in req_headers.items()
        ],
        "client": ("127.0.0.1", 9000),
        "server": ("testserver", 80),
    }

    async def receive() -> dict[str, Any]:
        nonlocal payload_sent
        if not payload_sent:
            payload_sent = True
            return {"type": "http.request", "body": body, "more_body": False}
        return {"type": "http.disconnect"}

    async def send(message: dict[str, Any]) -> None:
        sent_messages.append(message)

    await app(scope, receive, send)

    status = 200
    response_headers: Mapping[str, str] = {}
    response_body_parts: list[str] = []

    for msg in sent_messages:
        msg_type = msg.get("type")
        if msg_type == "http.response.start":
            status = msg.get("status", 200)
            raw_headers = msg.get("headers", [])
            response_headers = {
                k.decode(): v.decode()
                for k, v in raw_headers
            }
        elif msg_type == "http.response.body":
            chunk = msg.get("body", b"")
            if chunk:
                response_body_parts.append(chunk.decode("utf-8", errors="replace"))

    return status, response_headers, "".join(response_body_parts)


def test_agents_list() -> None:
    app = create_gateway_app()
    status, _, body = asyncio.run(_invoke(app, method="GET", path="/agents/"))
    assert status == 200
    data = json.loads(body)
    assert "agents" in data
    assert isinstance(data["agents"], list)
    assert len(data["agents"]) > 0


def test_agents_list_has_required_fields() -> None:
    app = create_gateway_app()
    _, _, body = asyncio.run(_invoke(app, method="GET", path="/agents/"))
    data = json.loads(body)
    for agent in data["agents"]:
        assert "id" in agent
        assert "name" in agent
        assert "role" in agent
        assert "status" in agent
        assert "capabilities" in agent


def test_agents_list_contains_all_system_agents() -> None:
    app = create_gateway_app()
    _, _, body = asyncio.run(_invoke(app, method="GET", path="/agents/"))
    data = json.loads(body)
    names = {a["name"] for a in data["agents"]}
    assert "Planner" in names
    assert "Coding" in names
    assert "Research" in names
    assert "Memory" in names
    assert "Automation" in names
    assert "Desktop" in names
    assert "WebIntelligence" in names
    assert "Vision" in names
    assert "Voice" in names
    assert "Communication" in names


def test_agents_list_roles() -> None:
    app = create_gateway_app()
    _, _, body = asyncio.run(_invoke(app, method="GET", path="/agents/"))
    data = json.loads(body)
    roles = {a["role"] for a in data["agents"]}
    assert "planner" in roles
    assert "coding" in roles
    assert "research" in roles
    assert "memory" in roles
    assert "automation" in roles
    assert "desktop" in roles
    assert "web_intelligence" in roles
    assert "vision" in roles
    assert "voice" in roles
    assert "communication" in roles


def test_get_single_agent() -> None:
    app = create_gateway_app()
    _, _, list_body = asyncio.run(_invoke(app, method="GET", path="/agents/"))
    agents = json.loads(list_body)["agents"]
    assert len(agents) > 0
    first_id = agents[0]["id"]

    status, _, body = asyncio.run(_invoke(app, method="GET", path=f"/agents/{first_id}"))
    assert status == 200
    data = json.loads(body)
    assert data["id"] == first_id


def test_get_nonexistent_agent() -> None:
    app = create_gateway_app()
    status, _, body = asyncio.run(_invoke(app, method="GET", path="/agents/nonexistent-id"))
    assert status == 404


def test_agent_execute() -> None:
    app = create_gateway_app()
    payload = json.dumps({"agent_id": "sys-planner", "description": "Create a test plan"}).encode()
    status, _, body = asyncio.run(_invoke(
        app, method="POST", path="/agents/execute", body=payload,
        headers={"content-type": "application/json"},
    ))
    assert status == 200
    data = json.loads(body)
    assert "task_id" in data
    assert data["success"] is True


def test_agent_execute_missing_fields() -> None:
    app = create_gateway_app()
    payload = json.dumps({"agent_id": ""}).encode()
    status, _, body = asyncio.run(_invoke(
        app, method="POST", path="/agents/execute", body=payload,
        headers={"content-type": "application/json"},
    ))
    assert status == 400


def test_agent_health() -> None:
    app = create_gateway_app()
    status, _, body = asyncio.run(_invoke(app, method="GET", path="/agents/health"))
    assert status == 200
    data = json.loads(body)
    assert "health" in data


def test_system_status() -> None:
    app = create_gateway_app()
    status, _, body = asyncio.run(_invoke(app, method="GET", path="/agents/system/status"))
    assert status == 200
    data = json.loads(body)
    assert "status" in data
    assert "total_agents" in data["status"]
    assert data["status"]["total_agents"] > 0
