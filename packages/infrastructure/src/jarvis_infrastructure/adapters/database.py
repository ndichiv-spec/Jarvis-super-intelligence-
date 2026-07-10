from __future__ import annotations

import pickle
import sqlite3
import threading
from collections.abc import Mapping
from pathlib import Path
from typing import ClassVar, Protocol, TypeVar, cast

from jarvis_core.domain.agents import Agent, AgentRepository
from jarvis_core.domain.conversations import Conversation, ConversationRepository
from jarvis_core.domain.identity import IdentityRepository, User
from jarvis_core.domain.knowledge import KnowledgeItem, KnowledgeRepository
from jarvis_core.domain.memory import MemoryEntry, MemoryRepository
from jarvis_core.domain.notifications import Notification, NotificationRepository
from jarvis_core.domain.plugins import Plugin, PluginRepository
from jarvis_core.domain.projects import Project, ProjectRepository
from jarvis_core.domain.shared.value_objects import DomainIdentifier
from jarvis_core.domain.workflows import Workflow, WorkflowRepository

from jarvis_infrastructure.adapters.base import BaseInfrastructureAdapter
from jarvis_infrastructure.configuration import AdapterConfiguration
from jarvis_infrastructure.metadata import AdapterMetadata

T = TypeVar("T")


class RecordStore(Protocol):
    def put(self, namespace: str, key: str, payload: bytes) -> None: ...

    def get(self, namespace: str, key: str) -> bytes | None: ...


class PostgreSqlClient(Protocol):
    async def execute(self, statement: str, parameters: tuple[object, ...]) -> None: ...

    async def fetch_one(
        self,
        statement: str,
        parameters: tuple[object, ...],
    ) -> Mapping[str, object] | None: ...


class InMemoryRecordStore(RecordStore):
    def __init__(self) -> None:
        self._records: dict[str, dict[str, bytes]] = {}

    def put(self, namespace: str, key: str, payload: bytes) -> None:
        bucket = self._records.setdefault(namespace, {})
        bucket[key] = payload

    def get(self, namespace: str, key: str) -> bytes | None:
        return self._records.get(namespace, {}).get(key)


class SQLiteRecordStore(RecordStore):
    def __init__(self, path: str | Path) -> None:
        self._path = Path(path)
        self._lock = threading.Lock()
        self._connection = sqlite3.connect(self._path)
        self._initialize()

    def _initialize(self) -> None:
        with self._connection:
            self._connection.execute(
                """
                CREATE TABLE IF NOT EXISTS jarvis_records (
                    namespace TEXT NOT NULL,
                    record_key TEXT NOT NULL,
                    payload BLOB NOT NULL,
                    PRIMARY KEY(namespace, record_key)
                )
                """
            )

    def put(self, namespace: str, key: str, payload: bytes) -> None:
        with self._lock, self._connection:
            self._connection.execute(
                """
                INSERT INTO jarvis_records(namespace, record_key, payload)
                VALUES(?, ?, ?)
                ON CONFLICT(namespace, record_key)
                DO UPDATE SET payload = excluded.payload
                """,
                (namespace, key, payload),
            )

    def get(self, namespace: str, key: str) -> bytes | None:
        with self._lock:
            cursor = self._connection.execute(
                "SELECT payload FROM jarvis_records WHERE namespace = ? AND record_key = ?",
                (namespace, key),
            )
            row = cursor.fetchone()
        return None if row is None else cast(bytes, row[0])

    def close(self) -> None:
        self._connection.close()


class PostgreSqlRecordStore(RecordStore):
    def __init__(self, *, client: PostgreSqlClient, table_name: str = "jarvis_records") -> None:
        self._client = client
        self._table_name = table_name

    def put(self, namespace: str, key: str, payload: bytes) -> None:
        raise RuntimeError(
            "PostgreSQL synchronous put is unsupported. "
            "Use the asynchronous adapter API for writes."
        )

    def get(self, namespace: str, key: str) -> bytes | None:
        raise RuntimeError(
            "PostgreSQL synchronous get is unsupported. Use the asynchronous adapter API for reads."
        )

    async def put_async(self, namespace: str, key: str, payload: bytes) -> None:
        statement = f"""
            INSERT INTO {self._table_name}(namespace, record_key, payload)
            VALUES($1, $2, $3)
            ON CONFLICT(namespace, record_key)
            DO UPDATE SET payload = EXCLUDED.payload
        """
        await self._client.execute(statement, (namespace, key, payload))

    async def get_async(self, namespace: str, key: str) -> bytes | None:
        statement = (
            f"SELECT payload FROM {self._table_name} WHERE namespace = $1 AND record_key = $2"
        )
        row = await self._client.fetch_one(statement, (namespace, key))
        if row is None:
            return None
        payload = row.get("payload")
        return None if payload is None else cast(bytes, payload)


class DomainRepositoryAdapter(
    AgentRepository,
    ConversationRepository,
    IdentityRepository,
    KnowledgeRepository,
    MemoryRepository,
    NotificationRepository,
    PluginRepository,
    ProjectRepository,
    WorkflowRepository,
):
    _NAMESPACE_BY_TYPE: ClassVar[dict[type[object], str]] = {
        Agent: "agents",
        Conversation: "conversations",
        KnowledgeItem: "knowledge",
        MemoryEntry: "memories",
        Notification: "notifications",
        Plugin: "plugins",
        Project: "projects",
        Workflow: "workflows",
        User: "users",
    }

    def __init__(self, *, store: RecordStore) -> None:
        self._store = store

    def save(self, aggregate: object) -> None:
        namespace = self._resolve_namespace(aggregate)
        identifier = self._extract_identifier(aggregate)
        self._store.put(namespace, self._identifier_key(identifier), pickle.dumps(aggregate))

    def get(self, conversation_id: DomainIdentifier) -> Conversation | None:
        payload = self._store.get("conversations", self._identifier_key(conversation_id))
        if payload is None:
            return None
        record = pickle.loads(payload)
        return cast(Conversation, record)

    def save_user(self, user: User) -> None:
        self._store.put("users", self._identifier_key(user.id), pickle.dumps(user))

    def get_user(self, user_id: DomainIdentifier) -> User | None:
        payload = self._store.get("users", self._identifier_key(user_id))
        if payload is None:
            return None
        record = pickle.loads(payload)
        return cast(User, record)

    @classmethod
    def _resolve_namespace(cls, aggregate: object) -> str:
        for candidate_type, namespace in cls._NAMESPACE_BY_TYPE.items():
            if isinstance(aggregate, candidate_type):
                return namespace
        raise TypeError(f"Unsupported aggregate type: {type(aggregate).__name__}")

    @staticmethod
    def _extract_identifier(value: object) -> DomainIdentifier:
        identifier = getattr(value, "id", None)
        if not isinstance(identifier, DomainIdentifier):
            raise TypeError("Aggregate must expose an `id` attribute of type DomainIdentifier.")
        return identifier

    @staticmethod
    def _identifier_key(identifier: DomainIdentifier) -> str:
        return str(identifier.value)


class SQLiteDatabaseAdapter(BaseInfrastructureAdapter):
    def __init__(self, *, path: str = ":memory:") -> None:
        super().__init__(
            metadata=AdapterMetadata(
                identifier="database.sqlite",
                version="1.0.0",
                provider="sqlite",
                capabilities=("persistence", "development", "repositories"),
                configuration_profile="default",
                compatibility=("repository:v1",),
            )
        )
        self._path = path
        self._store: SQLiteRecordStore | None = None
        self._repositories: DomainRepositoryAdapter | None = None

    async def configure(self, configuration: AdapterConfiguration) -> None:
        await super().configure(configuration)
        self._path = configuration.settings.get("path", self._path)

    async def start(self) -> None:
        self._store = SQLiteRecordStore(path=self._path)
        self._repositories = DomainRepositoryAdapter(store=self._store)
        await super().start()

    async def stop(self) -> None:
        if self._store is not None:
            self._store.close()
        await super().stop()

    @property
    def repositories(self) -> DomainRepositoryAdapter:
        if self._repositories is None:
            raise RuntimeError("SQLiteDatabaseAdapter is not started.")
        return self._repositories


class PostgreSQLDatabaseAdapter(BaseInfrastructureAdapter):
    def __init__(
        self, *, client: PostgreSqlClient | None = None, table_name: str = "jarvis_records"
    ) -> None:
        super().__init__(
            metadata=AdapterMetadata(
                identifier="database.postgresql",
                version="1.0.0",
                provider="postgresql",
                capabilities=("persistence", "repositories", "production"),
                configuration_profile="default",
                compatibility=("repository:v1",),
            )
        )
        self._client = client
        self._table_name = table_name
        self._store: PostgreSqlRecordStore | None = None

    async def configure(self, configuration: AdapterConfiguration) -> None:
        await super().configure(configuration)
        self._table_name = configuration.settings.get("table_name", self._table_name)

    async def start(self) -> None:
        if self._client is None:
            raise RuntimeError("PostgreSQL client is required to start PostgreSQLDatabaseAdapter.")
        self._store = PostgreSqlRecordStore(client=self._client, table_name=self._table_name)
        await super().start()

    @property
    def store(self) -> PostgreSqlRecordStore:
        if self._store is None:
            raise RuntimeError("PostgreSQLDatabaseAdapter is not started.")
        return self._store
