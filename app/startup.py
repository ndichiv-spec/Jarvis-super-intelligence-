"""Startup — orchestrates the bootstrap sequence with dependency ordering."""

from __future__ import annotations

import time

from app.configuration import ConfigurationLoader
from app.environment import EnvironmentValidator
from app.health import HealthStatus
from app.kernel import AppKernel
from app.log import configure_logging, get_logger
from app.registry import ServiceStatus


class StartupError(Exception):
    pass


def run_startup(config_path: str = "") -> AppKernel:
    logger = get_logger("startup")
    configure_logging()
    t0 = time.perf_counter()

    logger.info("Loading configuration...")
    loader = ConfigurationLoader(config_path or None)
    config = loader.resolve()
    issues = loader.validate()
    if issues:
        for i in issues:
            logger.warning("Config issue: %s", i)
    configure_logging(level=config.log_level, log_file=config.log_file)
    logger.info("Configuration loaded (profile=%s)", config.profile)

    logger.info("Validating environment...")
    validator = EnvironmentValidator(config)
    checks = validator.validate_all()
    critical = [c for c in checks if c.severity == "critical" and c.status == "error"]
    if critical:
        for c in critical:
            logger.error("Environment: %s - %s", c.name, c.message)
        raise StartupError(f"Environment validation failed: {', '.join(c.name for c in critical)}")
    for c in checks:
        if c.status == "error":
            logger.warning("Environment: %s - %s", c.name, c.message)
        elif c.status == "warning":
            logger.warning("Environment: %s - %s", c.name, c.message)

    logger.info("Initializing kernel...")
    kernel = AppKernel(config)
    kernel.initialize()
    logger.info("Kernel initialized with %d services", kernel.registry.count())

    logger.info("Starting platform services...")
    startup_order = kernel.registry.resolve_startup_order()
    for svc_id in startup_order:
        svc = kernel.registry.get(svc_id)
        if svc is None:
            continue
        kernel.registry.update_status(svc_id, ServiceStatus.running)
        kernel.health.report(svc_id, HealthStatus.ready, f"{svc.name} started")
        logger.info("  [OK] %s (%s)", svc.name, svc_id)

    failed = [s for s in kernel.registry.list() if s.status == ServiceStatus.failed]
    if failed:
        kernel.mark_degraded(reason=f"{len(failed)} service(s) failed")
        logger.warning("Platform degraded: %d service(s) failed", len(failed))

    logger.info("Platform services started")
    return kernel
