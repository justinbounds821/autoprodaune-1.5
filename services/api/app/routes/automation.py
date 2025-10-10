"""Automation routes providing cron editor, IF/THEN rules and execution history."""

from __future__ import annotations

import asyncio
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db, get_session_local
from ..schemas.automation import (
    AutomationHistoryResponse,
    AutomationRuleCreate,
    AutomationRuleResponse,
    AutomationRuleUpdate,
)
from ..services.automation_service import AutomationService

router = APIRouter(prefix="/api/automation", tags=["automation"])


def get_automation_service(db: Session = Depends(get_db)) -> AutomationService:
    return AutomationService(db)


@router.get("/rules", response_model=Dict[str, List[AutomationRuleResponse]])
async def list_rules(service: AutomationService = Depends(get_automation_service)) -> Dict[str, Any]:
    """Return all automation rules with IF/THEN configuration."""
    rules = service.list_rules()
    return {
        "rules": [AutomationRuleResponse.parse_obj(_format_rule(rule)) for rule in rules]
    }


@router.post("/rules", response_model=AutomationRuleResponse, status_code=201)
async def create_rule(
    payload: AutomationRuleCreate, service: AutomationService = Depends(get_automation_service)
) -> AutomationRuleResponse:
    try:
        rule = service.create_rule(payload)
        return AutomationRuleResponse.parse_obj(_format_rule(rule))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.put("/rules/{rule_id}", response_model=AutomationRuleResponse)
async def update_rule(
    rule_id: int,
    payload: AutomationRuleUpdate,
    service: AutomationService = Depends(get_automation_service),
) -> AutomationRuleResponse:
    try:
        rule = service.update_rule(rule_id, payload)
        return AutomationRuleResponse.parse_obj(_format_rule(rule))
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.delete("/rules/{rule_id}", status_code=204)
async def delete_rule(rule_id: int, service: AutomationService = Depends(get_automation_service)) -> None:
    try:
        service.delete_rule(rule_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/rules/{rule_id}/trigger", response_model=AutomationHistoryResponse)
async def trigger_rule(
    rule_id: int,
    trigger_payload: Dict[str, Any] | None = None,
    service: AutomationService = Depends(get_automation_service),
) -> AutomationHistoryResponse:
    rule = service.get_rule(rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Regula nu a fost găsită")

    async def _run_rule():
        session_local = get_session_local()
        db = session_local()
        try:
            background_service = AutomationService(db)
            await background_service.trigger_rule_async(
                rule_id, dict(trigger_payload or {}), "manual"
            )
        finally:
            db.close()

    asyncio.create_task(_run_rule())
    run_log = service.record_manual_run(rule_id, "queued")
    return AutomationHistoryResponse.parse_obj(_format_history(run_log))


@router.post("/run-due", response_model=Dict[str, Any])
async def run_due_rules(
    service: AutomationService = Depends(get_automation_service),
) -> Dict[str, Any]:
    async def _run_due():
        session_local = get_session_local()
        db = session_local()
        try:
            background_service = AutomationService(db)
            await background_service.trigger_scheduled_rules()
        finally:
            db.close()

    asyncio.create_task(_run_due())
    return {"success": True, "message": "Rulele programate au fost trimise către worker"}


@router.get("/history", response_model=Dict[str, List[AutomationHistoryResponse]])
async def get_history(
    limit: int = Query(50, ge=1, le=200), service: AutomationService = Depends(get_automation_service)
) -> Dict[str, Any]:
    history = service.list_history(limit)
    return {
        "history": [AutomationHistoryResponse.parse_obj(_format_history(item)) for item in history]
    }


@router.get("/status", response_model=Dict[str, Any])
async def get_status(service: AutomationService = Depends(get_automation_service)) -> Dict[str, Any]:
    rules = service.list_rules()
    history = service.list_history(limit=10)
    active_rules = [rule for rule in rules if rule.get("is_active")]
    return {
        "totalRules": len(rules),
        "activeRules": len(active_rules),
        "lastRuns": [AutomationHistoryResponse.parse_obj(_format_history(item)) for item in history],
    }


def _format_rule(rule: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": rule["id"],
        "name": rule.get("name"),
        "description": rule.get("description"),
        "cronExpression": rule.get("cron_expression"),
        "timezone": rule.get("timezone"),
        "isActive": rule.get("is_active"),
        "triggerType": rule.get("trigger_type"),
        "conditionLogic": rule.get("condition_logic", []),
        "actionConfig": rule.get("action_config", []),
        "lastRunAt": rule.get("last_run_at"),
        "nextRunAt": rule.get("next_run_at"),
        "retryCount": rule.get("retry_count", 0),
        "maxRetries": rule.get("max_retries", 0),
        "createdAt": rule.get("created_at"),
        "updatedAt": rule.get("updated_at"),
    }


def _format_history(history: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": history["id"],
        "ruleId": history.get("rule_id"),
        "status": history.get("status"),
        "triggerPayload": history.get("trigger_payload", {}),
        "resultPayload": history.get("result_payload", {}),
        "errorMessage": history.get("error_message"),
        "attempt": history.get("attempt"),
        "startedAt": history.get("started_at"),
        "finishedAt": history.get("finished_at"),
        "triggeredBy": history.get("triggered_by"),
    }

