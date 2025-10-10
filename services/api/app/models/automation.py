"""SQLAlchemy models for automation rules and execution history."""

from datetime import datetime
from typing import Any, Dict

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    JSON,
    Time,
)
from sqlalchemy.orm import relationship

from ..database import Base


class AutomationRule(Base):
    """Model representing an automation rule with cron schedule and IF/THEN logic."""

    __tablename__ = "automation_rules"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    cron_expression = Column(String(120), nullable=False)
    timezone = Column(String(60), default="Europe/Bucharest", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    trigger_type = Column(String(50), default="time", nullable=False)
    condition_logic = Column(JSON, default=list)
    action_config = Column(JSON, default=list)
    last_run_at = Column(DateTime(timezone=True), nullable=True)
    next_run_at = Column(DateTime(timezone=True), nullable=True)
    retry_count = Column(Integer, default=0, nullable=False)
    max_retries = Column(Integer, default=3, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    conditions = relationship("AutomationCondition", back_populates="rule", cascade="all, delete-orphan")
    actions = relationship("AutomationAction", back_populates="rule", cascade="all, delete-orphan")
    runs = relationship("AutomationRunHistory", back_populates="rule", cascade="all, delete-orphan")

    def as_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "cron_expression": self.cron_expression,
            "timezone": self.timezone,
            "is_active": self.is_active,
            "trigger_type": self.trigger_type,
            "condition_logic": self.condition_logic or [],
            "action_config": self.action_config or [],
            "last_run_at": self.last_run_at.isoformat() if self.last_run_at else None,
            "next_run_at": self.next_run_at.isoformat() if self.next_run_at else None,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "conditions": [condition.as_dict() for condition in self.conditions],
            "actions": [action.as_dict() for action in self.actions],
        }


class AutomationCondition(Base):
    """IF condition associated with an automation rule."""

    __tablename__ = "automation_conditions"

    id = Column(Integer, primary_key=True, index=True)
    rule_id = Column(Integer, ForeignKey("automation_rules.id", ondelete="CASCADE"), nullable=False)
    field = Column(String(120), nullable=False)
    operator = Column(String(30), nullable=False)
    target_value = Column(Text, nullable=True)
    value_type = Column(String(30), default="string", nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    rule = relationship("AutomationRule", back_populates="conditions")

    def as_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "rule_id": self.rule_id,
            "field": self.field,
            "operator": self.operator,
            "target_value": self.target_value,
            "value_type": self.value_type,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class AutomationAction(Base):
    """THEN action associated with an automation rule."""

    __tablename__ = "automation_actions"

    id = Column(Integer, primary_key=True, index=True)
    rule_id = Column(Integer, ForeignKey("automation_rules.id", ondelete="CASCADE"), nullable=False)
    action_type = Column(String(60), nullable=False)
    action_payload = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    rule = relationship("AutomationRule", back_populates="actions")

    def as_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "rule_id": self.rule_id,
            "action_type": self.action_type,
            "action_payload": self.action_payload or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class AutomationRunHistory(Base):
    """History of automation rule executions."""

    __tablename__ = "automation_run_history"

    id = Column(Integer, primary_key=True, index=True)
    rule_id = Column(Integer, ForeignKey("automation_rules.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(30), nullable=False)
    trigger_payload = Column(JSON, default=dict)
    result_payload = Column(JSON, default=dict)
    error_message = Column(Text, nullable=True)
    attempt = Column(Integer, default=1, nullable=False)
    started_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    triggered_by = Column(String(60), default="system", nullable=False)

    rule = relationship("AutomationRule", back_populates="runs")

    def as_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "rule_id": self.rule_id,
            "status": self.status,
            "trigger_payload": self.trigger_payload or {},
            "result_payload": self.result_payload or {},
            "error_message": self.error_message,
            "attempt": self.attempt,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
            "triggered_by": self.triggered_by,
        }


class NotificationPreference(Base):
    """User notification channel preferences."""

    __tablename__ = "notification_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(64), nullable=False, index=True)
    channel = Column(String(20), nullable=False)
    destination = Column(String(255), nullable=True)
    enabled = Column(Boolean, default=True, nullable=False)
    quiet_hours_start = Column(Time(timezone=False), nullable=True)
    quiet_hours_end = Column(Time(timezone=False), nullable=True)
    preferences = Column(JSON, default=dict)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "channel": self.channel,
            "destination": self.destination,
            "enabled": self.enabled,
            "quiet_hours_start": self.quiet_hours_start.isoformat() if self.quiet_hours_start else None,
            "quiet_hours_end": self.quiet_hours_end.isoformat() if self.quiet_hours_end else None,
            "preferences": self.preferences or {},
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

