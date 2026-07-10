"""Banner — professional startup display that adapts to available components."""

from __future__ import annotations

from typing import Any

from app.kernel import AppKernel
from app.lifecycle import LifecycleState
from app.registry import ServiceStatus


def print_banner(
    kernel: AppKernel,
    elapsed: float = 0.0,
    process_health: dict[str, dict[str, Any]] | None = None,
) -> None:
    config = kernel.config
    lifecycle = kernel.lifecycle
    registry = kernel.registry
    state = kernel.state
    ph = process_health or {}
    width = 76
    sep = "=" * width
    dash = "-" * width
    print()
    print(sep)
    print("  JARVIS AI PLATFORM")
    print(f"  Version {state.version}")
    print(sep)
    print()
    print("  Loading Configuration...")
    result = "OK" if config is not None else "FAILED"
    print(f"  [{result}]")
    print()
    print("  Initializing Kernel...")
    kernel_status = "Ready" if lifecycle.state in (LifecycleState.ready, LifecycleState.starting, LifecycleState.initializing) else "Failed"
    print(f"  {kernel_status}")
    print()
    services = registry.list()
    for svc in services:
        status_sym = "[OK]" if svc.status in (ServiceStatus.running, ServiceStatus.registered) else "[FAIL]"
        print(f"  Loading {svc.name}...")
        print(f"  {status_sym} {svc.id}")
    print()

    has_process_health = bool(process_health)

    if lifecycle.state == LifecycleState.ready:
        if has_process_health and (not ph.get("gateway", {}).get("healthy", False) or not ph.get("home", {}).get("healthy", False)):
            failed_components = [k for k, v in ph.items() if not v.get("healthy")]
            print(dash)
            print("  JARVIS STARTUP INCOMPLETE")
            for comp in failed_components:
                print(f"  {comp} failed to start")
            print()
        else:
            print(sep)
            print("  JARVIS READY")
            if has_process_health:
                print()
                print("  Gateway:")
                print(f"  http://localhost:{config.gateway_port}")
                print()
                print("  Home:")
                print(f"  {config.home_url}")
            print()
    elif lifecycle.state == LifecycleState.degraded:
        print(dash)
        print("  JARVIS DEGRADED")
        print()
    elif lifecycle.state == LifecycleState.failed:
        print(dash)
        print("  JARVIS FAILED")
        print()
    else:
        if lifecycle.state == LifecycleState.ready and not gateway_ok:
            print(dash)
            print("  JARVIS STARTUP INCOMPLETE")
            print("  Gateway failed to start")
            print()
        elif lifecycle.state == LifecycleState.ready and not home_ok:
            print(dash)
            print("  JARVIS STARTUP INCOMPLETE")
            print("  Home failed to start")
            print()

    gateway_pid = ph.get("gateway", {}).get("pid")
    home_pid = ph.get("home", {}).get("pid")
    pid_info = ""
    if gateway_pid:
        pid_info += f"Gateway PID {gateway_pid}"
    if home_pid:
        if pid_info:
            pid_info += " | "
        pid_info += f"Home PID {home_pid}"
    if pid_info:
        print(f"  {len(services)} services  |  {pid_info}  |  {elapsed:.2f}s")
    else:
        print(f"  {len(services)} services  |  {elapsed:.2f}s")
    print(sep)
    print()
