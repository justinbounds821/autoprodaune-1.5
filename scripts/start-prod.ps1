# AutoPro Daune - Production Start Script
Write-Host "🚀 Starting AutoPro Daune Production Environment..." -ForegroundColor Green

# Check if we're in the right directory
if (!(Test-Path "services/api/app/main.py")) {
    Write-Host "❌ Error: Please run this script from the project root directory" -ForegroundColor Red
    exit 1
}

Write-Host "📁 Current directory: $(Get-Location)" -ForegroundColor Gray

# Build Frontend
Write-Host "🔨 Building Frontend for Production..." -ForegroundColor Yellow
Set-Location "02_FRONTEND_UI_CLEAN"

if (!(Test-Path ".env")) { 
    Write-Host "Creating production .env file..." -ForegroundColor Cyan
    Copy-Item ".env.frontend.example" ".env"
}

Write-Host "Installing npm dependencies..." -ForegroundColor Cyan
npm install

Write-Host "Building frontend (this may take a few minutes)..." -ForegroundColor Cyan
npm run build

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Frontend build failed!" -ForegroundColor Red
    Set-Location ".."
    exit 1
}

Write-Host "✅ Frontend build completed successfully!" -ForegroundColor Green

# Go back to root
Set-Location ".."

# Start Backend (Production)
Write-Host "📡 Starting Backend API (Production Mode)..." -ForegroundColor Yellow
Set-Location "services/api"

if (!(Test-Path ".venv")) { 
    Write-Host "Creating Python virtual environment..." -ForegroundColor Cyan
    python -m venv .venv 
}

Write-Host "Activating virtual environment..." -ForegroundColor Cyan
.\.venv\Scripts\Activate.ps1

Write-Host "Installing dependencies..." -ForegroundColor Cyan
pip install -r requirements.txt

if (!(Test-Path ".env")) { 
    Write-Host "Creating production .env file..." -ForegroundColor Cyan
    Copy-Item ".env.backend.example" ".env"
}

Write-Host "Starting FastAPI server in production mode (4 workers)..." -ForegroundColor Green
Write-Host "⚠️  Note: This will run in foreground. Use Ctrl+C to stop." -ForegroundColor Yellow

# Production command with multiple workers
uvicorn app.main:app --host 0.0.0.0 --port 8001 --workers 4

# Go back to root
Set-Location ".."
