#!/bin/bash
# AutoPro Daune - Backend Startup Script
# Start FastAPI server on port 8001

set -e

echo "🚀 Starting AutoPro Daune Backend..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Navigate to API directory
cd /workspace/services/api

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "Please create .env file with required configuration"
    exit 1
fi

echo "✅ .env file found"

# Set PYTHONPATH
export PYTHONPATH=/workspace/services/api

# Start server
echo "🔧 Starting Uvicorn server..."
echo "   - Host: 127.0.0.1"
echo "   - Port: 8001"
echo "   - Reload: enabled"
echo ""
echo "📊 API Documentation: http://127.0.0.1:8001/docs"
echo "🏥 Health Check: http://127.0.0.1:8001/health"
echo ""
echo "Press Ctrl+C to stop the server"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload
