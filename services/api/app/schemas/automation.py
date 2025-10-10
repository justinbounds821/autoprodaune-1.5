"""Pydantic schemas for automation API."""

from datetime import datetime, time
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator


class AutomationConditionPayload(BaseModel):
    field: str = Field(..., description="Name of the field that will be evaluated")
    operator: str = Field(..., description="Comparison operator", pattern=r"^[a-z_]+$")
    target_value: Optional[str] = Field(None, description="Value used for comparison")
    value_type: str = Field("string", description="Type of value")


class AutomationActionPayload(BaseModel):
    action_type: str = Field(..., description="Type of the action to execute", pattern=r"^[a-z_]+$")
    action_payload: Dict[str, Any] = Field(default_factory=dict)


class AutomationRuleCreate(BaseModel):
    name: str
    description: Optional[str]
    cron_expression: str = Field(..., alias="cronExpression")
    timezone: str = "Europe/Bucharest"
    is_active: bool = Field(True, alias="isActive")
    trigger_type: str = Field("time", alias="triggerType")
    max_retries: int = Field(3, ge=0, le=10, alias="maxRetries")
    conditions: List[AutomationConditionPayload] = Field(default_factory=list)
    actions: List[AutomationActionPayload] = Field(default_factory=list)

    class Config:
        allow_population_by_field_name = True


class AutomationRuleUpdate(AutomationRuleCreate):
    pass


class AutomationRuleResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    cron_expression: str = Field(..., alias="cronExpression")
    timezone: str
    is_active: bool = Field(..., alias="isActive")
    trigger_type: str = Field(..., alias="triggerType")
    condition_logic: List[Dict[str, Any]] = Field(..., alias="conditionLogic")
    action_config: List[Dict[str, Any]] = Field(..., alias="actionConfig")
    last_run_at: Optional[datetime] = Field(None, alias="lastRunAt")
    next_run_at: Optional[datetime] = Field(None, alias="nextRunAt")
    retry_count: int = Field(..., alias="retryCount")
    max_retries: int = Field(..., alias="maxRetries")
    created_at: Optional[datetime] = Field(None, alias="createdAt")
    updated_at: Optional[datetime] = Field(None, alias="updatedAt")


class AutomationHistoryResponse(BaseModel):
    id: int
    rule_id: int = Field(..., alias="ruleId")
    status: str
    trigger_payload: Dict[str, Any] = Field(default_factory=dict, alias="triggerPayload")
    result_payload: Dict[str, Any] = Field(default_factory=dict, alias="resultPayload")
    error_message: Optional[str] = Field(None, alias="errorMessage")
    attempt: int
    started_at: Optional[datetime] = Field(None, alias="startedAt")
    finished_at: Optional[datetime] = Field(None, alias="finishedAt")
    triggered_by: str = Field(..., alias="triggeredBy")


class NotificationPreferencePayload(BaseModel):
    user_id: str = Field(..., alias="userId")
    channel: str
    destination: Optional[str]
    enabled: bool = True
    quiet_hours_start: Optional[time] = Field(None, alias="quietHoursStart")
    quiet_hours_end: Optional[time] = Field(None, alias="quietHoursEnd")
    preferences: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        allow_population_by_field_name = True

    @validator("channel")
    def validate_channel(cls, value: str) -> str:
        supported = {"email", "sms", "whatsapp", "push"}
        if value not in supported:
            raise ValueError(f"Channel '{value}' nu este suportat. Canale acceptate: {', '.join(sorted(supported))}")
        return value


class NotificationPreferenceResponse(NotificationPreferencePayload):
    id: int
    updated_at: Optional[datetime] = Field(None, alias="updatedAt")

