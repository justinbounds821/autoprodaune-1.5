Write-Host "🏥 AutoPro Daune - Health Check..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$errors = 0

# Check Backend Health
Write-Host "[1/3] Checking Backend (8001)..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://127.0.0.1:8001/health" -TimeoutSec 5
    if ($response.status -eq "ok") {
        Write-Host "✅ Backend Health: OK" -ForegroundColor Green
    } else {
        Write-Host "❌ Backend Health: FAILED" -ForegroundColor Red
        $errors++
    }
} catch {
    Write-Host "❌ Backend Health: DOWN ($($_.Exception.Message))" -ForegroundColor Red
    $errors++
}

# Check Frontend
Write-Host "[2/3] Checking Frontend (3003)..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:3003" -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Frontend: OK" -ForegroundColor Green
    } else {
        Write-Host "❌ Frontend: FAILED (Status: $($response.StatusCode))" -ForegroundColor Red
        $errors++
    }
} catch {
    Write-Host "❌ Frontend: DOWN ($($_.Exception.Message))" -ForegroundColor Red
    $errors++
}

# Check API Proxy
Write-Host "[3/3] Checking API Proxy..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://127.0.0.1:3003/api/leads" -TimeoutSec 5
    Write-Host "✅ API Proxy: OK" -ForegroundColor Green
} catch {
    Write-Host "❌ API Proxy: FAILED ($($_.Exception.Message))" -ForegroundColor Red
    $errors++
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan

if ($errors -eq 0) {
    Write-Host "🎉 ALL SYSTEMS HEALTHY!" -ForegroundColor Green
    Write-Host "Backend:  http://127.0.0.1:8001" -ForegroundColor White
    Write-Host "Frontend: http://127.0.0.1:3003" -ForegroundColor White
    Write-Host "Admin:    http://127.0.0.1:3003/admin" -ForegroundColor White
    exit 0
} else {
    Write-Host "❌ HEALTH CHECK FAILED ($errors errors)" -ForegroundColor Red
    Write-Host "Run .\scripts\start-all.ps1 to restart services" -ForegroundColor Yellow
    exit 1
}
