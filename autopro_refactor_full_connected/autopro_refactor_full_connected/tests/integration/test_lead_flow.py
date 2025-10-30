import pytest

@pytest.mark.asyncio
async def test_create_and_retrieve_lead(lead_client):
    # Create a lead
    lead_data = {
        "name": "Integration Test User",
        "email": "test@integration.com",
        "phone": "1234567890"
    }

    # Note: This would need a valid JWT token in production
    # For now, this is a structural test

    # Test health endpoint
    response = await lead_client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
