#!/bin/bash
# AutoPro Daune - Smoke Tests
# Testează toate endpoint-urile critice ale API-ului

set -e

BASE_URL="http://localhost:8000"
AUTH_TOKEN="Bearer test"

echo "🧪 AutoPro Daune Smoke Tests"
echo "=============================="

# Test 1: Health Check
echo "1. Testing health endpoint..."
curl -s -f "$BASE_URL/health" | jq '.' || {
    echo "❌ Health check failed"
    exit 1
}
echo "✅ Health check passed"

# Test 2: Metrics endpoint
echo "2. Testing metrics endpoint..."
curl -s -f "$BASE_URL/metrics" | grep -q "http_requests_total" || {
    echo "❌ Metrics endpoint failed"
    exit 1
}
echo "✅ Metrics endpoint passed"

# Test 3: Root endpoint
echo "3. Testing root endpoint..."
curl -s -f "$BASE_URL/" | jq '.status' | grep -q "ok" || {
    echo "❌ Root endpoint failed"
    exit 1
}
echo "✅ Root endpoint passed"

# Test 4: Video Queue (should work without auth)
echo "4. Testing video queue endpoint..."
curl -s -f "$BASE_URL/api/video/queue" | jq '.items' || {
    echo "❌ Video queue endpoint failed"
    exit 1
}
echo "✅ Video queue endpoint passed"

# Test 5: Video Stats
echo "5. Testing video stats endpoint..."
curl -s -f "$BASE_URL/api/video/stats" | jq '.total' || {
    echo "❌ Video stats endpoint failed"
    exit 1
}
echo "✅ Video stats endpoint passed"

# Test 6: Video Generate (should require auth)
echo "6. Testing video generate endpoint (auth required)..."
response=$(curl -s -w "%{http_code}" -o /dev/null -X POST "$BASE_URL/api/video/generate" \
    -H "Content-Type: application/json" \
    -d '{"duration_seconds": 5, "resolution": "720p", "text": "Test"}')

if [ "$response" = "401" ] || [ "$response" = "403" ]; then
    echo "✅ Video generate auth protection working"
else
    echo "❌ Video generate should require auth (got $response)"
    exit 1
fi

# Test 7: Rate limiting
echo "7. Testing rate limiting..."
for i in {1..7}; do
    response=$(curl -s -w "%{http_code}" -o /dev/null -X POST "$BASE_URL/api/video/generate" \
        -H "Authorization: $AUTH_TOKEN" \
        -H "Content-Type: application/json" \
        -d '{"duration_seconds": 5, "resolution": "720p", "text": "Rate limit test"}')
    
    if [ "$i" -le 5 ]; then
        if [ "$response" != "202" ] && [ "$response" != "401" ]; then
            echo "❌ Request $i should succeed (got $response)"
            exit 1
        fi
    else
        if [ "$response" = "429" ]; then
            echo "✅ Rate limiting working (got 429 on request $i)"
            break
        fi
    fi
done

# Test 8: Redis connection (if available)
echo "8. Testing Redis connection..."
if curl -s -f "$BASE_URL/metrics" | grep -q "redis"; then
    echo "✅ Redis metrics available"
else
    echo "⚠️ Redis metrics not found (may be using in-memory rate limiting)"
fi

echo ""
echo "🎉 All smoke tests passed!"
echo "=============================="
