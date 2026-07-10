"""HEALTH command — show consolidated health report."""

from __future__ import annotations

import argparse

from app.runtime import Runtime


def cmd_health(args: argparse.Namespace, runtime: Runtime) -> int:
    report = runtime.health()
    print(f"Platform: {report['platform']}")
    if report.get("summary"):
        print(f"Summary: {report['summary']}")
    print()
    for c in report.get("checks", []):
        sym = "[OK]" if c["status"] == "ready" else ("[FAIL]" if c["status"] == "error" else "[?]")
        print(f"  {sym} {c['subsystem']}: {c['status']} - {c['message']}")
    if report.get("process_checks"):
        print()
        print("Application Processes:")
        for c in report["process_checks"]:
            sym = "[OK]" if c["status"] == "ready" else ("[FAIL]" if c["status"] == "error" else "[?]")
            print(f"  {sym} {c['subsystem']}: {c['status']} - {c['message']}")
    print()
    if report.get("processes"):
        print("Process Details:")
        for pid, info in report["processes"].items():
            alive = "Running" if info.get("alive") else "Stopped"
            healthy = "Healthy" if info.get("healthy") else "Unhealthy"
            print(f"  {pid}: PID={info.get('pid', 'N/A')} Port={info.get('port', 'N/A')} {alive} {healthy} Uptime={info.get('uptime', 'N/A')}")
    return 0 if report["platform"] in ("ready", "degraded") else 1
