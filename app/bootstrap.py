"""Bootstrap — top-level entry point that wires configuration, startup, and shutdown."""

from __future__ import annotations

from typing import TYPE_CHECKING

from app.log import configure_logging, get_logger
from app.shutdown import install_signal_handlers, run_shutdown
from app.startup import run_startup

if TYPE_CHECKING:
    from app.process_manager import ProcessManager


def bootstrap(config_path: str = "") -> BootstrapContext:
    configure_logging()
    logger = get_logger("bootstrap")
    logger.info("JARVIS Platform 2.0 booting...")
    kernel = run_startup(config_path)
    install_signal_handlers(kernel)
    return BootstrapContext(kernel)


class BootstrapContext:
    def __init__(self, kernel: AppKernel) -> None:
        self._kernel = kernel

    @property
    def kernel(self) -> AppKernel:
        return self._kernel

    def shutdown(self, process_manager: ProcessManager | None = None) -> None:
        run_shutdown(self._kernel, process_manager)
