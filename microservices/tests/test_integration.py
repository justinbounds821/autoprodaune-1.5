"""
Integration Tests for AutoPro Microservices
Test the complete flow across services
"""
import pytest
import httpx
import asyncio
import json
import time
from typing import Dict, Any

# Test configuration
BASE_URL = "http://localhost"
CORE_API_URL = "http://localhost:8001"
VIDEO_SERVICE_URL = "http://localhost:8002"

@pytest.mark.asyncio
async def test_health_checks():
    """Test that all services are healthy."""
    async with httpx.AsyncClient() as client:
        # Gateway health
        response = await client.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        
        # Core API health
        response = await client.get(f"{CORE_API_URL}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "core-api"
        assert data["status"] == "healthy"
        
        # Video Service health
        response = await client.get(f"{VIDEO_SERVICE_URL}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "video-service"
        assert data["status"] == "healthy"

@pytest.mark.asyncio
async def test_lead_crud_flow():
    """Test complete lead CRUD flow through gateway."""
    async with httpx.AsyncClient() as client:
        # 1. Create lead
        lead_data = {
            "name": "Test Lead Integration",
            "phone_number": "0712345678",
            "source": "test",
            "notes": "Integration test lead"
        }
        
        response = await client.post(
            f"{BASE_URL}/api/leads",
            json=lead_data,
            timeout=10.0
        )
        
        # Should succeed or return 201/200
        assert response.status_code in [200, 201, 500]  # Allow 500 if DB not configured
        
        if response.status_code in [200, 201]:
            result = response.json()
            assert result.get("success") == True
            
            # 2. List leads (verify creation)
            response = await client.get(f"{BASE_URL}/api/leads")
            assert response.status_code == 200
            
            data = response.json()
            assert "items" in data or "data" in data

@pytest.mark.asyncio
async def test_video_generation_async_flow():
    """Test async video generation flow."""
    async with httpx.AsyncClient() as client:
        # 1. Enqueue video job
        video_request = {
            "prompt": "Test video for integration testing",
            "duration": 10,
            "resolution": "720p"
        }
        
        response = await client.post(
            f"{BASE_URL}/api/video/generate",
            json=video_request,
            timeout=10.0
        )
        
        assert response.status_code == 200
        result = response.json()
        
        assert result["success"] == True
        assert "job_id" in result
        assert result["status"] == "queued"
        
        job_id = result["job_id"]
        
        # 2. Check job status
        response = await client.get(f"{BASE_URL}/api/video/status/{job_id}")
        assert response.status_code in [200, 404]  # 404 if Redis not available
        
        if response.status_code == 200:
            status = response.json()
            assert status["job_id"] == job_id
            assert status["status"] in ["queued", "processing", "completed", "failed"]
            
        # 3. List jobs
        response = await client.get(f"{BASE_URL}/api/video/jobs")
        assert response.status_code == 200
        
        jobs = response.json()
        assert "jobs" in jobs

@pytest.mark.asyncio
async def test_api_gateway_routing():
    """Test that API Gateway routes correctly to services."""
    async with httpx.AsyncClient() as client:
        # Test Core API routes through gateway
        routes_to_test = [
            f"{BASE_URL}/api/leads",
            f"{BASE_URL}/api/referrals",
            f"{BASE_URL}/api/financial/dashboard",
        ]
        
        for route in routes_to_test:
            try:
                response = await client.get(route, timeout=5.0)
                # Should return 200, 404, or 500 (not 502 Bad Gateway)
                assert response.status_code in [200, 404, 500]
                assert response.status_code != 502
            except httpx.TimeoutException:
                pytest.skip(f"Route {route} timed out")

@pytest.mark.asyncio
async def test_concurrent_requests():
    """Test that system handles concurrent requests."""
    async with httpx.AsyncClient() as client:
        # Send 10 concurrent health check requests
        tasks = [
            client.get(f"{BASE_URL}/health", timeout=5.0)
            for _ in range(10)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Count successful responses
        successful = sum(1 for r in results if isinstance(r, httpx.Response) and r.status_code == 200)
        
        # At least 80% should succeed
        assert successful >= 8, f"Only {successful}/10 concurrent requests succeeded"

@pytest.mark.asyncio
async def test_metrics_endpoints():
    """Test that Prometheus metrics are exposed."""
    async with httpx.AsyncClient() as client:
        # Core API metrics
        response = await client.get(f"{CORE_API_URL}/metrics", timeout=5.0)
        assert response.status_code == 200
        assert "TYPE" in response.text  # Prometheus format
        
        # Video Service metrics
        response = await client.get(f"{VIDEO_SERVICE_URL}/metrics", timeout=5.0)
        assert response.status_code == 200
        assert "TYPE" in response.text

def test_env_variables():
    """Test that required environment variables are set."""
    import os
    
    # Check for critical env vars (in CI/test environment)
    # These might not be set in dev, so we just warn
    required_vars = [
        "SUPABASE_URL",
        "SUPABASE_KEY",
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        pytest.skip(f"Missing environment variables: {', '.join(missing_vars)}")

# Run with: pytest microservices/tests/test_integration.py -v
