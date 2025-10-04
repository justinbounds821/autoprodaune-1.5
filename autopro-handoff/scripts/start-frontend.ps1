# Start AutoPro Daune Frontend (Vite dev server)
# Windows PowerShell script

Write-Host "🚀 Starting AutoPro Daune Frontend..." -ForegroundColor Cyan

# Navigate to frontend directory
Set-Location -Path "02_FRONTEND_UI_CLEAN"

# Check if node_modules exists
if (-Not (Test-Path "node_modules")) {
    Write-Host "⚠️ node_modules not found. Running npm install..." -ForegroundColor Yellow
    npm install
}

# Start Vite dev server
Write-Host "🔧 Starting Vite dev server..." -ForegroundColor Yellow
Write-Host "Frontend will be available at: http://localhost:3006" -ForegroundColor Green
npm run dev
