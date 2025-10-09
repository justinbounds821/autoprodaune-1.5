#!/bin/bash

# Admin Dashboard Endpoint Testing Script
# Run with: bash test_admin_endpoints.sh

BASE_URL="http://localhost:8001"

echo "=== Testing Admin Dashboard Endpoints ==="
echo ""

# Test 1: Financial Dashboard
echo "1. Testing Financial Dashboard (FAKE_MODE)..."
curl -s "${BASE_URL}/api/financial/dashboard?period=7d" | jq '.' || echo "FAILED"
echo ""

# Test 2: Advanced Video Jobs List (with pagination)
echo "2. Testing Video Jobs List (paginated)..."
curl -s "${BASE_URL}/api/advanced-video/list-generated?page=1&limit=5" | jq '.videos | length' || echo "FAILED"
echo ""

# Test 3: Automation Logs
echo "3. Testing Automation Logs..."
curl -s "${BASE_URL}/api/automation/logs?limit=5" | jq '.logs | length' || echo "FAILED"
echo ""

# Test 4: Credit Balance (TikTok)
echo "4. Testing Credit Balance for TikTok..."
curl -s "${BASE_URL}/api/financial/credit-balance/tiktok" | jq '.' || echo "FAILED"
echo ""

# Test 5: Credit Balance (OpenAI)
echo "5. Testing Credit Balance for OpenAI..."
curl -s "${BASE_URL}/api/financial/credit-balance/openai" | jq '.' || echo "FAILED"
echo ""

# Test 6: Automation Status
echo "6. Testing Automation Status..."
curl -s "${BASE_URL}/api/automation/status" | jq '.automation_active' || echo "FAILED"
echo ""

# Test 7: Health Check
echo "7. Testing Health Check..."
curl -s "${BASE_URL}/health" | jq '.' || echo "FAILED"
echo ""

echo "=== All Tests Complete ==="
