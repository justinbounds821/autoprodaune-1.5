# AutoPro Daune - Development Start Script
Write-Host "🚀 Starting AutoPro Daune Development Environment..." -ForegroundColor Green

# Check if we're in the right directory
if (!(Test-Path "services/api/app/main.py")) {
    Write-Host "❌ Error: Please run this script from the project root directory" -ForegroundColor Red
    exit 1
}

Write-Host "📁 Current directory: $(Get-Location)" -ForegroundColor Gray

# Start Backend
Write-Host "📡 Starting Backend API..." -ForegroundColor Yellow
$backendProcess = Start-Process powershell -ArgumentList "-NoExit", "-Command", @"
cd '$(Get-Location)\services\api'
if (!(Test-Path '.venv')) { 
    Write-Host 'Creating Python virtual environment...' -ForegroundColor Cyan
    python -m venv .venv 
}
Write-Host 'Activating virtual environment...' -ForegroundColor Cyan
.\.venv\Scripts\Activate.ps1
Write-Host 'Installing dependencies...' -ForegroundColor Cyan
pip install -r requirements.txt
if (!(Test-Path '.env')) { 
    Write-Host 'Creating .env file from example...' -ForegroundColor Cyan
    Copy-Item '.env.backend.example' '.env' 
}
Write-Host 'Starting FastAPI server on port 8001...' -ForegroundColor Green
uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload
"@ -PassThru

# Wait 5 seconds for backend to start
Write-Host "⏳ Waiting for backend to initialize..." -ForegroundColor Gray
Start-Sleep -Seconds 5

# Test backend health
try {
    $healthResponse = Invoke-RestMethod -Uri "http://127.0.0.1:8001/health" -TimeoutSec 5
    Write-Host "✅ Backend health check passed: $($healthResponse.status)" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Backend health check failed, but continuing..." -ForegroundColor Yellow
}

# Start Frontend
Write-Host "🎨 Starting Frontend..." -ForegroundColor Yellow
$frontendProcess = Start-Process powershell -ArgumentList "-NoExit", "-Command", @"
cd '$(Get-Location)\02_FRONTEND_UI_CLEAN'
if (!(Test-Path '.env')) { 
    Write-Host 'Creating frontend .env file from example...' -ForegroundColor Cyan
    Copy-Item '.env.frontend.example' '.env' 
}
Write-Host 'Installing npm dependencies...' -ForegroundColor Cyan
npm install
Write-Host 'Starting Vite development server on port 3000...' -ForegroundColor Green
npm run dev
"@ -PassThru

# Wait 3 seconds for frontend to start
Write-Host "⏳ Waiting for frontend to initialize..." -ForegroundColor Gray
Start-Sleep -Seconds 3

Write-Host ""
Write-Host "🎉 Development environment started successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "📱 Access URLs:" -ForegroundColor Cyan
Write-Host "   🌐 Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "   🔗 Backend:  http://localhost:8001" -ForegroundColor White
Write-Host "   📊 Health:   http://localhost:8001/health" -ForegroundColor White
Write-Host "   📈 Metrics:  http://localhost:8001/metrics" -ForegroundColor White
Write-Host ""
Write-Host "🔧 Management:" -ForegroundColor Cyan
Write-Host "   • Backend Process ID: $($backendProcess.Id)" -ForegroundColor White
Write-Host "   • Frontend Process ID: $($frontendProcess.Id)" -ForegroundColor White
Write-Host "   • To stop: Close both PowerShell windows or Ctrl+C" -ForegroundColor White
Write-Host ""
Write-Host "Tips:" -ForegroundColor Cyan
Write-Host "   • Backend auto-reloads on code changes" -ForegroundColor White
Write-Host "   • Frontend hot-reloads on code changes" -ForegroundColor White
Write-Host "   • Check browser console for any errors" -ForegroundColor White
