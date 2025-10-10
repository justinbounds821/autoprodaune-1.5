"""Automation service that manages cron based IF/THEN rules."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional

from sqlalchemy.orm import Session

try:
    from croniter import croniter
except ImportError:  # pragma: no cover - optional dependency
    croniter = None

from ..models.automation import (
    AutomationAction,
    AutomationCondition,
    AutomationRule,
    AutomationRunHistory,
)
from ..schemas.automation import AutomationRuleCreate, AutomationRuleUpdate
from .monitoring import get_monitoring_service
from .notifications import NotificationService

logger = logging.getLogger(__name__)


class AutomationService:
    """Service wrapper around the automation SQLAlchemy models."""

    def __init__(self, db: Session):
        self.db = db
        self.monitoring = get_monitoring_service()
        self.notification_service = NotificationService(db)

    # ------------------------------------------------------------------
    # Rule management helpers
    # ------------------------------------------------------------------
    def list_rules(self) -> List[Dict[str, Any]]:
        rules = self.db.query(AutomationRule).order_by(AutomationRule.id.desc()).all()
        return [rule.as_dict() for rule in rules]

    def get_rule(self, rule_id: int) -> Optional[AutomationRule]:
        return self.db.query(AutomationRule).filter(AutomationRule.id == rule_id).first()

    def create_rule(self, payload: AutomationRuleCreate) -> Dict[str, Any]:
        self._validate_cron(payload.cron_expression)
        rule = AutomationRule(
            name=payload.name,
            description=payload.description,
            cron_expression=payload.cron_expression,
            timezone=payload.timezone,
            is_active=payload.is_active,
            trigger_type=payload.trigger_type,
            max_retries=payload.max_retries,
            condition_logic=[condition.dict() for condition in payload.conditions],
            action_config=[action.dict() for action in payload.actions],
        )

        self.db.add(rule)
        self.db.flush()

        for condition in payload.conditions:
            self.db.add(
                AutomationCondition(
                    rule_id=rule.id,
                    field=condition.field,
                    operator=condition.operator,
                    target_value=condition.target_value,
                    value_type=condition.value_type,
                )
            )

        for action in payload.actions:
            self.db.add(
                AutomationAction(
                    rule_id=rule.id,
                    action_type=action.action_type,
                    action_payload=action.action_payload,
                )
            )

        rule.next_run_at = self._calculate_next_run(rule.cron_expression, rule.timezone)
        self.db.commit()
        self.db.refresh(rule)

        logger.info("Automation rule created", extra={"rule_id": rule.id})
        return rule.as_dict()

    def update_rule(self, rule_id: int, payload: AutomationRuleUpdate) -> Dict[str, Any]:
        rule = self.get_rule(rule_id)
        if not rule:
            raise ValueError("Regula specificată nu există")

        self._validate_cron(payload.cron_expression)

        rule.name = payload.name
        rule.description = payload.description
        rule.cron_expression = payload.cron_expression
        rule.timezone = payload.timezone
        rule.is_active = payload.is_active
        rule.trigger_type = payload.trigger_type
        rule.max_retries = payload.max_retries
        rule.condition_logic = [condition.dict() for condition in payload.conditions]
        rule.action_config = [action.dict() for action in payload.actions]
        rule.next_run_at = self._calculate_next_run(rule.cron_expression, rule.timezone)
        rule.updated_at = datetime.now(timezone.utc)

        rule.conditions.clear()
        for condition in payload.conditions:
            rule.conditions.append(
                AutomationCondition(
                    field=condition.field,
                    operator=condition.operator,
                    target_value=condition.target_value,
                    value_type=condition.value_type,
                )
            )

        rule.actions.clear()
        for action in payload.actions:
            rule.actions.append(
                AutomationAction(
                    action_type=action.action_type,
                    action_payload=action.action_payload,
                )
            )

        self.db.commit()
        self.db.refresh(rule)

        logger.info("Automation rule updated", extra={"rule_id": rule.id})
        return rule.as_dict()

    def delete_rule(self, rule_id: int) -> None:
        rule = self.get_rule(rule_id)
        if not rule:
            raise ValueError("Regula specificată nu există")
        self.db.delete(rule)
        self.db.commit()
        logger.info("Automation rule deleted", extra={"rule_id": rule_id})

    # ------------------------------------------------------------------
    # Execution helpers
    # ------------------------------------------------------------------
    async def trigger_rule_async(
        self, rule_id: int, trigger_payload: Optional[Dict[str, Any]] = None, triggered_by: str = "manual"
    ) -> Dict[str, Any]:
        rule = self.get_rule(rule_id)
        if not rule:
            raise ValueError("Regula specificată nu există")
        return await self._execute_rule(rule, trigger_payload or {}, triggered_by)

    async def trigger_scheduled_rules(self) -> List[Dict[str, Any]]:
        now = datetime.now(timezone.utc)
        rules = (
            self.db.query(AutomationRule)
            .filter(AutomationRule.is_active.is_(True))
            .filter(AutomationRule.next_run_at != None)  # noqa: E711
            .filter(AutomationRule.next_run_at <= now)
            .all()
        )

        results: List[Dict[str, Any]] = []
        for rule in rules:
            results.append(await self._execute_rule(rule, {"trigger": "cron"}, "scheduler"))
            rule.next_run_at = self._calculate_next_run(rule.cron_expression, rule.timezone)
        self.db.commit()
        return results

    async def _execute_rule(
        self, rule: AutomationRule, trigger_payload: Dict[str, Any], triggered_by: str
    ) -> Dict[str, Any]:
        run = AutomationRunHistory(
            rule_id=rule.id,
            status="running",
            trigger_payload=trigger_payload,
            triggered_by=triggered_by,
            attempt=rule.retry_count + 1,
            started_at=datetime.now(timezone.utc),
        )
        self.db.add(run)
        self.db.commit()
        self.db.refresh(run)

        try:
            if not self._evaluate_conditions(rule.conditions, trigger_payload):
                run.status = "skipped"
                run.finished_at = datetime.now(timezone.utc)
                self.db.commit()
                return run.as_dict()

            action_results = await self._execute_actions(rule.actions, trigger_payload)

            run.status = "success"
            run.result_payload = {"actions": action_results}
            run.finished_at = datetime.now(timezone.utc)
            rule.last_run_at = run.finished_at
            rule.retry_count = 0
            self.monitoring.record_custom_metric("automation_success", 1)
            logger.info("Automation rule executed", extra={"rule_id": rule.id})
        except Exception as exc:  # pragma: no cover - runtime errors
            rule.retry_count += 1
            run.status = "failed"
            run.error_message = str(exc)
            run.finished_at = datetime.now(timezone.utc)
            self.monitoring.record_custom_metric("automation_failure", 1)
            logger.exception("Automation rule execution failed", extra={"rule_id": rule.id})

            if rule.retry_count <= rule.max_retries:
                delay_seconds = min(60 * rule.retry_count, 300)
                run.result_payload = {"retry": True, "delay_seconds": delay_seconds}
                asyncio.create_task(self._retry_rule(rule.id, delay_seconds))
            else:
                self.notification_service.notify_admins(
                    title="Regula de automatizare a eșuat",
                    message=f"Regula '{rule.name}' a depășit numărul maxim de retry.",
                )
        finally:
            self.db.commit()
            self.db.refresh(run)
            self.db.refresh(rule)

        return run.as_dict()

    async def _retry_rule(self, rule_id: int, delay_seconds: int) -> None:
        await asyncio.sleep(delay_seconds)
        try:
            rule = self.get_rule(rule_id)
            if rule and rule.retry_count <= rule.max_retries:
                await self._execute_rule(rule, {"trigger": "retry"}, "retry")
        except Exception:  # pragma: no cover - defensive
            logger.exception("Retry execution failed", extra={"rule_id": rule_id})

    async def _execute_actions(
        self, actions: Iterable[AutomationAction], trigger_payload: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        results = []
        for action in actions:
            if action.action_type == "send_email":
                await self.notification_service.send_email_async(action.action_payload)
                results.append({"action": "send_email", "status": "queued"})
            elif action.action_type == "send_sms":
                await self.notification_service.send_sms_async(action.action_payload)
                results.append({"action": "send_sms", "status": "queued"})
            elif action.action_type == "trigger_video_generation":
                # integrate with video generator queue if available
                from .video_generator import VideoGenerator

                generator = VideoGenerator()
                await asyncio.get_event_loop().run_in_executor(
                    None,
                    generator.generate_video,
                    action.action_payload.get("template", "default"),
                    action.action_payload.get("context", {}),
                )
                results.append({"action": "trigger_video_generation", "status": "completed"})
            else:
                logger.warning("Unsupported automation action", extra={"type": action.action_type})
                results.append({"action": action.action_type, "status": "ignored"})
        return results

    def _evaluate_conditions(
        self, conditions: Iterable[AutomationCondition], trigger_payload: Dict[str, Any]
    ) -> bool:
        if not conditions:
            return True

        for condition in conditions:
            payload_value = trigger_payload.get(condition.field)
            if not self._compare(payload_value, condition.operator, condition.target_value, condition.value_type):
                return False
        return True

    @staticmethod
    def _compare(value: Any, operator: str, target_value: Optional[str], value_type: str) -> bool:
        if value_type in {"int", "integer"}:
            try:
                value = int(value) if value is not None else None
                target = int(target_value) if target_value is not None else None
            except (TypeError, ValueError):
                return False
        elif value_type in {"float", "number"}:
            try:
                value = float(value) if value is not None else None
                target = float(target_value) if target_value is not None else None
            except (TypeError, ValueError):
                return False
        else:
            target = target_value

        if operator == "equals":
            return value == target
        if operator == "not_equals":
            return value != target
        if operator == "contains":
            return target in value if isinstance(value, str) and target is not None else False
        if operator == "greater_than":
            return value is not None and target is not None and value > target
        if operator == "less_than":
            return value is not None and target is not None and value < target
        return False

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------
    def _calculate_next_run(self, cron_expression: str, tz: str) -> Optional[datetime]:
        if croniter:
            try:
                now = datetime.now(timezone.utc)
                iterator = croniter(cron_expression, now)
                return iterator.get_next(datetime)
            except Exception:  # pragma: no cover - croniter runtime errors
                logger.warning("Nu s-a putut calcula următoarea rulare pentru cron", extra={"cron": cron_expression})
        return None

    @staticmethod
    def _validate_cron(cron_expression: str) -> None:
        parts = cron_expression.split()
        if len(parts) != 5:
            raise ValueError("Expresia cron trebuie să aibă 5 segmente (minut, oră, zi, lună, zi săptămână)")
        allowed = set("0123456789*/,-")
        for part in parts:
            if not part:
                raise ValueError("Expresia cron nu poate conține segmente goale")
            if any(ch not in allowed for ch in part):
                raise ValueError(f"Segmentul '{part}' conține caractere invalide")

    def list_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        history = (
            self.db.query(AutomationRunHistory)
            .order_by(AutomationRunHistory.started_at.desc())
            .limit(limit)
            .all()
        )
        return [item.as_dict() for item in history]

    def record_manual_run(self, rule_id: int, status: str, message: Optional[str] = None) -> Dict[str, Any]:
        run = AutomationRunHistory(
            rule_id=rule_id,
            status=status,
            error_message=message,
            started_at=datetime.now(timezone.utc),
            finished_at=datetime.now(timezone.utc),
            triggered_by="manual",
        )
        self.db.add(run)
        self.db.commit()
        self.db.refresh(run)
        return run.as_dict()


__all__ = ["AutomationService"]

