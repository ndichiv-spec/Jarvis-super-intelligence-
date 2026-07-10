"""DOCTOR command — comprehensive environment and platform diagnostics."""

from __future__ import annotations

import argparse

from app.runtime import Runtime


def cmd_doctor(args: argparse.Namespace, runtime: Runtime) -> int:
    print("JARVIS Platform Diagnostics")
    print("=" * 60)
    if runtime.kernel is None:
        print("Platform is not running")
        return 0
    report = runtime.diagnostics()
    health = runtime.health()
    status = runtime.status()
    print(f"Python: {report.python_info.get('version', '?')}")
    print(f"System: {report.platform_info.get('system', '?')} {report.platform_info.get('release', '?')}")
    print(f"Machine: {report.platform_info.get('machine', '?')}")
    print(f"Profile: {report.config_summary.get('profile', '?')}")
    print(f"Debug: {report.config_summary.get('debug', False)}")
    print(f"Gateway: {report.config_summary.get('gateway_host', '?')}:{report.config_summary.get('gateway_port', '?')}")
    print(f"Lifecycle: {report.lifecycle.get('state', '?')}")
    print(f"Services: {len(report.services)}")
    for svc in report.services:
        sym = "[OK]" if svc["status"] == "running" else ("[FAIL]" if svc["status"] == "failed" else "[?]")
        print(f"  {sym} {svc['name']} ({svc['id']}) -- {svc['status']}")
    print(f"Health: {report.health.get('platform', '?')}")
    for c in report.health.get("checks", []):
        sym = "[OK]" if c["status"] == "ready" else ("[FAIL]" if c["status"] == "error" else "[?]")
        print(f"  {sym} {c['subsystem']}: {c['message']}")
    if status.get("processes"):
        print()
        print("Application Processes:")
        for pid, info in status["processes"].items():
            alive_sym = "[OK]" if info.get("alive") else "[STOPPED]"
            healthy_sym = "[OK]" if info.get("healthy") else "[UNHEALTHY]"
            print(f"  {alive_sym} {pid}: PID={info.get('pid', 'N/A')} Port={info.get('port', 'N/A')} {healthy_sym} Uptime={info.get('uptime', 'N/A')}")
    if report.warnings:
        print()
        print("Warnings:")
        for w in report.warnings:
            print(f"  [WARN] {w}")
    return 0
