import asyncio

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from services.api.app.database import Base
from services.api.app.models import automation  # noqa: F401 - ensures models are registered
from services.api.app.schemas.automation import (
    AutomationActionPayload,
    AutomationConditionPayload,
    AutomationRuleCreate,
)
from services.api.app.services.automation_service import AutomationService
from services.api.app.services.notifications import NotificationService


@pytest.fixture()
def session():
    engine = create_engine("sqlite:///:memory:")
    TestingSessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def test_create_and_list_rules(session):
    service = AutomationService(session)
    payload = AutomationRuleCreate(
        name="Follow up",
        description="Email pentru lead nou",
        cronExpression="0 9 * * *",
        timezone="Europe/Bucharest",
        isActive=True,
        triggerType="time",
        maxRetries=2,
        conditions=[
            AutomationConditionPayload(
                field="status",
                operator="equals",
                target_value="new",
                value_type="string",
            )
        ],
        actions=[
            AutomationActionPayload(
                action_type="send_email",
                action_payload={"subject": "Salut", "message": "Lead nou"},
            )
        ],
    )

    rule = service.create_rule(payload)
    rules = service.list_rules()

    assert rule["name"] == "Follow up"
    assert len(rules) == 1
    assert rules[0]["cron_expression"] == "0 9 * * *"


def test_history_recording(session):
    service = AutomationService(session)
    payload = AutomationRuleCreate(
        name="Reminder",
        description="",
        cronExpression="0 10 * * *",
        timezone="Europe/Bucharest",
        isActive=True,
        triggerType="time",
        maxRetries=1,
        conditions=[],
        actions=[AutomationActionPayload(action_type="send_email", action_payload={})],
    )

    rule = service.create_rule(payload)

    run_log = service.record_manual_run(rule["id"], "queued")
    history = service.list_history()

    assert run_log["status"] == "queued"
    assert history
    assert history[0]["status"] == "queued"


def test_notification_preferences(session):
    service = NotificationService(session, smtp_settings={"host": "localhost", "port": 25, "use_tls": False})

    saved = service.upsert_preference(
        {
            "user_id": "admin",
            "channel": "email",
            "destination": "admin@example.com",
            "enabled": True,
        }
    )

    assert saved["destination"] == "admin@example.com"
    assert service.list_preferences("admin")[0]["channel"] == "email"


@pytest.mark.asyncio
async def test_trigger_rule_skips_when_condition_not_met(session):
    service = AutomationService(session)
    payload = AutomationRuleCreate(
        name="Conditional",
        description="",
        cronExpression="0 12 * * *",
        timezone="Europe/Bucharest",
        isActive=True,
        triggerType="time",
        maxRetries=1,
        conditions=[
            AutomationConditionPayload(field="status", operator="equals", target_value="active", value_type="string")
        ],
        actions=[AutomationActionPayload(action_type="send_email", action_payload={})],
    )

    rule = service.create_rule(payload)

    result = await service.trigger_rule_async(rule["id"], {"status": "inactive"}, "test")
    assert result["status"] == "skipped"

    history = service.list_history()
    assert history[0]["status"] == "skipped"

