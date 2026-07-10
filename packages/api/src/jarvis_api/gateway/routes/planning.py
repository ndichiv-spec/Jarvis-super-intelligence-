from __future__ import annotations

from fastapi import APIRouter, HTTPException

from jarvis_planning.planner import Planner

router = APIRouter(prefix="/planning", tags=["planning"])

_planner = Planner()


@router.post("/create")
async def create_plan(body: dict):
    objective = body.get("objective", "")
    if not objective:
        raise HTTPException(status_code=400, detail="Objective is required")
    templates = body.get("templates")
    plan = _planner.full_plan(objective, templates)
    return {"plan_id": plan.id, "objective": plan.objective, "status": plan.status,
            "goal": plan.goal.to_dict() if plan.goal else None,
            "tasks": [t.to_dict() for t in plan.tasks],
            "graph": plan.graph.to_dict() if plan.graph else None}


@router.post("/analyze")
async def analyze_goal(body: dict):
    objective = body.get("objective", "")
    if not objective:
        raise HTTPException(status_code=400, detail="Objective is required")
    plan = _planner.create_plan(objective)
    plan = _planner.analyze(plan.id)
    return {"plan_id": plan.id, "goal": plan.goal.to_dict() if plan.goal else None,
            "validation": plan.validation.to_dict() if plan.validation else None}


@router.post("/decompose")
async def decompose_goal(body: dict):
    objective = body.get("objective", "")
    if not objective:
        raise HTTPException(status_code=400, detail="Objective is required")
    templates = body.get("templates")
    plan = _planner.create_plan(objective)
    plan = _planner.decompose(plan.id, templates)
    return {"plan_id": plan.id, "tasks": [t.to_dict() for t in plan.tasks],
            "graph": plan.graph.to_dict() if plan.graph else None}


@router.post("/execute")
async def execute_plan(body: dict):
    plan_id = body.get("plan_id", "")
    if not plan_id:
        raise HTTPException(status_code=400, detail="plan_id is required")
    plan = _planner.get_plan(plan_id)
    if plan is None:
        raise HTTPException(status_code=404, detail="Plan not found")
    if plan.status not in ("validated", "executing", "replanned"):
        if plan.graph is None:
            raise HTTPException(status_code=400, detail="Plan not ready for execution. Call /planning/create first.")
    plan = _planner.prepare_execution(plan_id)
    plan = _planner.execute_all(plan_id)
    return {"plan_id": plan.id, "status": plan.status,
            "results": {tid: r.to_dict() for tid, r in _planner._executors.get(plan_id, {}).get_all_results().items()}
            if _planner._executors.get(plan_id) else {}}


@router.post("/replan")
async def replan_plan(body: dict):
    plan_id = body.get("plan_id", "")
    reason = body.get("reason", "manual")
    if not plan_id:
        raise HTTPException(status_code=400, detail="plan_id is required")
    context = body.get("context")
    result = _planner.replan(plan_id, reason, context)
    return {"plan_id": plan_id, "replan_result": result.to_dict()}


@router.get("/{plan_id}")
async def get_plan(plan_id: str):
    plan = _planner.get_plan(plan_id)
    if plan is None:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan.to_dict()


@router.get("/{plan_id}/graph")
async def get_plan_graph(plan_id: str):
    plan = _planner.get_plan(plan_id)
    if plan is None:
        raise HTTPException(status_code=404, detail="Plan not found")
    if plan.graph is None:
        raise HTTPException(status_code=400, detail="Plan has no graph. Decompose first.")
    return plan.graph.to_dict()


@router.get("/{plan_id}/status")
async def get_plan_status(plan_id: str):
    plan = _planner.get_plan(plan_id)
    if plan is None:
        raise HTTPException(status_code=404, detail="Plan not found")
    progress = _planner.get_progress(plan_id)
    explanation = _planner.get_explanation(plan_id)
    result = plan.to_dict()
    if progress:
        result["progress"] = progress.to_dict()
    result["explanation"] = explanation.to_dict()
    return result


@router.get("/")
async def list_plans():
    return {"plans": _planner.list_plans()}
