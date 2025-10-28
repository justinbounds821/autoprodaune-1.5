#!/bin/bash

# 🚀 AutoPro Daune - Frontend Startup Script
# This script installs dependencies and starts the frontend dev server

set -e  # Exit on error

echo "======================================"
echo "🚀 AutoPro Daune - Frontend Startup"
echo "======================================"
echo ""

# Navigate to frontend directory
cd /workspace/02_FRONTEND_UI_CLEAN

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing npm dependencies..."
    npm install
    echo "✅ Dependencies installed!"
else
    echo "✅ Dependencies already installed"
fi

echo ""
echo "🚀 Starting Vite dev server..."
echo "Frontend will be available at: http://localhost:3006 or http://localhost:3007"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

npm run dev
