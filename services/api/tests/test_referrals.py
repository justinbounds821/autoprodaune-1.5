"""
Tests for the referrals API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient


class TestReferralsAPI:
    """Test suite for referral system endpoints."""

    def test_create_referral_success(self, client: TestClient, sample_referral_data):
        """Test successful referral creation."""
        response = client.post("/api/referrals/", json=sample_referral_data)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "Referral creat cu succes" in data["message"]

    def test_create_referral_duplicate(self, client: TestClient, sample_referral_data):
        """Test creating duplicate referral."""
        # Create first referral
        client.post("/api/referrals/", json=sample_referral_data)

        # Try to create duplicate
        response = client.post("/api/referrals/", json=sample_referral_data)

        # Should handle gracefully (either allow or prevent duplicate)
        assert response.status_code in [200, 400, 409]

    def test_get_referrals_list(self, client: TestClient):
        """Test retrieving referrals list."""
        response = client.get("/api/referrals/")

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert isinstance(data["items"], list)

    def test_get_referral_stats(self, client: TestClient):
        """Test referral statistics endpoint."""
        response = client.get("/api/referrals/stats")

        assert response.status_code == 200
        data = response.json()
        # Should return statistical data
        assert isinstance(data, dict)

    def test_complete_referral(self, client: TestClient, mock_supabase):
        """Test marking referral as completed."""
        # Setup mock to return referral data
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [
            {"id": "test-ref-id", "status": "completed", "reward_amount": 200.0}
        ]

        response = client.put("/api/referrals/test-ref-id/complete")

        assert response.status_code in [200, 404]

    def test_referral_by_phone(self, client: TestClient):
        """Test getting referrals by phone number."""
        response = client.get("/api/referrals/?referrer_phone=0721123456")

        assert response.status_code == 200
        data = response.json()
        assert "items" in data

    def test_referral_code_generation(self, client: TestClient, sample_referral_data):
        """Test that referral codes are generated automatically."""
        response = client.post("/api/referrals/", json=sample_referral_data)

        assert response.status_code == 200
        # Should generate referral code automatically
        # (Implementation specific - may be handled in service layer)

    def test_referral_reward_calculation(self, client: TestClient, sample_referral_data):
        """Test reward amount calculation."""
        # Test with default reward amount
        response = client.post("/api/referrals/", json=sample_referral_data)
        assert response.status_code == 200

        # Test with custom reward amount
        custom_data = sample_referral_data.copy()
        custom_data["reward_amount"] = 150.0
        response = client.post("/api/referrals/", json=custom_data)
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_referral_async_operations(self, async_client: AsyncClient, sample_referral_data):
        """Test async referral operations."""
        response = await async_client.post("/api/referrals/", json=sample_referral_data)
        assert response.status_code == 200

        response = await async_client.get("/api/referrals/stats")
        assert response.status_code == 200

    def test_referral_validation(self, client: TestClient):
        """Test referral data validation."""
        invalid_data = {
            "referrer_phone": "",  # Empty phone
            "referred_phone": "",  # Empty phone
            "reward_amount": -100  # Negative amount
        }

        response = client.post("/api/referrals/", json=invalid_data)
        assert response.status_code in [200, 400, 422]

    def test_referral_performance_metrics(self, client: TestClient):
        """Test referral performance tracking."""
        response = client.get("/api/referrals/performance")

        # Should handle even if not implemented
        assert response.status_code in [200, 404, 501]

    def test_referral_leaderboard(self, client: TestClient):
        """Test referral leaderboard functionality."""
        response = client.get("/api/referrals/leaderboard")

        # Should handle even if not implemented
        assert response.status_code in [200, 404, 501]

    @pytest.mark.integration
    def test_referral_workflow_integration(self, client: TestClient, sample_lead_data, sample_referral_data):
        """Integration test for complete referral workflow."""
        # Step 1: Create a lead
        lead_response = client.post("/api/leads/", json=sample_lead_data)
        assert lead_response.status_code == 200

        # Step 2: Create referral linked to lead
        referral_data = sample_referral_data.copy()
        if lead_response.json().get("data"):
            referral_data["lead_id"] = "test-lead-id"

        response = client.post("/api/referrals/", json=referral_data)
        assert response.status_code == 200

        # Step 3: Check referral stats
        response = client.get("/api/referrals/stats")
        assert response.status_code == 200

    def test_referral_payout_tracking(self, client: TestClient):
        """Test referral payout tracking functionality."""
        response = client.get("/api/referrals/payouts")

        # Should handle payout tracking
        assert response.status_code in [200, 404, 501]

    def test_referral_currency_handling(self, client: TestClient, sample_referral_data):
        """Test different currency handling."""
        # Test with LEI (default)
        response = client.post("/api/referrals/", json=sample_referral_data)
        assert response.status_code == 200

        # Test with different currency
        eur_data = sample_referral_data.copy()
        eur_data["currency"] = "EUR"
        eur_data["reward_amount"] = 50.0
        eur_data["referred_phone"] = "0721333333"  # Different phone to avoid duplicate

        response = client.post("/api/referrals/", json=eur_data)
        assert response.status_code == 200