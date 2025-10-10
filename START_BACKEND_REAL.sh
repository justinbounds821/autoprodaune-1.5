#!/bin/bash

# 🚀 AutoPro Daune - Backend Startup Script
# This script installs dependencies and starts the backend server

set -e  # Exit on error

echo "======================================"
echo "🚀 AutoPro Daune - Backend Startup"
echo "======================================"
echo ""

# Navigate to API directory
cd /workspace/services/api

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ ERROR: .env file not found!"
    echo "Please create .env file with API keys"
    exit 1
fi

echo "✅ .env file found"
echo ""

# Check Python version
echo "📋 Checking Python version..."
python3 --version
echo ""

# Install dependencies if not already installed
echo "📦 Installing dependencies..."
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

echo "Installing packages from requirements.txt..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "✅ Dependencies installed successfully!"
echo ""

# Set PYTHONPATH
export PYTHONPATH=/workspace/services/api

# Start the server
echo "🚀 Starting FastAPI server..."
echo "Backend will be available at: http://localhost:8001"
echo "API Documentation: http://localhost:8001/docs"
echo "Health check: http://localhost:8001/health"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
