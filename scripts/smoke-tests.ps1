# AutoPro Daune - Smoke Tests Script
Write-Host "🧪 Running AutoPro Daune Smoke Tests..." -ForegroundColor Green

# Check if we're in the right directory
if (!(Test-Path "services/api/app/main.py")) {
    Write-Host "❌ Error: Please run this script from the project root directory" -ForegroundColor Red
    exit 1
}

Write-Host "📁 Current directory: $(Get-Location)" -ForegroundColor Gray
Write-Host ""

# Test 1: Check if ports are listening
Write-Host "🔍 Test 1: Checking if required ports are listening..." -ForegroundColor Yellow
$ports = @(3000, 8001, 4173)
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

Write-Host ""

# Test 2: Backend Health Check
Write-Host "🔍 Test 2: Backend Health Check..." -ForegroundColor Yellow
try {
    $healthResponse = Invoke-RestMethod -Uri "http://127.0.0.1:8001/health" -TimeoutSec 10
    Write-Host "   ✅ Backend is healthy: $($healthResponse.status)" -ForegroundColor Green
    Write-Host "   📊 Service: $($healthResponse.service)" -ForegroundColor Gray
    Write-Host "   🔌 Port: $($healthResponse.port)" -ForegroundColor Gray
} catch {
    Write-Host "   ❌ Backend health check failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Test 3: Backend Metrics
Write-Host "🔍 Test 3: Backend Metrics Endpoint..." -ForegroundColor Yellow
try {
    $metricsResponse = Invoke-WebRequest -Uri "http://127.0.0.1:8001/metrics" -TimeoutSec 10
    if ($metricsResponse.StatusCode -eq 200) {
        Write-Host "   ✅ Metrics endpoint is accessible" -ForegroundColor Green
        
        # Check for specific metrics
        $metrics = $metricsResponse.Content
        if ($metrics -match "http_requests_total") {
            Write-Host "   📈 HTTP requests metric found" -ForegroundColor Green
        } else {
            Write-Host "   ⚠️ HTTP requests metric not found" -ForegroundColor Yellow
        }
    } else {
        Write-Host "   ❌ Metrics endpoint returned status: $($metricsResponse.StatusCode)" -ForegroundColor Red
    }
} catch {
    Write-Host "   ❌ Metrics endpoint failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Test 4: Frontend Accessibility
Write-Host "🔍 Test 4: Frontend Accessibility..." -ForegroundColor Yellow

# Test dev server (port 3000)
try {
    $frontendResponse = Invoke-WebRequest -Uri "http://127.0.0.1:3000" -TimeoutSec 5 -ErrorAction Stop
    if ($frontendResponse.StatusCode -eq 200) {
        Write-Host "   ✅ Frontend dev server is accessible on port 3000" -ForegroundColor Green
    }
} catch {
    Write-Host "   ❌ Frontend dev server not accessible on port 3000" -ForegroundColor Red
}

# Test preview server (port 4173)
try {
    $previewResponse = Invoke-WebRequest -Uri "http://127.0.0.1:4173" -TimeoutSec 5 -ErrorAction Stop
    if ($previewResponse.StatusCode -eq 200) {
        Write-Host "   ✅ Frontend preview server is accessible on port 4173" -ForegroundColor Green
    }
} catch {
    Write-Host "   ❌ Frontend preview server not accessible on port 4173" -ForegroundColor Red
}

Write-Host ""

# Test 5: API Endpoints
Write-Host "🔍 Test 5: Testing API Endpoints..." -ForegroundColor Yellow

$endpoints = @(
    @{ Path = "/"; Name = "Root" },
    @{ Path = "/health"; Name = "Health" },
    @{ Path = "/metrics"; Name = "Metrics" },
    @{ Path = "/api/leads/"; Name = "Leads API" },
    @{ Path = "/api/financial/dashboard"; Name = "Financial Dashboard" }
)

foreach ($endpoint in $endpoints) {
    try {
        $response = Invoke-WebRequest -Uri "http://127.0.0.1:8001$($endpoint.Path)" -TimeoutSec 5 -ErrorAction Stop
        Write-Host "   ✅ $($endpoint.Name) ($($endpoint.Path)) - Status: $($response.StatusCode)" -ForegroundColor Green
    } catch {
        $statusCode = "N/A"
        if ($_.Exception.Response) {
            $statusCode = $_.Exception.Response.StatusCode
        }
        Write-Host "   ❌ $($endpoint.Name) ($($endpoint.Path)) - Error: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host ""

# Test 6: Build Status
Write-Host "🔍 Test 6: Checking Frontend Build..." -ForegroundColor Yellow
if (Test-Path "02_FRONTEND_UI_CLEAN/dist") {
    $distFiles = Get-ChildItem "02_FRONTEND_UI_CLEAN/dist" -Recurse
    Write-Host "   ✅ Frontend build exists with $($distFiles.Count) files" -ForegroundColor Green
    
    if (Test-Path "02_FRONTEND_UI_CLEAN/dist/index.html") {
        Write-Host "   ✅ index.html found" -ForegroundColor Green
    } else {
        Write-Host "   ❌ index.html not found" -ForegroundColor Red
    }
} else {
    Write-Host "   ❌ Frontend build directory not found" -ForegroundColor Red
}

Write-Host ""

# Summary
Write-Host "📋 Test Summary:" -ForegroundColor Cyan
Write-Host "   🔌 Listening ports: $($listeningPorts -join ', ')" -ForegroundColor White
Write-Host "   📡 Backend: http://127.0.0.1:8001" -ForegroundColor White
Write-Host "   🎨 Frontend: http://127.0.0.1:3000 (dev) | http://127.0.0.1:4173 (preview)" -ForegroundColor White
Write-Host "   📊 Health: http://127.0.0.1:8001/health" -ForegroundColor White
Write-Host "   📈 Metrics: http://127.0.0.1:8001/metrics" -ForegroundColor White

Write-Host ""
Write-Host "🎉 Smoke tests completed!" -ForegroundColor Green
