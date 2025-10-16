# ========================================
# MCP Integration Tests
# Testează toate endpoint-urile și integrările
# ========================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  MCP INTEGRATION TESTS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$testsPassed = 0
$testsFailed = 0

function Test-Endpoint {
    param(
        [string]$Name,
        [string]$Url,
        [string]$Method = "GET",
        [object]$Body = $null
    )
    
    Write-Host "Testing: $Name" -ForegroundColor Yellow -NoNewline
    
    try {
        $params = @{
            Uri = $Url
            Method = $Method
            UseBasicParsing = $true
            TimeoutSec = 10
        }
        
        if ($Body) {
            $params.Body = ($Body | ConvertTo-Json -Depth 10)
            $params.ContentType = "application/json"
        }
        
        $response = Invoke-WebRequest @params
        
        if ($response.StatusCode -eq 200 -or $response.StatusCode -eq 201) {
            Write-Host " ✅ PASS" -ForegroundColor Green
            $script:testsPassed++
            return $true
        } else {
            Write-Host " ❌ FAIL (Status: $($response.StatusCode))" -ForegroundColor Red
            $script:testsFailed++
            return $false
        }
    } catch {
        Write-Host " ❌ FAIL ($($_.Exception.Message))" -ForegroundColor Red
        $script:testsFailed++
        return $false
    }
}

# Test 1: Orchestrator Health
Write-Host "[1/8] Orchestrator Health Check" -ForegroundColor Cyan
Test-Endpoint -Name "Orchestrator /health" -Url "http://127.0.0.1:3030/health"
Write-Host ""

# Test 2: MCP Server Health
Write-Host "[2/8] MCP Server Health Check" -ForegroundColor Cyan
Test-Endpoint -Name "MCP Server /health" -Url "http://127.0.0.1:8012/health"
Write-Host ""

# Test 3: OpenAPI Spec
Write-Host "[3/8] OpenAPI Specification" -ForegroundColor Cyan
Test-Endpoint -Name "OpenAPI JSON" -Url "http://127.0.0.1:8012/openapi.json"
Write-Host ""

# Test 4: Workflow Orchestration
Write-Host "[4/8] Workflow Orchestration" -ForegroundColor Cyan
$workflowPayload = @{
    command = "Test workflow"
    context = @{
        project = "AutoPro"
        branch = "main"
    }
    options = @{
        create_linear_tasks = $false
        create_github_issues = $false
    }
}
Test-Endpoint -Name "POST /mcp/workflows/orchestrate" -Url "http://127.0.0.1:8012/mcp/workflows/orchestrate" -Method "POST" -Body $workflowPayload
Write-Host ""

# Test 5: GPT Orchestrate Endpoint
Write-Host "[5/8] GPT Developer Mode Endpoints" -ForegroundColor Cyan
Test-Endpoint -Name "POST /mcp/tools/gpt/orchestrate" -Url "http://127.0.0.1:8012/mcp/tools/gpt/orchestrate" -Method "POST" -Body $workflowPayload
Write-Host ""

# Test 6: GPT System Status
Write-Host "[6/8] GPT System Status" -ForegroundColor Cyan
Test-Endpoint -Name "GET /mcp/tools/gpt/status" -Url "http://127.0.0.1:8012/mcp/tools/gpt/status"
Write-Host ""

# Test 7: System Health Check (via Orchestrator)
Write-Host "[7/8] System Health Check (Orchestrator)" -ForegroundColor Cyan
Test-Endpoint -Name "GET /mcp/tools/system/health" -Url "http://127.0.0.1:8012/mcp/tools/system/health"
Write-Host ""

# Test 8: Check OpenAPI GPT Compatibility
Write-Host "[8/8] OpenAPI GPT Compatibility Check" -ForegroundColor Cyan
try {
    $openapi = Invoke-RestMethod -Uri "http://127.0.0.1:8012/openapi.json" -UseBasicParsing
    
    # Check for GPT-specific features
    $checks = @()
    
    if ($openapi.info."x-gpt-integration") {
        $checks += "✅ x-gpt-integration metadata present"
    } else {
        $checks += "❌ x-gpt-integration metadata missing"
    }
    
    $gptEndpoints = $openapi.paths.PSObject.Properties | Where-Object { $_.Name -like "*/gpt/*" }
    if ($gptEndpoints.Count -ge 4) {
        $checks += "✅ GPT endpoints found ($($gptEndpoints.Count))"
    } else {
        $checks += "❌ GPT endpoints missing"
    }
    
    if ($openapi.tags | Where-Object { $_.name -eq "GPT Developer Mode" }) {
        $checks += "✅ GPT Developer Mode tag present"
    } else {
        $checks += "❌ GPT Developer Mode tag missing"
    }
    
    foreach ($check in $checks) {
        Write-Host "  $check" -ForegroundColor $(if ($check.StartsWith("✅")) { "Green" } else { "Red" })
    }
    
    if ($checks -match "❌") {
        $script:testsFailed++
    } else {
        $script:testsPassed++
    }
} catch {
    Write-Host "  ❌ FAIL: $($_.Exception.Message)" -ForegroundColor Red
    $script:testsFailed++
}
Write-Host ""

# Summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  TEST RESULTS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "✅ Passed: $testsPassed" -ForegroundColor Green
Write-Host "❌ Failed: $testsFailed" -ForegroundColor Red
Write-Host ""

if ($testsFailed -eq 0) {
    Write-Host "🎉 ALL TESTS PASSED!" -ForegroundColor Green
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  READY FOR CHATGPT INTEGRATION" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 ChatGPT Developer Mode Setup:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "1. Open ChatGPT Developer Mode" -ForegroundColor White
    Write-Host "2. Click 'Create new action'" -ForegroundColor White
    Write-Host "3. Authentication: None (or API Key if configured)" -ForegroundColor White
    Write-Host "4. Schema:" -ForegroundColor White
    Write-Host ""
    Write-Host "   URL: " -NoNewline -ForegroundColor Gray
    Write-Host "http://127.0.0.1:8012/openapi.json" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "5. Click 'Import from URL' or paste JSON directly" -ForegroundColor White
    Write-Host "6. Test with: 'Orchestrate a workflow for AutoPro'" -ForegroundColor White
    Write-Host ""
    exit 0
} else {
    Write-Host "⚠️  SOME TESTS FAILED" -ForegroundColor Yellow
    Write-Host "Check service logs for details" -ForegroundColor Gray
    Write-Host ""
    exit 1
}
