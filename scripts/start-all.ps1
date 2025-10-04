Write-Host "🚀 AutoPro Daune - Starting Full System..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Start Backend
Write-Host "[1/2] Starting Backend..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit","-Command","& '$PSScriptRoot\start-backend.ps1' 8001"

# Wait a moment
Start-Sleep -Seconds 3

# Start Frontend  
Write-Host "[2/2] Starting Frontend..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit","-Command","& '$PSScriptRoot\start-frontend.ps1'"

Start-Sleep -Seconds 2

Write-Host ""
Write-Host "✅ SYSTEM STARTED!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "📡 Backend:  http://localhost:8001" -ForegroundColor White
Write-Host "🌐 Frontend: http://localhost:3003" -ForegroundColor White
Write-Host "📚 API Docs: http://localhost:8001/docs" -ForegroundColor White
Write-Host "🔐 Admin:    http://localhost:3003/admin" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C in each window to stop the servers" -ForegroundColor Yellow