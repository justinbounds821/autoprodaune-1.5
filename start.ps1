# ============================================
# AutoPro Daune - Startup Script
# ============================================
# Porneste backend si frontend intr-o singura comanda

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🚀 AUTOPRO DAUNE - STARTING SYSTEM" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if running in the right directory
if (!(Test-Path "services\api") -or !(Test-Path "02_FRONTEND_UI_CLEAN")) {
    Write-Host "❌ ERROR: Run this script from the autoprodaune-1 root directory!" -ForegroundColor Red
    Write-Host "Current location: $PWD" -ForegroundColor Yellow
    exit 1
}

# ============================================
# 1. START BACKEND (FastAPI)
# ============================================
Write-Host "[1/2] Starting Backend (FastAPI on port 8001)..." -ForegroundColor Yellow

Start-Process powershell -ArgumentList @"
    -NoExit
    -Command
    `$Host.UI.RawUI.WindowTitle = 'AutoPro Daune - Backend';
    cd '$PWD\services\api';
    Write-Host '🔧 Installing Python dependencies...' -ForegroundColor Cyan;
    pip install -q -r requirements.txt;
    Write-Host '';
    Write-Host '✅ Backend starting on http://localhost:8001' -ForegroundColor Green;
    Write-Host '📚 API Docs: http://localhost:8001/docs' -ForegroundColor Green;
    Write-Host '';
    python -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload
"@

Start-Sleep -Seconds 3

# ============================================
# 2. START FRONTEND (React + Vite)
# ============================================
Write-Host "[2/2] Starting Frontend (React on port 3003)..." -ForegroundColor Yellow

Start-Process powershell -ArgumentList @"
    -NoExit
    -Command
    `$Host.UI.RawUI.WindowTitle = 'AutoPro Daune - Frontend';
    cd '$PWD\02_FRONTEND_UI_CLEAN';
    Write-Host '🔧 Installing Node dependencies...' -ForegroundColor Cyan;
    npm install --silent;
    Write-Host '';
    Write-Host '✅ Frontend starting on http://localhost:3003' -ForegroundColor Green;
    Write-Host '';
    npm run dev
"@

Start-Sleep -Seconds 2

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "✅ AUTOPRO DAUNE SYSTEM STARTED!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "📡 Backend:  http://localhost:8001" -ForegroundColor White
Write-Host "🌐 Frontend: http://localhost:3003" -ForegroundColor White
Write-Host "📚 API Docs: http://localhost:8001/docs" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C in each window to stop the servers" -ForegroundColor Yellow
Write-Host ""