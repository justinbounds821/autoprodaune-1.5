#!/usr/bin/env bash
# Smoke test for AutoPro Daune API (bash version)
# Tests critical endpoints to verify backend is working

set -e

BASE_URL="http://127.0.0.1:8001"
FAILED=0

echo "🧪 Running AutoPro Daune Smoke Tests..."

test_endpoint() {
    local name="$1"
    local url="$2"
    echo ""
    echo "📍 Testing: $name"
    echo "   GET $url"

    if response=$(curl -sS "$url" 2>&1); then
        echo "   ✅ Response: ${response:0:100}"
    else
        echo "   ❌ FAILED"
        ((FAILED++))
    fi
}

# Test 1: Health check
test_endpoint "Health Check" "$BASE_URL/health"

# Test 2: Mock data
test_endpoint "Mock Data" "$BASE_URL/api/test/mock-data"

# Test 3: Automation status
test_endpoint "Automation Status" "$BASE_URL/api/automation/status"

# Test 4: Payments list
test_endpoint "Payments List" "$BASE_URL/api/financial/payments"

# Test 5: HeyGen avatars
test_endpoint "HeyGen Avatars" "$BASE_URL/api/video/video/heygen/avatars"

# Test 6: HeyGen generate (expect 400 if key missing)
echo ""
echo "📍 Testing: HeyGen Generate (expect 400 if key missing)"
response=$(curl -sS -X POST "$BASE_URL/api/video/video/heygen/generate" \
    -H "Content-Type: application/json" \
    -d '{"script":"test"}' 2>&1 || true)

if echo "$response" | grep -q "HEYGEN_API_KEY"; then
    echo "   ✅ Correctly returns 400 with API key message"
else
    echo "   ⚠️ Unexpected response (may need UX improvement)"
    echo "   Response: $response"
fi

# Summary
echo ""
echo "═══════════════════════════════════════"
if [ "$FAILED" -eq 0 ]; then
    echo "✅ All smoke tests passed!"
else
    echo "❌ $FAILED test(s) failed"
fi
echo "═══════════════════════════════════════"

exit $FAILED
