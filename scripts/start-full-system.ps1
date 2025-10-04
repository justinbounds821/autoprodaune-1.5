# ==============================
# AutoPro Daune - Full System Startup
# ==============================

Write-Host "🚀 Starting AutoPro Daune full system (Backend + Frontend)..." -ForegroundColor Green

# Setează variabilele de mediu
$env:PYTHONPATH = (Get-Location).Path
$env:BACKEND_CORS_ORIGINS = "http://localhost:3005,http://127.0.0.1:3005,http://localhost:3000,http://127.0.0.1:3000"

Write-Host "📡 Starting Backend on port 8001..." -ForegroundColor Cyan

# Pornește backend (port 8001) - din services/api cu cheile Supabase
$backendCmd = @"
cd .\services\api
`$env:SUPABASE_URL = 'https://orctxxpyiqzbordibqxi.supabase.co'
`$env:SUPABASE_SERVICE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9yY3R4eHB5aXF6Ym9yZGlicXhpIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NzkzMTkxNSwiZXhwIjoyMDczNTA3OTE1fQ.mqpjr7frHPqtQqLoZJiO-8e5KOP_yeX_AvCoEGbnYGY'
`$env:SUPABASE_SERVICE_ROLE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9yY3R4eHB5aXF6Ym9yZGlicXhpIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NzkzMTkxNSwiZXhwIjoyMDczNTA3OTE1fQ.mqpjr7frHPqtQqLoZJiO-8e5KOP_yeX_AvCoEGbnYGY'
`$env:BACKEND_CORS_ORIGINS = 'http://localhost:3006,http://127.0.0.1:3006,http://localhost:3005,http://127.0.0.1:3005,http://localhost:3000,http://127.0.0.1:3000'
python -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload --log-level debug
"@

Start-Process powershell -ArgumentList '-NoExit','-Command',$backendCmd

Start-Sleep -Seconds 3

Write-Host "🌐 Starting Frontend on port 3005..." -ForegroundColor Cyan

# Pornește frontend (port 3005) - cu npx vite direct
$frontendCmd = @"
cd .\02_FRONTEND_UI_CLEAN
`$env:VITE_API_BASE_URL = 'http://127.0.0.1:8001'
if(Test-Path package-lock.json){npm ci}else{npm install}
npx vite --port 3006 --host
"@

Start-Process powershell -ArgumentList '-NoExit','-Command',$frontendCmd

Start-Sleep -Seconds 2

Write-Host "🎬 Opening Admin Dashboard - Video Management..." -ForegroundColor Yellow

# Deschide Admin Dashboard direct pe Video Management
Start-Process "http://localhost:3006/admin/videos"

Write-Host "✅ AutoPro Daune started! Backend 8001 + Frontend 3006" -ForegroundColor Green
Write-Host "📋 Quick Health Checks (run in new terminal):" -ForegroundColor Magenta
Write-Host "   curl.exe http://127.0.0.1:8001/health" -ForegroundColor Gray
Write-Host "   curl.exe http://127.0.0.1:3006" -ForegroundColor Gray
Write-Host "   curl.exe http://127.0.0.1:3005/api/leads" -ForegroundColor Gray
