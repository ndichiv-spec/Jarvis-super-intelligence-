"""Shutdown — graceful reverse-order shutdown with signal handling."""

from __future__ import annotations

import logging
import signal
import sys
from types import FrameType
from typing import TYPE_CHECKING

from app.kernel import AppKernel
from app.lifecycle import LifecycleState

if TYPE_CHECKING:
    from app.process_manager import ProcessManager


def run_shutdown(kernel: AppKernel, process_manager: ProcessManager | None = None) -> None:
    logger = logging.getLogger("shutdown")
    logger.info("Shutdown requested")

    if process_manager is not None:
        logger.info("Stopping child processes...")
        process_manager.stop_all()

    kernel.lifecycle.transition(LifecycleState.stopping, "Shutdown requested")
    shutdown_order = list(reversed(kernel.registry.resolve_startup_order()))
    for svc_id in shutdown_order:
        svc = kernel.registry.get(svc_id)
        if svc is None:
            continue
        logger.info("  Stopping %s (%s)...", svc.name, svc_id)
    kernel.lifecycle.transition(LifecycleState.stopped, "Platform stopped")
    logger.info("Platform shutdown complete")


_shutdown_hook = None


def _signal_handler(sig: int, frame: FrameType | None) -> None:
    global _shutdown_hook
    logging.getLogger("shutdown").info("Received signal %s", signal.Signals(sig).name)
    if _shutdown_hook:
        _shutdown_hook()


def install_signal_handlers(kernel: AppKernel, process_manager: ProcessManager | None = None) -> None:
    global _shutdown_hook

    def hook() -> None:
        run_shutdown(kernel, process_manager)
        sys.exit(0)

    _shutdown_hook = hook
    signal.signal(signal.SIGINT, _signal_handler)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, _signal_handler)
