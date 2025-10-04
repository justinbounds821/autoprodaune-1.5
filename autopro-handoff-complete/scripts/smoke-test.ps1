# AutoPro Daune - Smoke Test Script
# Tests critical endpoints to validate system functionality

Write-Host "🧪 AutoPro Daune - Smoke Test" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

$baseUrl = "http://127.0.0.1:8001"
$frontendUrl = "http://127.0.0.1:3007"

# Test 1: Health Check
Write-Host "`n1. Testing Health Check..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/health" -Method GET
    Write-Host "✅ Health Check: $($response.status)" -ForegroundColor Green
} catch {
    Write-Host "❌ Health Check Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 2: Automation Status
Write-Host "`n2. Testing Automation Status..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/automation/status" -Method GET
    Write-Host "✅ Automation Status: OK" -ForegroundColor Green
} catch {
    Write-Host "❌ Automation Status Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 3: Leads API
Write-Host "`n3. Testing Leads API..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/leads/" -Method GET
    Write-Host "✅ Leads API: OK" -ForegroundColor Green
} catch {
    Write-Host "❌ Leads API Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 4: HeyGen Avatars
Write-Host "`n4. Testing HeyGen Avatars..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/video/video/heygen/avatars" -Method GET
    Write-Host "✅ HeyGen Avatars: OK" -ForegroundColor Green
} catch {
    Write-Host "❌ HeyGen Avatars Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 5: HeyGen Generate (Expected to fail with API key error)
Write-Host "`n5. Testing HeyGen Generate..." -ForegroundColor Yellow
try {
    $form = @{
        script = "Test script"
        quality = "high"
        style = "realistic"
    }
    $response = Invoke-RestMethod -Uri "$baseUrl/api/video/video/heygen/generate" -Method POST -Form $form
    Write-Host "✅ HeyGen Generate: OK" -ForegroundColor Green
} catch {
    if ($_.Exception.Message -like "*API key*" -or $_.Exception.Message -like "*401*") {
        Write-Host "⚠️ HeyGen Generate: API Key not configured (expected)" -ForegroundColor Yellow
    } else {
        Write-Host "❌ HeyGen Generate Failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Test 6: Financial Dashboard
Write-Host "`n6. Testing Financial Dashboard..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/financial/dashboard" -Method GET
    Write-Host "✅ Financial Dashboard: OK" -ForegroundColor Green
} catch {
    Write-Host "❌ Financial Dashboard Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 7: Frontend Health
Write-Host "`n7. Testing Frontend Health..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$frontendUrl" -Method GET -TimeoutSec 10
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Frontend: OK" -ForegroundColor Green
    } else {
        Write-Host "❌ Frontend: HTTP $($response.StatusCode)" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Frontend Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 8: API Proxy (Frontend -> Backend)
Write-Host "`n8. Testing API Proxy..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$frontendUrl/api/leads/" -Method GET
    Write-Host "✅ API Proxy: OK" -ForegroundColor Green
} catch {
    Write-Host "❌ API Proxy Failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n🎯 Smoke Test Complete!" -ForegroundColor Cyan
Write-Host "Check results above for any ❌ failures" -ForegroundColor Cyan
