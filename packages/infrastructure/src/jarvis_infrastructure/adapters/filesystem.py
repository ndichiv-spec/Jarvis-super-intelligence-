from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from jarvis_infrastructure.adapters.base import BaseInfrastructureAdapter
from jarvis_infrastructure.metadata import AdapterMetadata


class FileAuthorizationPort(Protocol):
    def is_allowed(
        self, *, actor_id: str, workspace_id: str, path: str, operation: str
    ) -> bool: ...


class CloudFileClient(Protocol):
    async def read(self, path: str) -> bytes: ...

    async def write(self, path: str, content: bytes) -> None: ...

    async def delete(self, path: str) -> None: ...

    async def list(self, prefix: str) -> tuple[str, ...]: ...


@dataclass(frozen=True, slots=True)
class AccessRequest:
    actor_id: str
    workspace_id: str
    path: str
    operation: str


class _AuthorizedFileSystemAdapter(BaseInfrastructureAdapter):
    def __init__(
        self,
        *,
        identifier: str,
        provider: str,
        authorizer: FileAuthorizationPort,
    ) -> None:
        super().__init__(
            metadata=AdapterMetadata(
                identifier=identifier,
                version="1.0.0",
                provider=provider,
                capabilities=("filesystem", "authorized-access"),
                configuration_profile="default",
                compatibility=("filesystem:v1", "security:v1"),
            )
        )
        self._authorizer = authorizer

    def _require_authorized(self, request: AccessRequest) -> None:
        if not self._authorizer.is_allowed(
            actor_id=request.actor_id,
            workspace_id=request.workspace_id,
            path=request.path,
            operation=request.operation,
        ):
            raise PermissionError(
                "Access denied for actor "
                f"'{request.actor_id}' to '{request.path}' ({request.operation})."
            )


class LocalFileSystemAdapter(_AuthorizedFileSystemAdapter):
    def __init__(self, *, root: str = ".", authorizer: FileAuthorizationPort) -> None:
        super().__init__(
            identifier="filesystem.local",
            provider="local",
            authorizer=authorizer,
        )
        self._root = Path(root)

    async def read(self, *, actor_id: str, workspace_id: str, path: str) -> bytes:
        request = AccessRequest(
            actor_id=actor_id, workspace_id=workspace_id, path=path, operation="read"
        )
        self._require_authorized(request)
        return self._resolve(path).read_bytes()

    async def write(self, *, actor_id: str, workspace_id: str, path: str, content: bytes) -> None:
        request = AccessRequest(
            actor_id=actor_id, workspace_id=workspace_id, path=path, operation="write"
        )
        self._require_authorized(request)
        target = self._resolve(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)

    async def delete(self, *, actor_id: str, workspace_id: str, path: str) -> None:
        request = AccessRequest(
            actor_id=actor_id, workspace_id=workspace_id, path=path, operation="delete"
        )
        self._require_authorized(request)
        target = self._resolve(path)
        if target.exists():
            target.unlink()

    async def list(self, *, actor_id: str, workspace_id: str, prefix: str = "") -> tuple[str, ...]:
        request = AccessRequest(
            actor_id=actor_id, workspace_id=workspace_id, path=prefix, operation="list"
        )
        self._require_authorized(request)
        root = self._resolve(prefix)
        if not root.exists():
            return ()
        results = [
            str(path.relative_to(self._root)).replace("\\", "/")
            for path in root.rglob("*")
            if path.is_file()
        ]
        results.sort()
        return tuple(results)

    def _resolve(self, relative_path: str) -> Path:
        safe = relative_path.strip().lstrip("/").replace("..", "")
        return self._root / safe


class VirtualFileSystemAdapter(_AuthorizedFileSystemAdapter):
    def __init__(self, *, authorizer: FileAuthorizationPort) -> None:
        super().__init__(
            identifier="filesystem.virtual",
            provider="virtual",
            authorizer=authorizer,
        )
        self._files: dict[str, bytes] = {}

    async def read(self, *, actor_id: str, workspace_id: str, path: str) -> bytes:
        self._require_authorized(
            AccessRequest(actor_id=actor_id, workspace_id=workspace_id, path=path, operation="read")
        )
        return self._files[path]

    async def write(self, *, actor_id: str, workspace_id: str, path: str, content: bytes) -> None:
        self._require_authorized(
            AccessRequest(
                actor_id=actor_id, workspace_id=workspace_id, path=path, operation="write"
            )
        )
        self._files[path] = content

    async def delete(self, *, actor_id: str, workspace_id: str, path: str) -> None:
        self._require_authorized(
            AccessRequest(
                actor_id=actor_id, workspace_id=workspace_id, path=path, operation="delete"
            )
        )
        self._files.pop(path, None)

    async def list(self, *, actor_id: str, workspace_id: str, prefix: str = "") -> tuple[str, ...]:
        self._require_authorized(
            AccessRequest(
                actor_id=actor_id, workspace_id=workspace_id, path=prefix, operation="list"
            )
        )
        return tuple(sorted(key for key in self._files if key.startswith(prefix)))


class CloudMappedFileSystemAdapter(_AuthorizedFileSystemAdapter):
    def __init__(
        self,
        *,
        authorizer: FileAuthorizationPort,
        client: CloudFileClient | None = None,
    ) -> None:
        super().__init__(
            identifier="filesystem.cloud_mapped",
            provider="cloud-mapped",
            authorizer=authorizer,
        )
        self._client = client

    async def start(self) -> None:
        if self._client is None:
            raise RuntimeError("Cloud file client is required.")
        await super().start()

    async def read(self, *, actor_id: str, workspace_id: str, path: str) -> bytes:
        self._require_authorized(
            AccessRequest(actor_id=actor_id, workspace_id=workspace_id, path=path, operation="read")
        )
        if self._client is None:
            raise RuntimeError("Cloud file client is not configured.")
        return await self._client.read(path)

    async def write(self, *, actor_id: str, workspace_id: str, path: str, content: bytes) -> None:
        self._require_authorized(
            AccessRequest(
                actor_id=actor_id, workspace_id=workspace_id, path=path, operation="write"
            )
        )
        if self._client is None:
            raise RuntimeError("Cloud file client is not configured.")
        await self._client.write(path, content)

    async def delete(self, *, actor_id: str, workspace_id: str, path: str) -> None:
        self._require_authorized(
            AccessRequest(
                actor_id=actor_id, workspace_id=workspace_id, path=path, operation="delete"
            )
        )
        if self._client is None:
            raise RuntimeError("Cloud file client is not configured.")
        await self._client.delete(path)

    async def list(self, *, actor_id: str, workspace_id: str, prefix: str = "") -> tuple[str, ...]:
        self._require_authorized(
            AccessRequest(
                actor_id=actor_id, workspace_id=workspace_id, path=prefix, operation="list"
            )
        )
        if self._client is None:
            raise RuntimeError("Cloud file client is not configured.")
        return await self._client.list(prefix)


class AllowAllAuthorizer(FileAuthorizationPort):
    def is_allowed(self, *, actor_id: str, workspace_id: str, path: str, operation: str) -> bool:
        _ = (actor_id, workspace_id, path, operation)
        return True


def normalize_paths(paths: Iterable[str]) -> tuple[str, ...]:
    return tuple(path.strip().replace("\\", "/") for path in paths)
