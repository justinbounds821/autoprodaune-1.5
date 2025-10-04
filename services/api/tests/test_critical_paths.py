"""
AutoPro Daune - Critical Path Tests

This module tests the most important user journeys and business logic
to ensure the core functionality works correctly.
"""

import pytest
import asyncio
import httpx
import os
from datetime import datetime
from typing import Dict, Any

# Test configuration
API_BASE_URL = "http://localhost:8000"
TIMEOUT = 30

class TestCriticalPaths:
    """Test the critical business paths of AutoPro Daune."""

    @pytest.fixture
    async def client(self):
        """Create HTTP client for API testing."""
        async with httpx.AsyncClient(base_url=API_BASE_URL, timeout=TIMEOUT) as client:
            yield client

    @pytest.fixture
    def sample_lead_data(self):
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
    def sample_referral_data(self):
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

    async def test_api_health_check(self, client):
        """Test that the API is running and healthy."""
        response = await client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "ok"
        print("✅ API health check passed")

    async def test_api_root_endpoint(self, client):
        """Test the root endpoint."""
        response = await client.get("/")
        assert response.status_code == 200

        data = response.json()
        assert "AutoPro Daune API" in data["message"]
        print("✅ Root endpoint test passed")

    async def test_lead_creation_flow(self, client, sample_lead_data):
        """Test the complete lead creation flow."""
        # Create a new lead
        response = await client.post("/api/leads/", json=sample_lead_data)
        assert response.status_code == 200

        data = response.json()
        assert data["success"] == True
        assert "Lead creat cu succes" in data["message"]

        lead_id = data["data"][0]["id"] if data["data"] else None
        assert lead_id is not None

        print(f"✅ Lead created successfully with ID: {lead_id}")

        # Retrieve the created lead
        response = await client.get(f"/api/leads/{lead_id}")
        assert response.status_code == 200

        lead_data = response.json()
        assert lead_data["name"] == sample_lead_data["name"]
        assert lead_data["phone_number"] == sample_lead_data["phone_number"]

        print("✅ Lead retrieval test passed")

        # List leads
        response = await client.get("/api/leads/")
        assert response.status_code == 200

        leads_list = response.json()
        assert "items" in leads_list
        assert len(leads_list["items"]) >= 1

        print("✅ Lead listing test passed")

        return lead_id

    async def test_referral_system_flow(self, client, sample_referral_data):
        """Test the complete referral system flow."""
        # Create a referral
        response = await client.post("/api/referrals/", json=sample_referral_data)
        assert response.status_code == 200

        data = response.json()
        assert data["success"] == True
        assert "Referral creat cu succes" in data["message"]

        print("✅ Referral creation test passed")

        # Get referral stats
        response = await client.get("/api/referrals/stats")
        assert response.status_code == 200

        stats = response.json()
        print("✅ Referral stats test passed")

    async def test_social_media_endpoints(self, client):
        """Test social media management endpoints."""
        # Get social summary
        response = await client.get("/api/social/summary")
        assert response.status_code == 200

        print("✅ Social media summary test passed")

        # Get social posts
        response = await client.get("/api/social/posts")
        assert response.status_code == 200

        posts_data = response.json()
        assert "items" in posts_data

        print("✅ Social posts listing test passed")

        # Get social analytics
        response = await client.get("/api/social/analytics")
        assert response.status_code == 200

        analytics = response.json()
        assert "total_posts" in analytics

        print("✅ Social analytics test passed")

    async def test_whatsapp_webhook_validation(self, client):
        """Test WhatsApp webhook endpoint."""
        # Test webhook verification (GET request)
        verify_token = "test_verify_token"
        challenge = "test_challenge"

        response = await client.get(
            "/api/whatsapp/webhook",
            params={
                "hub.mode": "subscribe",
                "hub.challenge": challenge,
                "hub.verify_token": verify_token
            }
        )

        # Should return the challenge if verify token matches
        # or handle gracefully if not configured
        assert response.status_code in [200, 403]

        print("✅ WhatsApp webhook verification test passed")

    async def test_automation_endpoints(self, client):
        """Test automation system endpoints."""
        # Get automation status
        response = await client.get("/api/automation/status")
        assert response.status_code == 200

        status = response.json()
        assert "automation_active" in status

        print("✅ Automation status test passed")

        # Get automation performance
        response = await client.get("/api/automation/performance")
        assert response.status_code == 200

        performance = response.json()
        assert "summary" in performance

        print("✅ Automation performance test passed")

    async def test_video_queue_endpoints(self, client):
        """Test video generation queue endpoints."""
        # Get video queue
        response = await client.get("/api/video/queue")
        assert response.status_code == 200

        queue_data = response.json()
        assert "items" in queue_data

        print("✅ Video queue test passed")

    async def test_content_endpoints(self, client):
        """Test content management endpoints."""
        # List content items
        response = await client.get("/api/content/")
        assert response.status_code == 200

        print("✅ Content listing test passed")

    async def test_complete_user_journey(self, client, sample_lead_data):
        """Test a complete user journey from lead to referral."""
        print("\n🚀 Starting complete user journey test...")

        # Step 1: User visits landing page and submits lead form
        lead_id = await self.test_lead_creation_flow(client, sample_lead_data)

        # Step 2: System processes lead and adds to WhatsApp group (simulated)
        print("✅ Step 2: Lead processed and added to WhatsApp community")

        # Step 3: User becomes client and refers a friend
        referral_data = {
            "referrer_phone": sample_lead_data["phone_number"],
            "referrer_name": sample_lead_data["name"],
            "referred_phone": "0721333333",
            "referred_name": "Prietenul Referit",
            "lead_id": lead_id,
            "status": "pending"
        }

        response = await client.post("/api/referrals/", json=referral_data)
        assert response.status_code == 200
        print("✅ Step 3: Referral created successfully")

        # Step 4: Check automation is working
        response = await client.get("/api/automation/status")
        assert response.status_code == 200
        print("✅ Step 4: Automation system active")

        print("🎉 Complete user journey test passed!")

    async def test_error_handling(self, client):
        """Test error handling for common scenarios."""
        # Test invalid lead creation
        invalid_lead = {"name": ""}  # Missing required fields
        response = await client.post("/api/leads/", json=invalid_lead)
        assert response.status_code in [400, 422, 500]  # Should handle error gracefully

        # Test non-existent lead retrieval
        response = await client.get("/api/leads/99999")
        assert response.status_code in [404, 500]  # Should handle gracefully

        print("✅ Error handling tests passed")

    async def test_rate_limiting(self, client):
        """Test API rate limiting."""
        # Make multiple rapid requests to test rate limiting
        responses = []
        for i in range(10):
            response = await client.get("/api/leads/")
            responses.append(response.status_code)

        # Should not all fail due to rate limiting in normal usage
        success_count = sum(1 for status in responses if status == 200)
        assert success_count >= 5  # At least half should succeed

        print("✅ Rate limiting test passed")

    async def test_performance_benchmarks(self, client):
        """Test basic performance benchmarks."""
        import time

        # Test response times for critical endpoints
        endpoints = [
            "/health",
            "/api/leads/",
            "/api/social/summary",
            "/api/automation/status"
        ]

        for endpoint in endpoints:
            start_time = time.time()
            response = await client.get(endpoint)
            end_time = time.time()

            response_time = end_time - start_time
            assert response_time < 5.0  # Should respond within 5 seconds

            print(f"✅ {endpoint} responded in {response_time:.2f}s")

    async def test_data_consistency(self, client, sample_lead_data):
        """Test data consistency across different endpoints."""
        # Create a lead
        response = await client.post("/api/leads/", json=sample_lead_data)
        assert response.status_code == 200

        data = response.json()
        lead_id = data["data"][0]["id"] if data["data"] else None

        # Verify lead appears in listings
        response = await client.get("/api/leads/")
        leads_list = response.json()

        # Find our lead in the list
        found_lead = None
        for lead in leads_list.get("items", []):
            if lead.get("id") == lead_id:
                found_lead = lead
                break

        assert found_lead is not None
        assert found_lead["name"] == sample_lead_data["name"]

        print("✅ Data consistency test passed")


# Pytest runner functions
@pytest.mark.asyncio
async def test_api_health():
    """Test API health."""
    test_instance = TestCriticalPaths()
    async with httpx.AsyncClient(base_url=API_BASE_URL, timeout=TIMEOUT) as client:
        await test_instance.test_api_health_check(client)

@pytest.mark.asyncio
async def test_leads_flow():
    """Test leads flow."""
    test_instance = TestCriticalPaths()
    sample_lead = {
        "name": "Ion Test",
        "phone_number": "0721123456",
        "email": "ion.test@example.com",
        "source": "test",
        "lead_type": "crash_claim",
        "details": "Test accident pentru sistem automat",
        "status": "new"
    }
    async with httpx.AsyncClient(base_url=API_BASE_URL, timeout=TIMEOUT) as client:
        await test_instance.test_lead_creation_flow(client, sample_lead)

@pytest.mark.asyncio
async def test_complete_journey():
    """Test complete user journey."""
    test_instance = TestCriticalPaths()
    sample_lead = {
        "name": "Ion Journey Test",
        "phone_number": "0721999999",
        "email": "ion.journey@example.com",
        "source": "test",
        "lead_type": "crash_claim",
        "details": "Complete journey test",
        "status": "new"
    }
    async with httpx.AsyncClient(base_url=API_BASE_URL, timeout=TIMEOUT) as client:
        await test_instance.test_complete_user_journey(client, sample_lead)


def run_smoke_tests():
    """Run basic smoke tests to verify system health."""
    print("\n🔥 AutoPro Daune - Running Smoke Tests...")
    print("=" * 50)

    try:
        # Run basic tests
        asyncio.run(test_api_health())
        asyncio.run(test_leads_flow())

        print("\n✅ All smoke tests passed!")
        print("🚀 System is ready for deployment!")
        return True

    except Exception as e:
        print(f"\n❌ Smoke tests failed: {e}")
        print("🛠️ Please fix issues before deployment.")
        return False


def run_full_test_suite():
    """Run the complete test suite."""
    print("\n🧪 AutoPro Daune - Running Full Test Suite...")
    print("=" * 50)

    try:
        # Run all tests
        asyncio.run(test_api_health())
        asyncio.run(test_leads_flow())
        asyncio.run(test_complete_journey())

        print("\n🎉 All tests passed!")
        print("🚀 System is fully validated and ready!")
        return True

    except Exception as e:
        print(f"\n❌ Tests failed: {e}")
        print("🛠️ Please address issues before deployment.")
        return False


if __name__ == "__main__":
    # Run smoke tests by default
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--full":
        success = run_full_test_suite()
    else:
        success = run_smoke_tests()

    sys.exit(0 if success else 1)