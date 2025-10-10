#!/bin/bash
# AutoPro Daune 1.5 - Backend Startup Script
# ==========================================

echo "🚀 Starting AutoPro Daune Backend..."

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found! Please create .env file with required configuration."
    exit 1
fi

echo "✅ .env file found"

# Navigate to services directory
cd services/api

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Set environment variables
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Start the FastAPI server
echo "🚀 Starting FastAPI server on port 8001..."
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

echo "✅ Backend started successfully!"
echo "🌐 API available at: http://localhost:8001"
echo "📊 API Documentation: http://localhost:8001/docs"
echo "💚 Health Check: http://localhost:8001/health"