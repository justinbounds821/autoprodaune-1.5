Write-Host "🏗️ AutoPro Daune - Building for Production..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Build Frontend
Write-Host "[1/2] Building Frontend..." -ForegroundColor Yellow
Set-Location $PSScriptRoot\..\02_FRONTEND_UI_CLEAN
npm run build

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Frontend build failed!" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Frontend build completed!" -ForegroundColor Green

# Check Backend
Write-Host "[2/2] Checking Backend..." -ForegroundColor Yellow
Set-Location $PSScriptRoot\..\services\api

if (!(Test-Path "requirements.txt")) {
    Write-Host "❌ Backend requirements.txt not found!" -ForegroundColor Red
    exit 1
}

if (!(Test-Path "app\main.py")) {
    Write-Host "❌ Backend main.py not found!" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Backend structure validated!" -ForegroundColor Green

Write-Host ""
Write-Host "🎉 PRODUCTION BUILD COMPLETED!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "📦 Frontend build: 02_FRONTEND_UI_CLEAN\dist\" -ForegroundColor White
Write-Host "🐍 Backend ready:  services\api\" -ForegroundColor White
Write-Host ""
Write-Host "To start production servers:" -ForegroundColor Yellow
Write-Host "  Frontend: npm run preview -- --port 4173" -ForegroundColor White
Write-Host "  Backend:  python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --workers 4" -ForegroundColor White
