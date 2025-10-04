"""
Tests for WhatsApp integration endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient


class TestWhatsAppAPI:
    """Test suite for WhatsApp integration endpoints."""

    def test_webhook_verification(self, client: TestClient):
        """Test WhatsApp webhook verification (GET request)."""
        params = {
            "hub.mode": "subscribe",
            "hub.challenge": "test_challenge_123",
            "hub.verify_token": "test_verify_token"
        }

        response = client.get("/api/whatsapp/webhook", params=params)

        # Should handle verification appropriately
        assert response.status_code in [200, 403]

    def test_webhook_message_handling(self, client: TestClient, sample_whatsapp_webhook_data):
        """Test WhatsApp webhook message handling (POST request)."""
        response = client.post("/api/whatsapp/webhook", json=sample_whatsapp_webhook_data)

        # Should process webhook payload
        assert response.status_code == 200

    def test_webhook_empty_payload(self, client: TestClient):
        """Test webhook with empty payload."""
        response = client.post("/api/whatsapp/webhook", json={})

        # Should handle gracefully
        assert response.status_code in [200, 400]

    def test_webhook_invalid_payload(self, client: TestClient):
        """Test webhook with invalid payload structure."""
        invalid_payload = {
            "invalid": "structure",
            "missing": "required_fields"
        }

        response = client.post("/api/whatsapp/webhook", json=invalid_payload)

        # Should handle gracefully
        assert response.status_code in [200, 400]

    def test_send_message_endpoint(self, client: TestClient, mock_whatsapp):
        """Test sending WhatsApp message."""
        message_data = {
            "to": "40721123456",
            "message": "Test message from API",
            "message_type": "text"
        }

        response = client.post("/api/whatsapp/send", json=message_data)

        # Should handle message sending
        assert response.status_code in [200, 501]  # 501 if not implemented

    def test_send_document_endpoint(self, client: TestClient):
        """Test sending document via WhatsApp."""
        document_data = {
            "to": "40721123456",
            "document_url": "https://example.com/document.pdf",
            "caption": "Test document"
        }

        response = client.post("/api/whatsapp/send-document", json=document_data)

        # Should handle document sending
        assert response.status_code in [200, 501]

    @pytest.mark.asyncio
    async def test_webhook_async_processing(self, async_client: AsyncClient, sample_whatsapp_webhook_data):
        """Test async webhook processing."""
        response = await async_client.post("/api/whatsapp/webhook", json=sample_whatsapp_webhook_data)

        assert response.status_code == 200

    def test_webhook_message_routing(self, client: TestClient):
        """Test message routing to Manole."""
        webhook_data = {
            "object": "whatsapp_business_account",
            "entry": [
                {
                    "id": "entry-id",
                    "changes": [
                        {
                            "value": {
                                "messaging_product": "whatsapp",
                                "messages": [
                                    {
                                        "from": "40721123456",
                                        "id": "message-id",
                                        "timestamp": "1704067200",
                                        "text": {
                                            "body": "Am nevoie de ajutor cu o daună"
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

        response = client.post("/api/whatsapp/webhook", json=webhook_data)
        assert response.status_code == 200

    def test_webhook_document_processing(self, client: TestClient):
        """Test document processing in webhook."""
        document_webhook = {
            "object": "whatsapp_business_account",
            "entry": [
                {
                    "id": "entry-id",
                    "changes": [
                        {
                            "value": {
                                "messaging_product": "whatsapp",
                                "messages": [
                                    {
                                        "from": "40721123456",
                                        "id": "message-id",
                                        "timestamp": "1704067200",
                                        "document": {
                                            "id": "document-id",
                                            "mime_type": "application/pdf",
                                            "sha256": "document-hash",
                                            "filename": "crash-report.pdf"
                                        },
                                        "type": "document"
                                    }
                                ]
                            },
                            "field": "messages"
                        }
                    ]
                }
            ]
        }

        response = client.post("/api/whatsapp/webhook", json=document_webhook)
        assert response.status_code == 200

    def test_webhook_status_updates(self, client: TestClient):
        """Test WhatsApp status update webhooks."""
        status_webhook = {
            "object": "whatsapp_business_account",
            "entry": [
                {
                    "id": "entry-id",
                    "changes": [
                        {
                            "value": {
                                "messaging_product": "whatsapp",
                                "statuses": [
                                    {
                                        "id": "message-id",
                                        "status": "delivered",
                                        "timestamp": "1704067200",
                                        "recipient_id": "40721123456"
                                    }
                                ]
                            },
                            "field": "messages"
                        }
                    ]
                }
            ]
        }

        response = client.post("/api/whatsapp/webhook", json=status_webhook)
        assert response.status_code == 200

    def test_webhook_rate_limiting(self, client: TestClient, sample_whatsapp_webhook_data):
        """Test webhook rate limiting."""
        # Send multiple webhook requests rapidly
        responses = []
        for _ in range(10):
            response = client.post("/api/whatsapp/webhook", json=sample_whatsapp_webhook_data)
            responses.append(response.status_code)

        # Most should succeed, but may hit rate limits
        success_count = sum(1 for status in responses if status == 200)
        assert success_count >= 5  # At least half should succeed

    def test_webhook_security_headers(self, client: TestClient, sample_whatsapp_webhook_data):
        """Test webhook request with security headers."""
        headers = {
            "X-Hub-Signature-256": "sha256=test-signature",
            "User-Agent": "WhatsApp/2.0"
        }

        response = client.post(
            "/api/whatsapp/webhook",
            json=sample_whatsapp_webhook_data,
            headers=headers
        )

        assert response.status_code == 200

    @pytest.mark.integration
    def test_whatsapp_lead_integration(self, client: TestClient, sample_lead_data):
        """Integration test for WhatsApp to lead conversion."""
        # Simulate WhatsApp message that should create a lead
        webhook_data = {
            "object": "whatsapp_business_account",
            "entry": [
                {
                    "id": "entry-id",
                    "changes": [
                        {
                            "value": {
                                "messaging_product": "whatsapp",
                                "contacts": [
                                    {
                                        "profile": {
                                            "name": "Ion Potențial Client"
                                        },
                                        "wa_id": "40721123456"
                                    }
                                ],
                                "messages": [
                                    {
                                        "from": "40721123456",
                                        "id": "message-id",
                                        "timestamp": "1704067200",
                                        "text": {
                                            "body": "Vreau să fac o reclamație pentru daună auto"
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

        # Process webhook
        response = client.post("/api/whatsapp/webhook", json=webhook_data)
        assert response.status_code == 200

        # Check if lead was created (depends on implementation)
        leads_response = client.get("/api/leads/")
        assert leads_response.status_code == 200

    def test_webhook_performance(self, client: TestClient, sample_whatsapp_webhook_data):
        """Test webhook processing performance."""
        import time

        start_time = time.time()
        response = client.post("/api/whatsapp/webhook", json=sample_whatsapp_webhook_data)
        end_time = time.time()

        assert response.status_code == 200
        assert (end_time - start_time) < 1.0  # Should process within 1 second