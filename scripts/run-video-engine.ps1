# scripts/run-video-engine.ps1
"""
AutoPro Video Engine - Startup Script
Starts the FastAPI backend with all required environment variables for video generation.
"""

param(
    [switch]$Dev = $false,
    [string]$Port = "8001",
    [string]$Host = "127.0.0.1"
)

# Set working directory to script location
Set-Location $PSScriptRoot/..

Write-Host "🚀 Starting AutoPro Video Engine..." -ForegroundColor Green

# Check if .env file exists
$envFile = "services/api/.env"
if (-not (Test-Path $envFile)) {
    Write-Warning ".env file not found at $envFile"
    Write-Host "Please copy services/api/env.example to services/api/.env and configure your API keys" -ForegroundColor Yellow
    exit 1
}

# Set environment variables for video engine
$env:USE_INTERNAL_VIDEO_ENGINE = "true"
$env:LIPSYNC_BACKEND = "sadtalker"
$env:VIDEO_ENGINE_FPS = "25"
$env:VIDEO_ENGINE_CANVAS = "1280x720"
$env:VIDEO_ENGINE_PRESET = "medium"
$env:VIDEO_ENGINE_STORAGE = "local"

Write-Host "✅ Video engine environment configured" -ForegroundColor Green

# Check for required dependencies
Write-Host "🔍 Checking dependencies..." -ForegroundColor Blue

# Check if FFmpeg is installed
try {
    $ffmpegVersion = & ffmpeg -version 2>&1 | Select-Object -First 1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ FFmpeg found: $ffmpegVersion" -ForegroundColor Green
    } else {
        Write-Warning "FFmpeg not found. Please install FFmpeg for video processing."
    }
} catch {
    Write-Warning "FFmpeg check failed. Please install FFmpeg for video processing."
}

# Check Python environment
try {
    $pythonVersion = & python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Error "Python not found. Please install Python 3.8+"
    exit 1
}

# Install/update Python dependencies if needed
Write-Host "📦 Ensuring Python dependencies..." -ForegroundColor Blue
try {
    Set-Location "services/api"
    & python -m pip install -r requirements.txt
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Python dependencies installed" -ForegroundColor Green
    } else {
        Write-Warning "Failed to install Python dependencies"
    }
} catch {
    Write-Warning "Failed to install Python dependencies"
} finally {
    Set-Location ../..
}

# Start the backend server
Write-Host "🎬 Starting FastAPI server..." -ForegroundColor Green
try {
    Set-Location "services/api"
    $env:PORT = $Port
    $env:HOST = $Host

    if ($Dev) {
        Write-Host "🔧 Running in development mode..." -ForegroundColor Yellow
        & uvicorn app.main:app --host $Host --port $Port --reload --log-level info
    } else {
        Write-Host "🏭 Running in production mode..." -ForegroundColor Green
        & uvicorn app.main:app --host $Host --port $Port --workers 4 --log-level warning
    }
} catch {
    Write-Error "Failed to start server: $_"
    exit 1
} finally {
    Set-Location ../..
}

Write-Host "✋ Server stopped" -ForegroundColor Yellow