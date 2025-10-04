# Start AutoPro Daune Backend (FastAPI + Uvicorn)
# Windows PowerShell script

Write-Host "🚀 Starting AutoPro Daune Backend..." -ForegroundColor Cyan

# Set environment variables (override if needed)
$env:BACKEND_CORS_ORIGINS = "http://localhost:3006,http://127.0.0.1:3006,http://localhost:3007,http://127.0.0.1:3007"
$env:REDIS_URL = "disabled"
$env:RATE_LIMIT_MODE = "memory"
$env:LOG_LEVEL = "DEBUG"
$env:ENVIRONMENT = "development"

# Optional: load .env file if exists
if (Test-Path "services\api\.env") {
    Write-Host "✅ Loading .env from services\api\.env" -ForegroundColor Green
    Get-Content "services\api\.env" | ForEach-Object {
        if ($_ -match '^\s*([^#][^=]*)\s*=\s*(.*)$') {
            $name = $matches[1].Trim()
            $value = $matches[2].Trim()
            Set-Item -Path "env:$name" -Value $value
        }
    }
}

# Navigate to backend directory
Set-Location -Path "services\api"

# Start uvicorn
Write-Host "🔧 Starting uvicorn on http://127.0.0.1:8001 ..." -ForegroundColor Yellow
python -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload
