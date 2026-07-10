from __future__ import annotations

from fastapi import APIRouter, HTTPException

from jarvis_intelligence import (
    IntelligenceEngine,
    GoalPriority,
    ExecutionPolicy,
)
from jarvis_intelligence.context import ExecutionContext

router = APIRouter(prefix="/intelligence", tags=["intelligence"])

_engine: IntelligenceEngine | None = None


def _get_engine() -> IntelligenceEngine:
    global _engine
    if _engine is None:
        _engine = IntelligenceEngine()
    return _engine


def _ok(data: object) -> dict:
    return {"ok": True, "data": data, "error": None, "metadata": {}}


def _error(status: int, message: str) -> HTTPException:
    return HTTPException(status_code=status, detail=message)


@router.get("/status")
async def get_status():
    engine = _get_engine()
    return _ok(engine.get_status())


@router.get("/context")
async def get_context():
    engine = _get_engine()
    ctx_manager = engine.context_manager
    contexts = []
    for key, ctx in ctx_manager._contexts.items():
        contexts.append({
            "id": key,
            "goal_id": ctx.goal_id,
            "plan_id": ctx.plan_id,
            "session_id": ctx.session_id,
            "user_id": ctx.user_id,
            "workspace_id": ctx.workspace_id,
            "reasoning_steps": len(ctx.reasoning_history),
            "memory_references": ctx.memory_references,
            "knowledge_references": ctx.knowledge_references,
            "execution_events": len(ctx.execution_history),
            "active_goals": ctx.active_goals,
            "created_at": ctx.created_at.isoformat(),
        })
    return _ok({"contexts": contexts, "total": len(contexts)})


@router.get("/goals")
async def list_goals():
    engine = _get_engine()
    goals = engine.goal_manager.list()
    return _ok([
        {
            "id": g.id,
            "description": g.description,
            "priority": g.priority.value,
            "state": g.state.value,
            "success_criteria": list(g.success_criteria),
            "dependencies": list(g.dependencies),
            "deadline": g.deadline.isoformat() if g.deadline else None,
            "created_at": g.created_at.isoformat(),
            "updated_at": g.updated_at.isoformat(),
        }
        for g in goals
    ])


@router.post("/goals")
async def create_goal(body: dict):
    description = body.get("description", "")
    if not description:
        raise _error(400, "description is required")
    priority_str = body.get("priority", "medium")
    try:
        priority = GoalPriority(priority_str)
    except ValueError:
        raise _error(400, f"Invalid priority: {priority_str}")
    engine = _get_engine()
    plan = engine.planner.create_plan(description, priority=priority)
    return _ok({
        "goal_id": plan.goal.id,
        "plan_id": plan.id,
        "description": plan.goal.description,
        "priority": plan.goal.priority.value,
        "state": plan.goal.state.value,
    })


@router.post("/plan")
async def create_plan(body: dict):
    description = body.get("description", "")
    if not description:
        raise _error(400, "description is required")
    priority_str = body.get("priority", "medium")
    policy_str = body.get("policy", "balanced")
    try:
        priority = GoalPriority(priority_str)
    except ValueError:
        raise _error(400, f"Invalid priority: {priority_str}")
    try:
        policy = ExecutionPolicy(policy_str)
    except ValueError:
        raise _error(400, f"Invalid policy: {policy_str}")

    engine = _get_engine()
    plan = engine.planner.create_plan(description, priority=priority)
    plan = engine.planner.decompose_goal(plan.id) or plan
    tasks = plan.task_graph.all()
    return _ok({
        "plan_id": plan.id,
        "goal_id": plan.goal.id,
        "status": plan.status,
        "strategy": plan.strategy.name if plan.strategy else None,
        "tasks": [
            {
                "id": t.id,
                "description": t.description,
                "state": t.state.value,
                "depends_on": list(t.depends_on),
                "required_capabilities": list(t.required_capabilities),
            }
            for t in tasks
        ],
    })


@router.post("/execute")
async def execute_goal(body: dict):
    description = body.get("description", "")
    if not description:
        raise _error(400, "description is required")
    priority_str = body.get("priority", "medium")
    policy_str = body.get("policy", "balanced")
    try:
        priority = GoalPriority(priority_str)
    except ValueError:
        raise _error(400, f"Invalid priority: {priority_str}")
    try:
        policy = ExecutionPolicy(policy_str)
    except ValueError:
        raise _error(400, f"Invalid policy: {policy_str}")

    engine = _get_engine()
    result = await engine.execute_goal(description, priority=priority, policy=policy)
    if not result.success:
        raise _error(502, result.error or "Goal execution failed")
    report = result.coordination
    return _ok({
        "goal_id": result.goal.id,
        "plan_id": result.plan.id if result.plan else None,
        "success": result.success,
        "total_tasks": report.total_tasks if report else 0,
        "completed_tasks": report.completed_tasks if report else 0,
        "failed_tasks": report.failed_tasks if report else 0,
        "duration_seconds": report.duration_seconds if report else 0.0,
        "decisions_made": report.decisions_made if report else 0,
    })


@router.get("/metrics")
async def get_metrics():
    engine = _get_engine()
    metrics = engine.telemetry.get_metrics()
    return _ok({
        "total_executions": metrics.total_executions,
        "successful_executions": metrics.successful_executions,
        "failed_executions": metrics.failed_executions,
        "avg_duration_seconds": metrics.avg_duration_seconds,
        "total_duration_seconds": metrics.total_duration_seconds,
        "decisions_made": metrics.decisions_made,
        "tasks_completed": metrics.tasks_completed,
        "tasks_failed": metrics.tasks_failed,
    })


@router.get("/plans")
async def list_plans():
    engine = _get_engine()
    plans = engine.planner.list_plans()
    return _ok([
        {
            "id": p.id,
            "goal_id": p.goal.id,
            "goal_description": p.goal.description,
            "status": p.status,
            "task_count": len(p.task_graph.all()),
            "created_at": p.created_at.isoformat(),
        }
        for p in plans
    ])


@router.get("/plans/{plan_id}")
async def get_plan(plan_id: str):
    engine = _get_engine()
    plan = engine.planner.get_plan(plan_id)
    if plan is None:
        raise _error(404, f"Plan not found: {plan_id}")
    return _ok({
        "id": plan.id,
        "goal": {
            "id": plan.goal.id,
            "description": plan.goal.description,
            "priority": plan.goal.priority.value,
            "state": plan.goal.state.value,
        },
        "strategy": plan.strategy.name if plan.strategy else None,
        "status": plan.status,
        "tasks": [
            {
                "id": t.id,
                "description": t.description,
                "state": t.state.value,
                "depends_on": list(t.depends_on),
                "required_capabilities": list(t.required_capabilities),
                "priority": t.priority,
                "retry_count": t.retry_count,
                "started_at": t.started_at.isoformat() if t.started_at else None,
                "completed_at": t.completed_at.isoformat() if t.completed_at else None,
            }
            for t in plan.task_graph.all()
        ],
        "created_at": plan.created_at.isoformat(),
    })


@router.get("/policy")
async def get_policy():
    engine = _get_engine()
    config = engine.policy.get_config()
    return _ok({
        "policy": engine.policy.get_current_policy().value,
        "max_concurrent_tasks": config.max_concurrent_tasks,
        "max_retries": config.max_retries,
        "timeout_seconds": config.timeout_seconds,
        "confidence_threshold": config.confidence_threshold,
        "allow_parallel": config.allow_parallel,
        "allow_replanning": config.allow_replanning,
    })


@router.put("/policy")
async def set_policy(body: dict):
    policy_str = body.get("policy", "")
    if not policy_str:
        raise _error(400, "policy is required")
    try:
        policy = ExecutionPolicy(policy_str)
    except ValueError:
        raise _error(400, f"Invalid policy: {policy_str}")
    engine = _get_engine()
    engine.policy.set_policy(policy)
    return _ok({"policy": policy.value})


@router.get("/learning")
async def get_learning():
    engine = _get_engine()
    records = engine.learning.get_all()
    return _ok([
        {
            "id": r.id,
            "pattern": r.pattern,
            "context": r.context,
            "outcome": r.outcome,
            "confidence": r.confidence,
            "applied_count": r.applied_count,
            "timestamp": r.timestamp.isoformat(),
        }
        for r in records
    ])
