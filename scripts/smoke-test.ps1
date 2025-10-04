# ============================================
# FAZA 1.5: AutoPro Daune - Smoke Test Script
# Conform Plan de implementare AutoPro Daune.pdf
# ============================================

Write-Host "🧪 AutoPro Daune - Running Smoke Tests..." -ForegroundColor Green
Write-Host "📋 FAZA 1 - Foundation Validation" -ForegroundColor Cyan
Write-Host ""

# Check if we're in the right directory
if (!(Test-Path "services/api/app/main.py")) {
    Write-Host "❌ Error: Please run this script from the project root directory" -ForegroundColor Red
    Write-Host "📁 Current directory: $(Get-Location)" -ForegroundColor Gray
    exit 1
}

Write-Host "📁 Project root: $(Get-Location)" -ForegroundColor Gray
Write-Host ""

# Test 1: Port Availability Check
Write-Host "🔍 Test 1: Port Availability..." -ForegroundColor Yellow
$ports = @(3006, 3007, 8001)
$listeningPorts = @()

foreach ($port in $ports) {
    $connection = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    if ($connection) {
        $listeningPorts += $port
        Write-Host "   ✅ Port $port is listening" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Port $port is not listening" -ForegroundColor Red
    }
}

if ($listeningPorts.Count -eq 0) {
    Write-Host "   ⚠️ No required ports are listening. Start services first!" -ForegroundColor Yellow
}

Write-Host ""

# Test 2: Backend Health Check (FAZA 1.2)
Write-Host "🔍 Test 2: Backend Health Check..." -ForegroundColor Yellow
try {
    $healthResponse = Invoke-RestMethod -Uri "http://127.0.0.1:8001/health" -TimeoutSec 10
    Write-Host "   ✅ Backend health: $($healthResponse.status)" -ForegroundColor Green
    Write-Host "   📊 Service: $($healthResponse.service)" -ForegroundColor Gray
    Write-Host "   🕒 Timestamp: $($healthResponse.timestamp)" -ForegroundColor Gray
} catch {
    Write-Host "   ❌ Backend health check failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Test 3: Ping Endpoint (FAZA 1.2)
Write-Host "🔍 Test 3: Ping Endpoint..." -ForegroundColor Yellow
try {
    $pingResponse = Invoke-RestMethod -Uri "http://127.0.0.1:8001/ping" -TimeoutSec 5
    Write-Host "   ✅ Ping response: $($pingResponse.status)" -ForegroundColor Green
    Write-Host "   🕒 Timestamp: $($pingResponse.timestamp)" -ForegroundColor Gray
} catch {
    Write-Host "   ❌ Ping endpoint failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Test 4: Frontend Accessibility
Write-Host "🔍 Test 4: Frontend Accessibility..." -ForegroundColor Yellow

# Test port 3006 (Vite default)
try {
    $frontendResponse = Invoke-WebRequest -Uri "http://127.0.0.1:3006" -TimeoutSec 5 -ErrorAction Stop
    if ($frontendResponse.StatusCode -eq 200) {
        Write-Host "   ✅ Frontend accessible on port 3006" -ForegroundColor Green
    }
} catch {
    Write-Host "   ❌ Frontend not accessible on port 3006" -ForegroundColor Red
}

# Test port 3007 (Vite fallback)
try {
    $frontendResponse = Invoke-WebRequest -Uri "http://127.0.0.1:3007" -TimeoutSec 5 -ErrorAction Stop
    if ($frontendResponse.StatusCode -eq 200) {
        Write-Host "   ✅ Frontend accessible on port 3007" -ForegroundColor Green
    }
} catch {
    Write-Host "   ❌ Frontend not accessible on port 3007" -ForegroundColor Red
}

Write-Host ""

# Test 5: API Endpoints
Write-Host "🔍 Test 5: API Endpoints..." -ForegroundColor Yellow

$endpoints = @(
    @{ Path = "/"; Name = "Root" },
    @{ Path = "/health"; Name = "Health Check" },
    @{ Path = "/ping"; Name = "Ping Test" },
    @{ Path = "/docs"; Name = "API Documentation" },
    @{ Path = "/api/dashboard/overview"; Name = "Dashboard Overview" },
    @{ Path = "/api/leads/"; Name = "Leads API" },
    @{ Path = "/api/financial/dashboard"; Name = "Financial Dashboard" }
)

foreach ($endpoint in $endpoints) {
    try {
        $response = Invoke-WebRequest -Uri "http://127.0.0.1:8001$($endpoint.Path)" -TimeoutSec 5 -ErrorAction Stop
        Write-Host "   ✅ $($endpoint.Name) - Status: $($response.StatusCode)" -ForegroundColor Green
    } catch {
        $statusCode = "N/A"
        if ($_.Exception.Response) {
            $statusCode = $_.Exception.Response.StatusCode
        }
        Write-Host "   ❌ $($endpoint.Name) - Error: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host ""

# Test 6: CORS Configuration (FAZA 1.1)
Write-Host "🔍 Test 6: CORS Configuration..." -ForegroundColor Yellow
try {
    # Test CORS preflight request
    $corsHeaders = @{
        'Origin' = 'http://localhost:3006'
        'Access-Control-Request-Method' = 'GET'
        'Access-Control-Request-Headers' = 'Content-Type'
    }
    
    $corsResponse = Invoke-WebRequest -Uri "http://127.0.0.1:8001/health" -Method OPTIONS -Headers $corsHeaders -TimeoutSec 5
    if ($corsResponse.Headers['Access-Control-Allow-Origin']) {
        Write-Host "   ✅ CORS headers present" -ForegroundColor Green
        Write-Host "   🌐 Allowed origins: $($corsResponse.Headers['Access-Control-Allow-Origin'])" -ForegroundColor Gray
    } else {
        Write-Host "   ⚠️ CORS headers not found" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   ❌ CORS test failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Test 7: File Structure Validation
Write-Host "🔍 Test 7: File Structure..." -ForegroundColor Yellow

$requiredFiles = @(
    "services/api/app/main.py",
    "services/api/app/routes/health.py",
    "02_FRONTEND_UI_CLEAN/src/services/autoproApi.ts",
    "scripts/run-dev.ps1",
    "scripts/smoke-test.ps1",
    "database_schema_fixes.sql"
)

foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "   ✅ $file exists" -ForegroundColor Green
    } else {
        Write-Host "   ❌ $file missing" -ForegroundColor Red
    }
}

Write-Host ""

# Test 8: Environment Variables
Write-Host "🔍 Test 8: Environment Variables..." -ForegroundColor Yellow
if ($env:BACKEND_CORS_ORIGINS) {
    Write-Host "   ✅ BACKEND_CORS_ORIGINS is set" -ForegroundColor Green
    Write-Host "   🌐 Value: $($env:BACKEND_CORS_ORIGINS)" -ForegroundColor Gray
} else {
    Write-Host "   ⚠️ BACKEND_CORS_ORIGINS not set" -ForegroundColor Yellow
}

Write-Host ""

# Summary Report
Write-Host "📋 FAZA 1 Smoke Test Summary:" -ForegroundColor Cyan
Write-Host ""
Write-Host "🔧 Foundation Status:" -ForegroundColor Cyan
Write-Host "   • CORS Configuration: $(if ($listeningPorts -contains 8001) { '✅ Ready' } else { '❌ Not Ready' })" -ForegroundColor White
Write-Host "   • Ping Endpoint: $(if ($listeningPorts -contains 8001) { '✅ Available' } else { '❌ Not Available' })" -ForegroundColor White
Write-Host "   • Backend Health: $(if ($listeningPorts -contains 8001) { '✅ Running' } else { '❌ Not Running' })" -ForegroundColor White
Write-Host "   • Frontend Access: $(if ($listeningPorts -contains 3006 -or $listeningPorts -contains 3007) { '✅ Available' } else { '❌ Not Available' })" -ForegroundColor White
Write-Host ""
Write-Host "📱 Service URLs:" -ForegroundColor Cyan
Write-Host "   • Backend: http://localhost:8001" -ForegroundColor White
Write-Host "   • Frontend: http://localhost:3006 or http://localhost:3007" -ForegroundColor White
Write-Host "   • Health: http://localhost:8001/health" -ForegroundColor White
Write-Host "   • Ping: http://localhost:8001/ping" -ForegroundColor White
Write-Host "   • API Docs: http://localhost:8001/docs" -ForegroundColor White
Write-Host ""

if ($listeningPorts.Count -ge 2) {
    Write-Host "🎉 FAZA 1 Foundation Tests PASSED!" -ForegroundColor Green
    Write-Host "🚀 Ready to proceed with FAZA 2 - Core Business" -ForegroundColor Green
} else {
    Write-Host "⚠️ Some tests failed. Please check the issues above." -ForegroundColor Yellow
    Write-Host "💡 Run '.\scripts\run-dev.ps1' to start services" -ForegroundColor Cyan
}

Write-Host ""
