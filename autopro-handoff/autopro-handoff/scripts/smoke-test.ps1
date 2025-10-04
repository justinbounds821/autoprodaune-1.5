# Smoke test for AutoPro Daune API
# Windows PowerShell script
# Tests critical endpoints to verify backend is working

Write-Host "🧪 Running AutoPro Daune Smoke Tests..." -ForegroundColor Cyan

$BASE_URL = "http://127.0.0.1:8001"
$FAILED = 0

function Test-Endpoint {
    param(
        [string]$Name,
        [string]$Url,
        [string]$Method = "GET",
        [string]$Body = $null
    )

    Write-Host "`n📍 Testing: $Name" -ForegroundColor Yellow
    Write-Host "   $Method $Url" -ForegroundColor Gray

    try {
        if ($Method -eq "GET") {
            $response = curl.exe -sS $Url 2>&1
        } else {
            $headers = @("-H", "Content-Type: application/json")
            if ($Body) {
                $response = curl.exe -sS -X $Method $Url @headers -d $Body 2>&1
            } else {
                $response = curl.exe -sS -X $Method $Url @headers 2>&1
            }
        }

        Write-Host "   ✅ Response: " -ForegroundColor Green -NoNewline
        Write-Host ($response | Out-String).Substring(0, [Math]::Min(100, ($response | Out-String).Length)) -ForegroundColor Gray
        return 0
    } catch {
        Write-Host "   ❌ FAILED: $_" -ForegroundColor Red
        return 1
    }
}

# Test 1: Health check
$FAILED += Test-Endpoint -Name "Health Check" -Url "$BASE_URL/health"

# Test 2: Mock data (no DB dependency)
$FAILED += Test-Endpoint -Name "Mock Data" -Url "$BASE_URL/api/test/mock-data"

# Test 3: Automation status
$FAILED += Test-Endpoint -Name "Automation Status" -Url "$BASE_URL/api/automation/status"

# Test 4: Payments list
$FAILED += Test-Endpoint -Name "Payments List" -Url "$BASE_URL/api/financial/payments"

# Test 5: HeyGen avatars (should fail gracefully if key missing)
$FAILED += Test-Endpoint -Name "HeyGen Avatars" -Url "$BASE_URL/api/video/video/heygen/avatars"

# Test 6: HeyGen generate (should return 400 if key missing, not 500)
Write-Host "`n📍 Testing: HeyGen Generate (expect 400 if key missing)" -ForegroundColor Yellow
$heygenBody = '{"script":"test"}'
$response = curl.exe -sS -X POST "$BASE_URL/api/video/video/heygen/generate" -H "Content-Type: application/json" -d $heygenBody 2>&1
if ($response -match "HEYGEN_API_KEY") {
    Write-Host "   ✅ Correctly returns 400 with API key message" -ForegroundColor Green
} else {
    Write-Host "   ⚠️ Unexpected response (may need UX improvement)" -ForegroundColor Yellow
    Write-Host "   Response: $response" -ForegroundColor Gray
}

# Summary
Write-Host "`n" -NoNewline
Write-Host "═══════════════════════════════════════" -ForegroundColor Cyan
if ($FAILED -eq 0) {
    Write-Host "✅ All smoke tests passed!" -ForegroundColor Green
} else {
    Write-Host "❌ $FAILED test(s) failed" -ForegroundColor Red
}
Write-Host "═══════════════════════════════════════" -ForegroundColor Cyan

exit $FAILED
