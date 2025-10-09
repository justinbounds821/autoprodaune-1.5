#!/bin/bash

# Test script for FAKE_MODE endpoints
# Usage: ./scripts/test-fake-mode.sh

set -e

API_BASE="${API_BASE:-http://localhost:8000}"

echo "🧪 Testing AutoPro Daune Admin Dashboard - FAKE_MODE"
echo "=================================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

test_endpoint() {
    local method=$1
    local endpoint=$2
    local description=$3
    
    echo -e "${BLUE}Testing:${NC} $description"
    echo -e "  ${method} ${API_BASE}${endpoint}"
    
    response=$(curl -s -w "\n%{http_code}" -X ${method} "${API_BASE}${endpoint}")
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
    
    if [ "$http_code" = "200" ]; then
        echo -e "  ${GREEN}✓ Success (200 OK)${NC}"
        echo "$body" | jq '.' 2>/dev/null || echo "$body"
    else
        echo -e "  ${RED}✗ Failed (${http_code})${NC}"
        echo "$body"
    fi
    echo ""
}

# Financial Dashboard
test_endpoint "GET" "/api/financial/dashboard?period=7d" "Financial Dashboard (7 days)"

# Automation Status
test_endpoint "GET" "/api/automation/status" "Automation Status"

# Automation Logs
test_endpoint "GET" "/api/automation/logs?limit=5" "Automation Logs (limit 5)"
test_endpoint "GET" "/api/automation/logs?limit=5&task_type=video_generation" "Automation Logs (filtered by task_type)"

# Video Jobs (Paginated)
test_endpoint "GET" "/api/advanced-video/jobs?page=1&limit=10" "Video Jobs (page 1, limit 10)"
test_endpoint "GET" "/api/advanced-video/jobs?page=1&limit=10&status=completed" "Video Jobs (filtered by status)"

# Video Job Status
test_endpoint "GET" "/api/advanced-video/jobs/vid_123" "Video Job Status (with progress)"

# Delete Video (mock)
# test_endpoint "DELETE" "/api/advanced-video/delete/test_video" "Delete Video"

# Credit Balance
test_endpoint "GET" "/api/financial/credit-balance/heygen" "Credit Balance - HeyGen"
test_endpoint "GET" "/api/financial/credit-balance/tiktok" "Credit Balance - TikTok"
test_endpoint "GET" "/api/financial/credit-balance/elevenlabs" "Credit Balance - ElevenLabs"

echo "=================================================="
echo -e "${GREEN}✓ FAKE_MODE Testing Complete!${NC}"
echo ""
echo "All endpoints should return 200 OK with mock data."
echo "To run backend in FAKE_MODE:"
echo "  export FAKE_MODE=true"
echo "  uvicorn services.api.app.main:app --reload"
