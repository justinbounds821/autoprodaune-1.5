import pytest
import asyncio
from httpx import AsyncClient

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def lead_client():
    async with AsyncClient(base_url="http://localhost:8001") as client:
        yield client

@pytest.fixture
async def mcp_client():
    async with AsyncClient(base_url="http://localhost:8010") as client:
        yield client
