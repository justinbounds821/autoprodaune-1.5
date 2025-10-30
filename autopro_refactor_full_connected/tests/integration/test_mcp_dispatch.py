import pytest

@pytest.mark.asyncio
async def test_mcp_health(mcp_client):
    response = await mcp_client.get("/health")
    assert response.status_code == 200
    assert response.json()["service"] == "mcp-service"

@pytest.mark.asyncio
async def test_dispatch_github_mock(mcp_client):
    dispatch_data = {
        "target": "github",
        "action": "create_issue",
        "payload": {
            "repo": "test/repo",
            "title": "Test Issue",
            "body": "Test body"
        }
    }

    response = await mcp_client.post("/api/v1/dispatch", json=dispatch_data)
    assert response.status_code == 200
    data = response.json()
    assert "mock" in data or "issue_id" in data
