#!/bin/bash
# AutoPro Daune - Frontend Startup Script
# Start React + Vite dev server on port 3006

set -e

echo "🎨 Starting AutoPro Daune Frontend..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Navigate to frontend directory
cd /workspace/02_FRONTEND_UI_CLEAN

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found, using defaults"
fi

# Check if node_modules exists
if [ ! -d node_modules ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

echo "✅ Dependencies ready"

# Start Vite dev server
echo "🔧 Starting Vite dev server..."
echo "   - Host: localhost"
echo "   - Port: 3006 (or next available)"
echo "   - Proxy: http://127.0.0.1:8001/api"
echo ""
echo "🌐 Frontend URL: http://localhost:3006"
echo "👤 Admin Panel: http://localhost:3006/admin"
echo ""
echo "Press Ctrl+C to stop the server"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

npm run dev
