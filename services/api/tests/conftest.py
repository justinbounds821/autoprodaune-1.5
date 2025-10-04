"""
Pytest configuration and shared fixtures for AutoPro Daune API tests.
"""

import asyncio
import os
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.main import app
from app.core.config import get_settings
from app.core.database import get_supabase
from app.core.redis_client import get_redis
from app.services.whatsapp_bot import WhatsAppBot


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_settings():
    """Override settings for testing."""
    settings = get_settings()
    settings.ENVIRONMENT = "test"
    settings.DEBUG = True
    settings.SUPABASE_URL = "https://test.supabase.co"
    settings.SUPABASE_KEY = "test-key"
    settings.SECRET_KEY = "test-secret-key-for-testing-only"
    settings.REDIS_URL = "redis://localhost:6379/1"
    return settings


@pytest.fixture
def mock_supabase():
    """Mock Supabase client for testing."""
    mock_client = MagicMock()

    # Mock table operations
    mock_table = MagicMock()
    mock_client.table.return_value = mock_table

    # Mock common operations
    mock_table.select.return_value = mock_table
    mock_table.insert.return_value = mock_table
    mock_table.update.return_value = mock_table
    mock_table.delete.return_value = mock_table
    mock_table.eq.return_value = mock_table
    mock_table.execute.return_value = MagicMock(
        data=[{"id": "test-id", "name": "Test Lead"}],
        count=1
    )

    return mock_client


@pytest.fixture
def mock_redis():
    """Mock Redis client for testing."""
    mock_client = AsyncMock()
    mock_client.get.return_value = None
    mock_client.set.return_value = True
    mock_client.delete.return_value = 1
    mock_client.exists.return_value = 0
    return mock_client


@pytest.fixture
def mock_whatsapp():
    """Mock WhatsApp bot for testing."""
    mock_bot = AsyncMock(spec=WhatsAppBot)
    mock_bot.send_message.return_value = {"success": True, "message_id": "test-msg-id"}
    mock_bot.send_document.return_value = {"success": True, "message_id": "test-doc-id"}
    mock_bot.add_to_group.return_value = {"success": True}
    return mock_bot


@pytest.fixture
def client(test_settings, mock_supabase, mock_redis, mock_whatsapp) -> TestClient:
    """Create test client with mocked dependencies."""

    def override_get_supabase():
        return mock_supabase

    def override_get_redis():
        return mock_redis

    def override_get_whatsapp():
        return mock_whatsapp

    app.dependency_overrides[get_supabase] = override_get_supabase
    app.dependency_overrides[get_redis] = override_get_redis

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def async_client(test_settings, mock_supabase, mock_redis, mock_whatsapp) -> AsyncGenerator[AsyncClient, None]:
    """Create async test client with mocked dependencies."""

    def override_get_supabase():
        return mock_supabase

    def override_get_redis():
        return mock_redis

    def override_get_whatsapp():
        return mock_whatsapp

    app.dependency_overrides[get_supabase] = override_get_supabase
    app.dependency_overrides[get_redis] = override_get_redis

    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
def sample_lead_data():
    """Sample lead data for testing."""
    return {
        "name": "Ion Test",
        "phone_number": "0721123456",
        "email": "ion.test@example.com",
        "source": "test",
        "lead_type": "crash_claim",
        "details": "Test accident pentru sistem automat",
        "status": "new"
    }


@pytest.fixture
def sample_referral_data():
    """Sample referral data for testing."""
    return {
        "referrer_phone": "0721111111",
        "referrer_name": "Maria Referrer",
        "referred_phone": "0721222222",
        "referred_name": "Ion Referred",
        "status": "pending",
        "reward_amount": 200.0,
        "currency": "LEI"
    }


@pytest.fixture
def sample_social_post_data():
    """Sample social post data for testing."""
    return {
        "title": "Test Post",
        "content": "This is a test social media post",
        "platforms": ["tiktok", "instagram"],
        "video_url": "https://example.com/test-video.mp4",
        "status": "scheduled"
    }


@pytest.fixture
def sample_whatsapp_webhook_data():
    """Sample WhatsApp webhook data for testing."""
    return {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "entry-id",
                "changes": [
                    {
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "40723456789",
                                "phone_number_id": "phone-id"
                            },
                            "messages": [
                                {
                                    "from": "40721123456",
                                    "id": "message-id",
                                    "timestamp": "1704067200",
                                    "text": {
                                        "body": "Test message from user"
                                    },
                                    "type": "text"
                                }
                            ]
                        },
                        "field": "messages"
                    }
                ]
            }
        ]
    }


@pytest.fixture
def mock_openai():
    """Mock OpenAI client for testing."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content="Generated test content"))
    ]
    mock_client.chat.completions.create.return_value = mock_response
    return mock_client


@pytest.fixture
def mock_social_media_apis():
    """Mock social media API clients for testing."""
    return {
        "tiktok": MagicMock(
            upload_video=AsyncMock(return_value={"success": True, "post_id": "tiktok-123"})
        ),
        "instagram": MagicMock(
            upload_video=AsyncMock(return_value={"success": True, "post_id": "ig-123"})
        ),
        "youtube": MagicMock(
            upload_video=AsyncMock(return_value={"success": True, "post_id": "yt-123"})
        )
    }


@pytest.fixture(autouse=True)
def setup_test_env():
    """Setup test environment variables."""
    test_env = {
        "ENVIRONMENT": "test",
        "DEBUG": "true",
        "SECRET_KEY": "test-secret-key-for-testing-only",
        "SUPABASE_URL": "https://test.supabase.co",
        "SUPABASE_KEY": "test-key",
        "REDIS_URL": "redis://localhost:6379/1",
        "WHATSAPP_ACCESS_TOKEN": "test-whatsapp-token",
        "WHATSAPP_PHONE_NUMBER_ID": "test-phone-id",
        "OPENAI_API_KEY": "test-openai-key"
    }

    for key, value in test_env.items():
        os.environ[key] = value

    yield

    # Cleanup
    for key in test_env.keys():
        os.environ.pop(key, None)