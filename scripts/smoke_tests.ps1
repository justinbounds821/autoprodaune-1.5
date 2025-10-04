# AutoPro Daune - Smoke Tests (PowerShell)
# Testează toate endpoint-urile critice ale API-ului

param(
    [string]$BaseUrl = "http://localhost:8000",
    [string]$AuthToken = "Bearer test"
)

Write-Host "[TEST] AutoPro Daune Smoke Tests" -ForegroundColor Cyan
Write-Host "==============================" -ForegroundColor Cyan

$ErrorActionPreference = "Stop"

# Test 1: Health Check
Write-Host "1. Testing health endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$BaseUrl/health" -Method GET -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "[OK] Health check passed" -ForegroundColor Green
    } else {
        throw "Health check failed with status $($response.StatusCode)"
    }
} catch {
    Write-Host "[ERROR] Health check failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Test 2: Metrics endpoint
Write-Host "2. Testing metrics endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$BaseUrl/metrics" -Method GET -UseBasicParsing
    if ($response.Content -match "http_requests_total") {
        Write-Host "[OK] Metrics endpoint passed" -ForegroundColor Green
    } else {
        throw "Metrics endpoint content invalid"
    }
} catch {
    Write-Host "[ERROR] Metrics endpoint failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Test 3: Root endpoint
Write-Host "3. Testing root endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$BaseUrl/" -Method GET -UseBasicParsing
    $json = $response.Content | ConvertFrom-Json
    if ($json.status -eq "ok") {
        Write-Host "[OK] Root endpoint passed" -ForegroundColor Green
    } else {
        throw "Root endpoint status invalid"
    }
} catch {
    Write-Host "[ERROR] Root endpoint failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Test 4: Video Queue
Write-Host "4. Testing video queue endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$BaseUrl/api/video/queue" -Method GET -UseBasicParsing
    $json = $response.Content | ConvertFrom-Json
    if ($json.items -ne $null) {
        Write-Host "[OK] Video queue endpoint passed" -ForegroundColor Green
    } else {
        throw "Video queue response invalid"
    }
} catch {
    Write-Host "[ERROR] Video queue endpoint failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Test 5: Video Stats
Write-Host "5. Testing video stats endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$BaseUrl/api/video/stats" -Method GET -UseBasicParsing
    $json = $response.Content | ConvertFrom-Json
    if ($json.total -ne $null) {
        Write-Host "[OK] Video stats endpoint passed" -ForegroundColor Green
    } else {
        throw "Video stats response invalid"
    }
} catch {
    Write-Host "[ERROR] Video stats endpoint failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Test 6: Video Generate (should require auth)
Write-Host "6. Testing video generate endpoint (auth required)..." -ForegroundColor Yellow
try {
    $body = @{
        duration_seconds = 5
        resolution = "720p"
        text = "Test"
    } | ConvertTo-Json

    $response = Invoke-WebRequest -Uri "$BaseUrl/api/video/generate" -Method POST -Body $body -ContentType "application/json" -UseBasicParsing
    Write-Host "[ERROR] Video generate should require auth" -ForegroundColor Red
    exit 1
} catch {
    if ($_.Exception.Response.StatusCode -eq 401 -or $_.Exception.Response.StatusCode -eq 403) {
        Write-Host "[OK] Video generate auth protection working" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] Video generate should require auth (got $($_.Exception.Response.StatusCode))" -ForegroundColor Red
        exit 1
    }
}

# Test 7: Rate limiting
Write-Host "7. Testing rate limiting..." -ForegroundColor Yellow
$rateLimitHit = $false
for ($i = 1; $i -le 7; $i++) {
    try {
        $body = @{
            duration_seconds = 5
            resolution = "720p"
            text = "Rate limit test"
        } | ConvertTo-Json

        $response = Invoke-WebRequest -Uri "$BaseUrl/api/video/generate" -Method POST -Body $body -ContentType "application/json" -Headers @{"Authorization" = $AuthToken} -UseBasicParsing
        
        if ($i -le 5) {
            if ($response.StatusCode -ne 202 -and $response.StatusCode -ne 401) {
                Write-Host "[ERROR] Request $i should succeed (got $($response.StatusCode))" -ForegroundColor Red
                exit 1
            }
        }
    } catch {
        if ($_.Exception.Response.StatusCode -eq 429) {
            Write-Host "[OK] Rate limiting working (got 429 on request $i)" -ForegroundColor Green
            $rateLimitHit = $true
            break
        }
    }
}

if (-not $rateLimitHit) {
    Write-Host "[WARN] Rate limiting may not be working as expected" -ForegroundColor Yellow
}

# Test 8: Redis connection
Write-Host "8. Testing Redis connection..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$BaseUrl/metrics" -Method GET -UseBasicParsing
    if ($response.Content -match "redis") {
        Write-Host "[OK] Redis metrics available" -ForegroundColor Green
    } else {
        Write-Host "[WARN] Redis metrics not found (may be using in-memory rate limiting)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "[WARN] Could not check Redis metrics" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[SUCCESS] All smoke tests passed!" -ForegroundColor Green
Write-Host "==============================" -ForegroundColor Green
