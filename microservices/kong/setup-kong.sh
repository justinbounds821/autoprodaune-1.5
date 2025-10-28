#!/bin/bash
# Kong API Gateway Setup Script

set -e

KONG_ADMIN_URL="${KONG_ADMIN_URL:-http://localhost:8001}"

echo "🔧 Configuring Kong API Gateway..."

# Wait for Kong to be ready
echo "⏳ Waiting for Kong to be ready..."
until curl -f -s "$KONG_ADMIN_URL/status" > /dev/null; do
  echo "  Kong not ready yet, waiting..."
  sleep 2
done
echo "✅ Kong is ready!"

# Apply declarative configuration
echo "📋 Applying Kong configuration..."
curl -i -X POST "$KONG_ADMIN_URL/config" \
  -F config=@kong.yml

echo "✅ Kong configuration applied successfully!"

# Verify services
echo "🔍 Verifying services..."
curl -s "$KONG_ADMIN_URL/services" | jq '.data[].name'

echo "✅ Kong setup complete!"
echo ""
echo "📊 Kong Admin UI: http://localhost:8001"
echo "🌐 Kong Proxy: http://localhost:8000"
echo ""
echo "Example requests:"
echo "  curl http://localhost:8000/api/leads"
echo "  curl http://localhost:8000/api/videos"
