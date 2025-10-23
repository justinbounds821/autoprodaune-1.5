# MCP Server Route Testing Script
# Tests all reorganized routes to verify functionality

Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "🧪 MCP Server Route Testing" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""

$baseUrl = "http://127.0.0.1:8012"
$results = @()

function Test-Endpoint {
    param(
        [string]$Method,
        [string]$Path,
        [string]$Description,
        [hashtable]$Body = $null
    )
    
    Write-Host "Testing: $Description" -ForegroundColor Yellow
    Write-Host "  $Method $Path" -ForegroundColor Gray
    
    try {
        $params = @{
            Uri = "$baseUrl$Path"
            Method = $Method
            TimeoutSec = 10
            ErrorAction = "Stop"
        }
        
        if ($Body) {
            $params.Body = ($Body | ConvertTo-Json -Depth 10)
            $params.ContentType = "application/json"
        }
        
        $response = Invoke-WebRequest @params
        $statusCode = $response.StatusCode
        $contentLength = $response.Content.Length
        
        Write-Host "  ✅ $statusCode - $contentLength bytes" -ForegroundColor Green
        
        $results += [PSCustomObject]@{
            Category = $script:currentCategory
            Method = $Method
            Path = $Path
            Description = $Description
            Status = "✅ PASS"
            StatusCode = $statusCode
            ContentLength = $contentLength
        }
        
        return $true
    }
    catch {
        $errorMessage = $_.Exception.Message
        Write-Host "  ❌ FAIL: $errorMessage" -ForegroundColor Red
        
        $results += [PSCustomObject]@{
            Category = $script:currentCategory
            Method = $Method
            Path = $Path
            Description = $Description
            Status = "❌ FAIL"
            StatusCode = "N/A"
            ContentLength = 0
        }
        
        return $false
    }
}

# Check if server is running
Write-Host "🔍 Checking if MCP Server is running..." -ForegroundColor Cyan
try {
    $healthCheck = Invoke-WebRequest -Uri "$baseUrl/health" -Method GET -TimeoutSec 5
    Write-Host "✅ MCP Server is running!" -ForegroundColor Green
    Write-Host ""
}
catch {
    Write-Host "❌ MCP Server is not responding!" -ForegroundColor Red
    Write-Host "Please start the server with: docker compose up mcp-server" -ForegroundColor Yellow
    exit 1
}

# Test System Routes
$script:currentCategory = "System Routes"
Write-Host ""
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "📊 Testing $script:currentCategory" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""

Test-Endpoint -Method "GET" -Path "/" -Description "Root endpoint"
Test-Endpoint -Method "GET" -Path "/health" -Description "Legacy health check"
Test-Endpoint -Method "GET" -Path "/system/health" -Description "System health check"
Test-Endpoint -Method "GET" -Path "/system/status" -Description "System status"
Test-Endpoint -Method "GET" -Path "/system/tools" -Description "List all tools"
Test-Endpoint -Method "GET" -Path "/system/info" -Description "System information"

# Test Core MCP Routes
$script:currentCategory = "Core MCP Routes"
Write-Host ""
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "📋 Testing $script:currentCategory" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""

Test-Endpoint -Method "POST" -Path "/mcp/execute" -Description "Execute task" -Body @{
    task = "Test task"
    context = @{}
}
Test-Endpoint -Method "GET" -Path "/mcp/tasks" -Description "List tasks"
Test-Endpoint -Method "GET" -Path "/mcp/tasks?limit=10" -Description "List tasks with limit"
Test-Endpoint -Method "GET" -Path "/mcp/tasks?status=completed" -Description "List completed tasks"

# Test Workflow Routes
$script:currentCategory = "Workflow Routes"
Write-Host ""
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "🔄 Testing $script:currentCategory" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""

Test-Endpoint -Method "GET" -Path "/mcp/workflows/templates" -Description "List workflow templates"
Test-Endpoint -Method "POST" -Path "/mcp/workflows/analyze" -Description "Analyze workflow" -Body @{
    command = "Test workflow"
    context = @{}
}

# Test Integration Routes - Linear
$script:currentCategory = "Integration Routes (Linear)"
Write-Host ""
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "🔗 Testing $script:currentCategory" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""

Test-Endpoint -Method "GET" -Path "/mcp/tools/linear/tasks?limit=5" -Description "List Linear tasks"

# Test Integration Routes - GitHub
$script:currentCategory = "Integration Routes (GitHub)"
Write-Host ""
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "🐙 Testing $script:currentCategory" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""

Test-Endpoint -Method "GET" -Path "/mcp/tools/github/status" -Description "GitHub status"

# Test Integration Routes - Supabase
$script:currentCategory = "Integration Routes (Supabase)"
Write-Host ""
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "🗄️ Testing $script:currentCategory" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""

Test-Endpoint -Method "GET" -Path "/mcp/tools/supabase/tables" -Description "List Supabase tables"
Test-Endpoint -Method "GET" -Path "/mcp/tools/supabase/status" -Description "Supabase status"

# Test Testing Routes
$script:currentCategory = "Testing Routes"
Write-Host ""
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "🧪 Testing $script:currentCategory" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""

Test-Endpoint -Method "GET" -Path "/mcp/tools/test/suites" -Description "List test suites"
Test-Endpoint -Method "GET" -Path "/mcp/tools/test/browser/history" -Description "Browser test history"
Test-Endpoint -Method "GET" -Path "/mcp/tools/test/api/history" -Description "API test history"
Test-Endpoint -Method "GET" -Path "/mcp/tools/system/health" -Description "System health (detailed)"
Test-Endpoint -Method "GET" -Path "/mcp/tools/system/metrics" -Description "System metrics"

# Test GPT Routes
$script:currentCategory = "GPT Routes"
Write-Host ""
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "🤖 Testing $script:currentCategory" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""

Test-Endpoint -Method "GET" -Path "/mcp/tools/gpt/status" -Description "GPT system status"
Test-Endpoint -Method "GET" -Path "/mcp/tools/gpt/capabilities" -Description "GPT capabilities"
Test-Endpoint -Method "GET" -Path "/mcp/tools/gpt/help" -Description "GPT help"
Test-Endpoint -Method "GET" -Path "/mcp/tools/gpt/help?topic=workflows" -Description "GPT help - workflows"
Test-Endpoint -Method "GET" -Path "/mcp/tools/gpt/help?topic=testing" -Description "GPT help - testing"
Test-Endpoint -Method "GET" -Path "/mcp/tools/gpt/examples" -Description "GPT examples"
Test-Endpoint -Method "GET" -Path "/mcp/tools/gpt/tasks?limit=5" -Description "GPT list tasks"

# Test OpenAPI Endpoints
$script:currentCategory = "OpenAPI"
Write-Host ""
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "📖 Testing $script:currentCategory" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""

Test-Endpoint -Method "GET" -Path "/openapi.json" -Description "OpenAPI schema"
Test-Endpoint -Method "GET" -Path "/docs" -Description "Swagger UI"
Test-Endpoint -Method "GET" -Path "/redoc" -Description "ReDoc"

# Summary
Write-Host ""
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "📊 Test Summary" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""

$totalTests = $results.Count
$passedTests = ($results | Where-Object { $_.Status -eq "✅ PASS" }).Count
$failedTests = ($results | Where-Object { $_.Status -eq "❌ FAIL" }).Count
$passRate = [math]::Round(($passedTests / $totalTests) * 100, 2)

Write-Host "Total Tests:   $totalTests" -ForegroundColor White
Write-Host "Passed:        $passedTests" -ForegroundColor Green
Write-Host "Failed:        $failedTests" -ForegroundColor Red
Write-Host "Pass Rate:     $passRate%" -ForegroundColor $(if ($passRate -ge 90) { "Green" } elseif ($passRate -ge 70) { "Yellow" } else { "Red" })
Write-Host ""

# Category breakdown
Write-Host "Results by Category:" -ForegroundColor Cyan
$results | Group-Object Category | ForEach-Object {
    $category = $_.Name
    $categoryTotal = $_.Count
    $categoryPassed = ($_.Group | Where-Object { $_.Status -eq "✅ PASS" }).Count
    $categoryRate = [math]::Round(($categoryPassed / $categoryTotal) * 100, 2)
    
    Write-Host "  $category`: $categoryPassed/$categoryTotal ($categoryRate%)" -ForegroundColor $(if ($categoryRate -eq 100) { "Green" } else { "Yellow" })
}

Write-Host ""
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "✅ Route testing complete!" -ForegroundColor Green
Write-Host "=" * 80 -ForegroundColor Cyan

# Export results to JSON
$resultsFile = "test_results.json"
$results | ConvertTo-Json -Depth 10 | Out-File -FilePath $resultsFile -Encoding UTF8
Write-Host ""
Write-Host "📄 Results exported to: $resultsFile" -ForegroundColor Cyan
