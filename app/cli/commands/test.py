"""TEST command — run quick platform self-test."""

from __future__ import annotations

import argparse

from app.runtime import Runtime


def cmd_test(args: argparse.Namespace, runtime: Runtime) -> int:
    print("Running platform self-test...")
    errors = []
    if runtime.kernel is None:
        print("  ✗ No running kernel")
        return 1
    try:
        registry = runtime.registry
        count = registry.count()
        if count > 0:
            print(f"  ✓ Registry has {count} services")
        else:
            print("  ✗ Registry is empty")
            errors.append("empty registry")
    except Exception as e:
        print(f"  ✗ Registry: {e}")
        errors.append(str(e))
    try:
        order = registry.resolve_startup_order()
        if order:
            print(f"  ✓ Startup order resolved ({len(order)} services)")
        else:
            print("  ✗ No startup order")
            errors.append("no startup order")
    except Exception as e:
        print(f"  ✗ Startup order: {e}")
        errors.append(str(e))
    try:
        graph = registry.get_dependency_graph()
        if graph:
            print(f"  ✓ Dependency graph has {len(graph)} entries")
        else:
            print("  ✗ Dependency graph empty")
            errors.append("empty graph")
    except Exception as e:
        print(f"  ✗ Dependency graph: {e}")
        errors.append(str(e))
    try:
        report = runtime.health()
        if report.get("checks"):
            print(f"  ✓ Health report has {len(report['checks'])} checks")
        else:
            print("  ✗ Health report empty")
            errors.append("empty health report")
    except Exception as e:
        print(f"  ✗ Health: {e}")
        errors.append(str(e))
    try:
        diag = runtime.diagnostics()
        print("  ✓ Diagnostics generated")
    except Exception as e:
        print(f"  ✗ Diagnostics: {e}")
        errors.append(str(e))
    if errors:
        print(f"\n  {len(errors)} failure(s): {', '.join(errors)}")
        return 1
    print("\n  All checks passed")
    return 0
