from __future__ import annotations

import asyncio
from collections.abc import Mapping

import pytest
from jarvis_infrastructure.adapters.base import BaseInfrastructureAdapter
from jarvis_infrastructure.configuration import ConfigurationLoader, ConfigurationSource
from jarvis_infrastructure.kernel import InfrastructureKernel
from jarvis_infrastructure.metadata import AdapterMetadata, AdapterStatus


class InlineSource(ConfigurationSource):
    def __init__(self, payload: Mapping[str, object]) -> None:
        self._payload = payload

    def load(self, profile: str | None = None) -> Mapping[str, object]:
        _ = profile
        return self._payload


class RecordingAdapter(BaseInfrastructureAdapter):
    def __init__(
        self, *, identifier: str, order: list[str], dependencies: tuple[str, ...] = ()
    ) -> None:
        super().__init__(
            metadata=AdapterMetadata(
                identifier=identifier,
                version="1.0.0",
                provider="test",
                capabilities=("test",),
                configuration_profile="test",
                compatibility=("test:v1",),
            ),
            dependencies=dependencies,
        )
        self._order = order

    async def start(self) -> None:
        self._order.append(self.adapter_metadata.identifier)
        await super().start()


def test_kernel_starts_adapters_in_dependency_order() -> None:
    async def _run() -> None:
        order: list[str] = []
        adapter_a = RecordingAdapter(identifier="a", order=order)
        adapter_b = RecordingAdapter(identifier="b", order=order, dependencies=("a",))

        kernel = InfrastructureKernel()
        kernel.register(adapter_b)
        kernel.register(adapter_a)

        source = InlineSource(
            {
                "profile": "test",
                "adapters": {
                    "a": {"provider": "test"},
                    "b": {"provider": "test", "dependencies": ["a"]},
                },
            }
        )
        kernel.load_configuration(ConfigurationLoader((source,)))

        await kernel.start()

        assert order == ["a", "b"]
        metadata = kernel.metadata_snapshot()
        assert metadata["a"].status == AdapterStatus.RUNNING
        assert metadata["b"].status == AdapterStatus.RUNNING

        await kernel.stop()
        metadata = kernel.metadata_snapshot()
        assert metadata["a"].status == AdapterStatus.STOPPED
        assert metadata["b"].status == AdapterStatus.STOPPED

    asyncio.run(_run())


def test_kernel_detects_unknown_dependencies() -> None:
    async def _run() -> None:
        kernel = InfrastructureKernel()
        kernel.register(RecordingAdapter(identifier="a", order=[], dependencies=("missing",)))
        source = InlineSource(
            {"adapters": {"a": {"provider": "test", "dependencies": ["missing"]}}}
        )
        kernel.load_configuration(ConfigurationLoader((source,)))

        with pytest.raises(ValueError):
            await kernel.start()

    asyncio.run(_run())


def test_kernel_detects_circular_dependencies() -> None:
    async def _run() -> None:
        kernel = InfrastructureKernel()
        kernel.register(RecordingAdapter(identifier="a", order=[], dependencies=("b",)))
        kernel.register(RecordingAdapter(identifier="b", order=[], dependencies=("a",)))
        source = InlineSource(
            {
                "adapters": {
                    "a": {"provider": "test", "dependencies": ["b"]},
                    "b": {"provider": "test", "dependencies": ["a"]},
                }
            }
        )
        kernel.load_configuration(ConfigurationLoader((source,)))

        with pytest.raises(ValueError):
            await kernel.start()

    asyncio.run(_run())
