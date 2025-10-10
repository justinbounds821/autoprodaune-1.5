#!/bin/bash
# AutoPro Daune 1.5 - Frontend Startup Script
# ============================================

echo "🚀 Starting AutoPro Daune Frontend..."

# Navigate to frontend directory
cd 02_FRONTEND_UI_CLEAN

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found! Please create .env file with required configuration."
    exit 1
fi

echo "✅ .env file found"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing Node.js dependencies..."
    npm install
fi

echo "✅ Dependencies ready"

# Start the development server
echo "🚀 Starting Vite development server on port 3006..."
npm run dev -- --port 3006 --host 0.0.0.0

echo "✅ Frontend started successfully!"
echo "🌐 Application available at: http://localhost:3006"