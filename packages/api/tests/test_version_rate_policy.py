from datetime import UTC, datetime, timedelta

from jarvis_api.gateway.errors import GatewayException
from jarvis_api.gateway.policies import GatewayPolicy, GatewayPolicyEngine
from jarvis_api.gateway.protocol_registry import ProtocolDescriptor
from jarvis_api.gateway.rate_limit import RateLimiter, RateLimitPolicy, RateLimitScope
from jarvis_api.gateway.routing import RouteDefinition
from jarvis_api.gateway.types import GatewayRequest, Protocols
from jarvis_api.gateway.versioning import ApiVersion, ApiVersionManager


def test_api_version_manager_supports_deprecation_and_fallback() -> None:
    manager = ApiVersionManager()
    manager.register("1.0.0", deprecated=True, replacement="1.1.0", migration_guidance="Upgrade to 1.1")
    manager.register("1.1.0")

    resolution = manager.resolve("1.0.5")

    assert str(resolution.resolved) == "1.0.0"
    assert resolution.deprecation_notice is not None
    assert resolution.migration_guidance == "Upgrade to 1.1"


def test_rate_limiter_enforces_user_limit_policy() -> None:
    limiter = RateLimiter(
        policies=(
            RateLimitPolicy(scope=RateLimitScope.USER, limit=1, window=timedelta(minutes=1)),
        )
    )
    request = GatewayRequest.new(
        protocol=Protocols.REST,
        path="/brain",
        version="1.0.0",
        subject_id="user-1",
    )

    now = datetime.now(tz=UTC)
    first = limiter.evaluate(request, now=now)
    second = limiter.evaluate(request, now=now)

    assert first.allowed is True
    assert second.allowed is False
    assert second.retry_after_seconds is not None


def test_policy_engine_blocks_restricted_protocol_and_workspace_violation() -> None:
    policy_engine = GatewayPolicyEngine(
        GatewayPolicy(
            restricted_protocols=(Protocols.MCP,),
            workspace_subsystem_rules={"workspace-a": ("knowledge",)},
            minimum_version=ApiVersion(major=1, minor=0, patch=0),
        )
    )
    route = RouteDefinition(identifier="brain-route", subsystem="brain", path_prefix="/brain")
    descriptor = ProtocolDescriptor(name=Protocols.REST, transport="http", supports_streaming=False)

    request = GatewayRequest.new(
        protocol=Protocols.REST,
        path="/brain",
        version="1.0.0",
        workspace_id="workspace-a",
    )

    try:
        policy_engine.enforce(
            request,
            route=route,
            resolved_version=ApiVersion(major=1, minor=0, patch=0),
            protocol_descriptor=descriptor,
        )
    except GatewayException as error:
        assert error.contract.code.value == "policy_violation"
    else:
        msg = "Expected workspace subsystem policy violation"
        raise AssertionError(msg)
