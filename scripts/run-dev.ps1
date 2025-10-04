# ============================================
# FAZA 1.5: AutoPro Daune - Development Run Script
# Conform Plan de implementare AutoPro Daune.pdf
# ============================================

Write-Host "🚀 AutoPro Daune - Starting Development Environment..." -ForegroundColor Green
Write-Host "📋 FAZA 1 - Foundation Fixes" -ForegroundColor Cyan
Write-Host ""

# Check if we're in the right directory
if (!(Test-Path "services/api/app/main.py")) {
    Write-Host "❌ Error: Please run this script from the project root directory" -ForegroundColor Red
    Write-Host "📁 Current directory: $(Get-Location)" -ForegroundColor Gray
    exit 1
}

Write-Host "📁 Project root: $(Get-Location)" -ForegroundColor Gray
Write-Host ""

# Set environment variables for CORS (FAZA 1.1)
Write-Host "🔧 Setting CORS environment variables..." -ForegroundColor Yellow
$env:BACKEND_CORS_ORIGINS = "http://localhost:3006,http://127.0.0.1:3006,http://localhost:3007,http://127.0.0.1:3007,http://localhost:3003,http://127.0.0.1:3003"
Write-Host "   ✅ CORS origins configured for Vite ports 3006/3007" -ForegroundColor Green
Write-Host ""

# Start Backend (FastAPI)
Write-Host "📡 Starting Backend API (FastAPI)..." -ForegroundColor Yellow
$backendProcess = Start-Process powershell -ArgumentList "-NoExit", "-Command", @"
cd '$(Get-Location)\services\api'
Write-Host '🔧 Backend Setup...' -ForegroundColor Cyan

# Create virtual environment if not exists
if (!(Test-Path '.venv')) { 
    Write-Host 'Creating Python virtual environment...' -ForegroundColor Cyan
    python -m venv .venv 
}

# Activate virtual environment
Write-Host 'Activating virtual environment...' -ForegroundColor Cyan
.\.venv\Scripts\Activate.ps1

# Install dependencies
Write-Host 'Installing Python dependencies...' -ForegroundColor Cyan
pip install -r requirements.txt

# Create .env if not exists
if (!(Test-Path '.env')) { 
    Write-Host 'Creating .env file from example...' -ForegroundColor Cyan
    if (Test-Path '.env.backend.example') {
        Copy-Item '.env.backend.example' '.env'
    } else {
        Write-Host 'Warning: .env.backend.example not found' -ForegroundColor Yellow
    }
}

# Set PYTHONPATH
`$env:PYTHONPATH = "backend"

Write-Host '🚀 Starting FastAPI server on port 8001...' -ForegroundColor Green
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
"@ -PassThru

# Wait for backend to start
Write-Host "⏳ Waiting for backend to initialize..." -ForegroundColor Gray
Start-Sleep -Seconds 8

# Test backend health (FAZA 1.2 - /ping endpoint)
Write-Host "🔍 Testing backend health..." -ForegroundColor Yellow
try {
    $healthResponse = Invoke-RestMethod -Uri "http://127.0.0.1:8001/health" -TimeoutSec 10
    Write-Host "   ✅ Backend health check: $($healthResponse.status)" -ForegroundColor Green
    
    # Test /ping endpoint (FAZA 1.2)
    $pingResponse = Invoke-RestMethod -Uri "http://127.0.0.1:8001/ping" -TimeoutSec 5
    Write-Host "   ✅ Ping endpoint: $($pingResponse.status)" -ForegroundColor Green
} catch {
    Write-Host "   ⚠️ Backend health check failed: $($_.Exception.Message)" -ForegroundColor Yellow
    Write-Host "   💡 Backend might still be starting up..." -ForegroundColor Gray
}

Write-Host ""

# Start Frontend (Vite)
Write-Host "🎨 Starting Frontend (Vite)..." -ForegroundColor Yellow
$frontendProcess = Start-Process powershell -ArgumentList "-NoExit", "-Command", @"
cd '$(Get-Location)\02_FRONTEND_UI_CLEAN'
Write-Host '🔧 Frontend Setup...' -ForegroundColor Cyan

# Create .env if not exists
if (!(Test-Path '.env')) { 
    Write-Host 'Creating frontend .env file from example...' -ForegroundColor Cyan
    if (Test-Path '.env.frontend.example') {
        Copy-Item '.env.frontend.example' '.env'
    } else {
        Write-Host 'Warning: .env.frontend.example not found' -ForegroundColor Yellow
    }
}

# Install npm dependencies
Write-Host 'Installing npm dependencies...' -ForegroundColor Cyan
npm install

Write-Host '🚀 Starting Vite development server (port 3006/3007)...' -ForegroundColor Green
npm run dev
"@ -PassThru

# Wait for frontend to start
Write-Host "⏳ Waiting for frontend to initialize..." -ForegroundColor Gray
Start-Sleep -Seconds 5

Write-Host ""
Write-Host "🎉 AutoPro Daune Development Environment Started!" -ForegroundColor Green
Write-Host ""
Write-Host "📱 Access URLs:" -ForegroundColor Cyan
Write-Host "   🌐 Frontend: http://localhost:3006 (or 3007 if 3006 is busy)" -ForegroundColor White
Write-Host "   🔗 Backend:  http://localhost:8001" -ForegroundColor White
Write-Host "   💚 Health:   http://localhost:8001/health" -ForegroundColor White
Write-Host "   🏓 Ping:     http://localhost:8001/ping" -ForegroundColor White
Write-Host "   📊 API Docs: http://localhost:8001/docs" -ForegroundColor White
Write-Host ""
Write-Host "🔧 Process Management:" -ForegroundColor Cyan
Write-Host "   • Backend Process ID: $($backendProcess.Id)" -ForegroundColor White
Write-Host "   • Frontend Process ID: $($frontendProcess.Id)" -ForegroundColor White
Write-Host "   • To stop: Close both PowerShell windows or Ctrl+C" -ForegroundColor White
Write-Host ""
Write-Host "📋 FAZA 1 Status:" -ForegroundColor Cyan
Write-Host "   ✅ CORS configured for Vite (3006/3007)" -ForegroundColor Green
Write-Host "   ✅ /ping endpoint available" -ForegroundColor Green
Write-Host "   ✅ Backend running on port 8001" -ForegroundColor Green
Write-Host "   ✅ Frontend running on dynamic port" -ForegroundColor Green
Write-Host ""
Write-Host "💡 Tips:" -ForegroundColor Cyan
Write-Host "   • Backend auto-reloads on code changes" -ForegroundColor White
Write-Host "   • Frontend hot-reloads on code changes" -ForegroundColor White
Write-Host "   • Check browser console for any errors" -ForegroundColor White
Write-Host "   • Run smoke-test.ps1 to verify everything works" -ForegroundColor White
