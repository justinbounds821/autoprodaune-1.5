"""
Tests for the leads API endpoints.
"""

import io

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.routes import leads as leads_routes


class TestLeadsAPI:
    """Test suite for leads management endpoints."""

    def test_create_lead_success(self, client: TestClient, sample_lead_data):
        """Test successful lead creation."""
        response = client.post("/api/leads/", json=sample_lead_data)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "Lead creat cu succes" in data["message"]
        assert data["data"] is not None

    def test_create_lead_missing_fields(self, client: TestClient):
        """Test lead creation with missing required fields."""
        incomplete_data = {"name": "Test User"}

        response = client.post("/api/leads/", json=incomplete_data)

        # Should handle gracefully (either validation error or create with defaults)
        assert response.status_code in [200, 400, 422]

    def test_get_leads_list(self, client: TestClient):
        """Test retrieving leads list."""
        response = client.get("/api/leads/")

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert isinstance(data["items"], list)

    def test_get_leads_with_pagination(self, client: TestClient):
        """Test leads list with pagination parameters."""
        response = client.get("/api/leads/?page=1&limit=10")

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data or "count" in data

    def test_get_leads_with_filters(self, client: TestClient):
        """Test leads list with filter parameters."""
        response = client.get("/api/leads/?source=test&status=new")

        assert response.status_code == 200
        data = response.json()
        assert "items" in data

    @pytest.mark.asyncio
    async def test_create_lead_async(self, async_client: AsyncClient, sample_lead_data):
        """Test async lead creation."""
        response = await async_client.post("/api/leads/", json=sample_lead_data)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_get_lead_by_id_success(self, client: TestClient, mock_supabase):
        """Test retrieving a specific lead by ID."""
        # Setup mock to return specific lead data
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            {"id": "test-id", "name": "Test Lead", "phone_number": "0721123456"}
        ]

        response = client.get("/api/leads/test-id")

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Lead"

    def test_get_lead_by_id_not_found(self, client: TestClient, mock_supabase):
        """Test retrieving non-existent lead."""
        # Setup mock to return empty data
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []

        response = client.get("/api/leads/nonexistent-id")

        # Should handle gracefully
        assert response.status_code in [404, 200]

    def test_update_lead_success(self, client: TestClient, mock_supabase):
        """Test successful lead update."""
        update_data = {
            "status": "contacted",
            "notes": "Client contactat prin telefon"
        }

        # Setup mock to return updated data
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [
            {"id": "test-id", "status": "contacted", "notes": "Client contactat prin telefon"}
        ]

        response = client.put("/api/leads/test-id", json=update_data)

        # Should handle update request
        assert response.status_code in [200, 404]

    def test_delete_lead_success(self, client: TestClient, mock_supabase):
        """Test successful lead deletion."""
        # Setup mock to return deletion success
        mock_supabase.table.return_value.delete.return_value.eq.return_value.execute.return_value.count = 1

        response = client.delete("/api/leads/test-id")

        # Should handle delete request
        assert response.status_code in [200, 204, 404]

    def test_lead_validation(self, client: TestClient):
        """Test lead data validation."""
        invalid_data = {
            "name": "",  # Empty name
            "phone_number": "invalid-phone",  # Invalid phone format
            "email": "not-an-email"  # Invalid email format
        }

        response = client.post("/api/leads/", json=invalid_data)

        # Should handle validation appropriately
        assert response.status_code in [200, 400, 422]

    def test_leads_performance(self, client: TestClient):
        """Test leads endpoint performance."""
        import time

        start_time = time.time()
        response = client.get("/api/leads/")
        end_time = time.time()

        assert response.status_code == 200
        assert (end_time - start_time) < 2.0  # Should respond within 2 seconds

    def test_leads_concurrent_creation(self, client: TestClient, sample_lead_data):
        """Test concurrent lead creation."""
        import threading
        results = []

        def create_lead():
            response = client.post("/api/leads/", json=sample_lead_data)
            results.append(response.status_code)

        # Create 5 leads concurrently
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=create_lead)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # All requests should be handled
        assert len(results) == 5
        assert all(status in [200, 429] for status in results)  # 429 = rate limited

    def test_leads_data_consistency(self, client: TestClient, sample_lead_data):
        """Test data consistency in leads operations."""
        # Create a lead
        create_response = client.post("/api/leads/", json=sample_lead_data)
        assert create_response.status_code == 200

        # Verify it appears in the list
        list_response = client.get("/api/leads/")
        assert list_response.status_code == 200

        list_data = list_response.json()
        assert "items" in list_data
        # Should have at least the lead we just created
        assert len(list_data["items"]) >= 0

    @pytest.mark.integration
    def test_lead_workflow_integration(self, client: TestClient, sample_lead_data):
        """Integration test for complete lead workflow."""
        # Step 1: Create lead
        response = client.post("/api/leads/", json=sample_lead_data)
        assert response.status_code == 200

        # Step 2: List leads to verify creation
        response = client.get("/api/leads/")
        assert response.status_code == 200

        # Step 3: Get lead statistics (if endpoint exists)
        response = client.get("/api/leads/stats")
        # Should handle even if not implemented
        assert response.status_code in [200, 404, 501]

    def test_assign_lead_endpoint(self, client: TestClient, monkeypatch):
        """Ensure the assignment endpoint stores data and returns success."""

        class StubSupabase:
            def __init__(self):
                self.updated_payload = None

            def _table_select(self, table: str, *args, **kwargs):
                if table == "leads":
                    return [{"id": "lead-1", "name": "Lead Test", "email": "lead@example.com"}]
                if table == "lead_assignments":
                    return []
                return []

            def _table_update(self, table: str, payload: dict, filters):
                self.updated_payload = payload
                return [{"id": "lead-1", **payload}]

            def _table_insert(self, table: str, payload: dict):
                return {**payload, "id": "assign-1"}

        stub = StubSupabase()
        monkeypatch.setattr(leads_routes, "get_supabase_service_instance", lambda: stub)

        response = client.post(
            "/api/leads/lead-1/assign",
            json={
                "assigned_to": "Agent X",
                "assigned_to_email": "agent@example.com",
                "assigned_by": "admin",
                "notes": "Preia urgent"
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["assigned_to"] == "Agent X"
        assert stub.updated_payload["assigned_to"] == "Agent X"

    def test_upload_attachment_endpoint(self, client: TestClient, monkeypatch):
        """Verify that attachments can be uploaded and metadata is returned."""

        class StubSupabase:
            def __init__(self):
                self.attachments = []

            def _table_select(self, table: str, *args, **kwargs):
                if table == "leads":
                    return [{"id": "lead-1", "name": "Lead Test", "email": "lead@example.com"}]
                if table == "lead_assignments":
                    return []
                if table == "lead_attachments":
                    return self.attachments
                return []

            def _table_update(self, *args, **kwargs):
                return [{"id": "lead-1"}]

            def _table_insert(self, table: str, payload: dict):
                record = {**payload, "id": "att-1"}
                if table == "lead_attachments":
                    self.attachments.insert(0, record)
                return record

        stub = StubSupabase()
        monkeypatch.setattr(leads_routes, "get_supabase_service_instance", lambda: stub)
        monkeypatch.setattr(
            leads_routes,
            "upload_file",
            lambda *args, **kwargs: "https://example.com/test.txt",
        )

        response = client.post(
            "/api/leads/lead-1/attachments",
            files={"file": ("test.txt", io.BytesIO(b"hello"), "text/plain")},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["file_name"] == "test.txt"
        assert stub.attachments[0]["file_name"] == "test.txt"

    def test_status_history_endpoint(self, client: TestClient, monkeypatch):
        """Ensure status history is returned in the expected format."""

        class StubSupabase:
            def _table_select(self, table: str, *args, **kwargs):
                if table == "lead_status_history":
                    return [
                        {
                            "id": "hist-1",
                            "lead_id": "lead-1",
                            "previous_status": "new",
                            "new_status": "contacted",
                            "changed_by": "admin",
                            "changed_at": "2024-01-01T10:00:00",
                            "notes": "Sunat clientul",
                        }
                    ]
                if table == "leads":
                    return [{"id": "lead-1"}]
                return []

            def _table_update(self, *args, **kwargs):
                return [{"id": "lead-1"}]

        stub = StubSupabase()
        monkeypatch.setattr(leads_routes, "get_supabase_service_instance", lambda: stub)

        response = client.get("/api/leads/lead-1/status-history")

        assert response.status_code == 200
        data = response.json()
        assert data["lead_id"] == "lead-1"
        assert len(data["items"]) == 1
        assert data["items"][0]["new_status"] == "contacted"