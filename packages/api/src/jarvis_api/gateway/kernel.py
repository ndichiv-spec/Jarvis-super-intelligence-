from __future__ import annotations

from dataclasses import replace
from time import perf_counter

from jarvis_api.gateway.errors import GatewayErrorCode, GatewayErrorContract, GatewayException
from jarvis_api.gateway.metadata import ApiMetadataRegistry
from jarvis_api.gateway.observability import InMemoryObservability
from jarvis_api.gateway.pipeline import RequestPipeline, ResponsePipeline
from jarvis_api.gateway.policies import GatewayPolicyEngine
from jarvis_api.gateway.protocol_registry import ProtocolRegistry
from jarvis_api.gateway.protocols import (
    AuthorizationServiceProtocol,
    RequestValidatorProtocol,
    RouteExecutorProtocol,
)
from jarvis_api.gateway.rate_limit import RateLimiter
from jarvis_api.gateway.routing import RouteDefinition, RoutingEngine
from jarvis_api.gateway.sessions import SessionManager
from jarvis_api.gateway.streaming import StreamingEngine
from jarvis_api.gateway.types import GatewayRequest, GatewayResponse, StreamKinds
from jarvis_api.gateway.versioning import ApiVersionManager, VersionResolution


class NoOpRequestValidator(RequestValidatorProtocol):
    async def validate(self, request: GatewayRequest) -> None:
        del request


class AllowAllAuthorizationService(AuthorizationServiceProtocol):
    async def authorize(self, request: GatewayRequest, route: object) -> None:
        del request
        del route


class MissingRouteExecutor(RouteExecutorProtocol):
    async def execute(self, request: GatewayRequest, route: object) -> GatewayResponse:
        del request
        del route
        raise GatewayException.execution("No route executor configured for Service Gateway")


class GatewayKernel:
    def __init__(
        self,
        *,
        protocol_registry: ProtocolRegistry | None = None,
        routing_engine: RoutingEngine | None = None,
        request_pipeline: RequestPipeline | None = None,
        response_pipeline: ResponsePipeline | None = None,
        streaming_engine: StreamingEngine | None = None,
        session_manager: SessionManager | None = None,
        api_version_manager: ApiVersionManager | None = None,
        rate_limiter: RateLimiter | None = None,
        policy_engine: GatewayPolicyEngine | None = None,
        metadata_registry: ApiMetadataRegistry | None = None,
        request_validator: RequestValidatorProtocol | None = None,
        authorization_service: AuthorizationServiceProtocol | None = None,
        route_executor: RouteExecutorProtocol | None = None,
        observability: InMemoryObservability | None = None,
    ) -> None:
        self._protocol_registry = protocol_registry or ProtocolRegistry.with_defaults()
        self._routing_engine = routing_engine or RoutingEngine()
        self._request_pipeline = request_pipeline or RequestPipeline()
        self._response_pipeline = response_pipeline or ResponsePipeline()
        self._streaming_engine = streaming_engine or StreamingEngine()
        self._session_manager = session_manager or SessionManager()
        self._api_version_manager = api_version_manager or ApiVersionManager()
        if not self._api_version_manager.list_versions():
            self._api_version_manager.register("1.0.0")
        self._rate_limiter = rate_limiter or RateLimiter()
        self._policy_engine = policy_engine or GatewayPolicyEngine()
        self._metadata_registry = metadata_registry or ApiMetadataRegistry()
        self._request_validator = request_validator or NoOpRequestValidator()
        self._authorization_service = authorization_service or AllowAllAuthorizationService()
        self._route_executor = route_executor or MissingRouteExecutor()
        self._observability = observability or InMemoryObservability()

    async def handle(self, request: GatewayRequest) -> GatewayResponse:
        started_at = perf_counter()
        latency_tags = {"protocol": request.protocol}

        try:
            protocol_descriptor = self._protocol_registry.ensure_supported(request.protocol)
            version_resolution = self._api_version_manager.resolve(request.version)
            route = self._routing_engine.resolve(request.path, protocol=request.protocol)

            await self._request_validator.validate(request)
            transformed_request = await self._request_pipeline.execute(request)

            await self._authorization_service.authorize(transformed_request, route)

            rate_limit_decision = self._rate_limiter.evaluate(transformed_request)
            if not rate_limit_decision.allowed:
                raise GatewayException.rate_limit(
                    "Rate limit exceeded",
                    details={
                        "remaining": rate_limit_decision.remaining,
                        "retry_after_seconds": rate_limit_decision.retry_after_seconds,
                    },
                )

            self._policy_engine.enforce(
                transformed_request,
                route=route,
                resolved_version=version_resolution.resolved,
                protocol_descriptor=protocol_descriptor,
            )

            session = self._session_manager.open_or_touch(
                session_id=transformed_request.session_id,
                identity_id=transformed_request.subject_id,
                workspace_id=transformed_request.workspace_id,
                protocol=transformed_request.protocol,
                metadata=transformed_request.metadata,
            )

            raw_response = await self._route_executor.execute(transformed_request, route)
            normalized = self._normalize_response(
                raw_response,
                request=transformed_request,
                route=route,
                session_id=session.session_id,
                version_resolution=version_resolution,
            )

            processed = await self._response_pipeline.execute(normalized)
            if processed.stream is not None:
                coordinated_stream = self._streaming_engine.coordinate(
                    processed.stream,
                    kind=StreamKinds.NOTIFICATION,
                    channel_id=transformed_request.request_id,
                    metadata={"route": route.identifier, "subsystem": route.subsystem},
                )
                processed = replace(processed, stream=coordinated_stream)

            self._observability.increment(
                "gateway.requests.success",
                tags={"protocol": request.protocol, "route": route.identifier},
            )
            return processed
        except GatewayException as gateway_exception:
            self._observability.increment(
                "gateway.requests.error",
                tags={"code": gateway_exception.contract.code.value},
            )
            return self._build_error_response(gateway_exception.contract, request=request)
        except Exception as unknown_error:
            error_contract = GatewayErrorContract(
                code=GatewayErrorCode.UNKNOWN,
                message="Unhandled gateway failure",
                status_code=500,
                retryable=False,
                details={"error": str(unknown_error)},
            )
            self._observability.increment(
                "gateway.requests.error",
                tags={"code": error_contract.code.value},
            )
            return self._build_error_response(error_contract, request=request)
        finally:
            latency_ms = (perf_counter() - started_at) * 1000
            self._observability.record_latency(
                "gateway.request.latency_ms",
                latency_ms,
                tags=latency_tags,
            )

    def register_route(self, route: RouteDefinition) -> None:
        self._routing_engine.register_route(route)

    def health(self) -> dict[str, object]:
        session_count = len(self._session_manager.active_sessions())
        return {
            "gateway": "service",
            "status": "ok",
            "sessions": session_count,
            "observability": dict(self._observability.health()),
        }

    def stats(self) -> dict[str, object]:
        return {
            "observability": dict(self._observability.stats()),
            "active_sessions": len(self._session_manager.active_sessions()),
            "registered_routes": len(self._routing_engine.list_routes()),
            "registered_protocols": len(self._protocol_registry.list_protocols()),
            "api_versions": [
                str(record.version)
                for record in self._api_version_manager.list_versions()
            ],
            "api_metadata": [
                metadata.identifier
                for metadata in self._metadata_registry.list_all()
            ],
        }

    def _normalize_response(
        self,
        response: GatewayResponse,
        *,
        request: GatewayRequest,
        route: RouteDefinition,
        session_id: str,
        version_resolution: VersionResolution,
    ) -> GatewayResponse:
        headers = dict(response.headers)
        headers.setdefault("x-jarvis-request-id", request.request_id)
        headers.setdefault("x-jarvis-session-id", session_id)

        metadata = {
            "request_id": request.request_id,
            "session_id": session_id,
            "route": route.identifier,
            "subsystem": route.subsystem,
            "api_version": str(version_resolution.resolved),
        }
        if version_resolution.deprecation_notice:
            metadata["deprecation_notice"] = version_resolution.deprecation_notice
        if version_resolution.migration_guidance:
            metadata["migration_guidance"] = version_resolution.migration_guidance

        body = {
            "ok": response.error is None,
            "data": response.body if response.error is None else None,
            "error": response.error.to_dict() if response.error else None,
            "metadata": metadata,
        }
        return GatewayResponse(
            status_code=response.status_code,
            body=body,
            headers=headers,
            metadata=metadata,
            stream=response.stream,
            protocol=request.protocol,
            error=response.error,
        )

    @staticmethod
    def _build_error_response(
        contract: GatewayErrorContract,
        *,
        request: GatewayRequest,
    ) -> GatewayResponse:
        body = {
            "ok": False,
            "data": None,
            "error": contract.to_dict(),
            "metadata": {"request_id": request.request_id},
        }
        return GatewayResponse(
            status_code=contract.status_code,
            body=body,
            headers={"x-jarvis-request-id": request.request_id},
            metadata={"request_id": request.request_id},
            protocol=request.protocol,
            error=contract,
        )
