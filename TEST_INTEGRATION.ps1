#Requires -Version 5.1
<#
.SYNOPSIS
    Test MCP system integration

.DESCRIPTION
    Runs comprehensive tests on the MCP system to verify all components work
#>

$ErrorActionPreference = 'Stop'

Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "  🧪 MCP System Integration Tests" -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host ""

$OrchestratorUrl = "http://127.0.0.1:3030"
$McpServerUrl = "http://127.0.0.1:8012"
$AllTestsPassed = $true

function Test-Endpoint {
    param(
        [string]$Name,
        [string]$Url,
        [string]$Method = "GET",
        [object]$Body = $null
    )
    
    Write-Host "Testing: $Name..." -NoNewline
    
    try {
        $params = @{
            Uri = $Url
            Method = $Method
            TimeoutSec = 10
        }
        
        if ($Body) {
            $params.Body = ($Body | ConvertTo-Json -Depth 10)
            $params.ContentType = "application/json"
        }
        
        $response = Invoke-RestMethod @params
        Write-Host " ✅" -ForegroundColor Green
        return $response
    } catch {
        Write-Host " ❌" -ForegroundColor Red
        Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Red
        $script:AllTestsPassed = $false
        return $null
    }
}

# Test 1: Orchestrator Health
Write-Host ""
Write-Host "📡 Test 1: Orchestrator Health" -ForegroundColor Yellow
$orchHealth = Test-Endpoint -Name "Orchestrator /health" -Url "$OrchestratorUrl/health"

if ($orchHealth) {
    Write-Host "   Status: $($orchHealth.status)" -ForegroundColor Green
}

# Test 2: MCP Server Health
Write-Host ""
Write-Host "🐍 Test 2: MCP Server Health" -ForegroundColor Yellow
$mcpHealth = Test-Endpoint -Name "MCP Server /health" -Url "$McpServerUrl/health"

if ($mcpHealth) {
    Write-Host "   Status: $($mcpHealth.status)" -ForegroundColor Green
    Write-Host "   Orchestrator Connected: $($mcpHealth.orchestrator_connected)" -ForegroundColor $(if ($mcpHealth.orchestrator_connected) { 'Green' } else { 'Red' })
    Write-Host "   Version: $($mcpHealth.version)" -ForegroundColor Gray
}

# Test 3: System Health (via MCP Server → Orchestrator)
Write-Host ""
Write-Host "🏥 Test 3: System Health Check (End-to-End)" -ForegroundColor Yellow
$sysHealth = Test-Endpoint -Name "System health via MCP" -Url "$McpServerUrl/mcp/tools/system/health"

if ($sysHealth -and $sysHealth.ok) {
    Write-Host "   Overall Status: $($sysHealth.overall_status)" -ForegroundColor Green
    Write-Host "   Services:" -ForegroundColor Gray
    foreach ($service in $sysHealth.services.PSObject.Properties) {
        $status = $service.Value.status
        $color = if ($status -eq "healthy") { "Green" } else { "Red" }
        Write-Host "     - $($service.Name): $status" -ForegroundColor $color
    }
}

# Test 4: OpenAPI Documentation
Write-Host ""
Write-Host "📚 Test 4: OpenAPI Documentation" -ForegroundColor Yellow
$openapi = Test-Endpoint -Name "OpenAPI spec" -Url "$McpServerUrl/openapi.json"

if ($openapi) {
    Write-Host "   Title: $($openapi.info.title)" -ForegroundColor Green
    Write-Host "   Version: $($openapi.info.version)" -ForegroundColor Gray
    Write-Host "   Endpoints: $($openapi.paths.Count)" -ForegroundColor Gray
    
    # Check for GPT endpoints
    $gptEndpoints = $openapi.paths.PSObject.Properties.Name | Where-Object { $_ -like "*gpt*" }
    Write-Host "   GPT Endpoints: $($gptEndpoints.Count)" -ForegroundColor Cyan
}

# Test 5: GPT Status Endpoint
Write-Host ""
Write-Host "🤖 Test 5: GPT Developer Mode Status" -ForegroundColor Yellow
$gptStatus = Test-Endpoint -Name "GPT status endpoint" -Url "$McpServerUrl/mcp/tools/gpt/status"

if ($gptStatus) {
    Write-Host "   Success: $($gptStatus.success)" -ForegroundColor $(if ($gptStatus.success) { 'Green' } else { 'Red' })
    Write-Host "   Overall Status: $($gptStatus.overall_status)" -ForegroundColor Green
}

# Test 6: Execute Simple Task
Write-Host ""
Write-Host "⚙️  Test 6: Execute Simple Task" -ForegroundColor Yellow
$taskBody = @{
    task = "Test task from integration test"
    context = @{
        test = $true
        timestamp = (Get-Date).ToString("o")
    }
}
$taskResult = Test-Endpoint -Name "Execute task" -Url "$McpServerUrl/mcp/execute" -Method POST -Body $taskBody

if ($taskResult) {
    Write-Host "   Task ID: $($taskResult.task_id)" -ForegroundColor Green
    Write-Host "   Status: $($taskResult.status)" -ForegroundColor Gray
    
    # Wait a bit and check status
    Start-Sleep -Seconds 2
    $taskStatus = Test-Endpoint -Name "Task status" -Url "$McpServerUrl/mcp/task/$($taskResult.task_id)/status"
    if ($taskStatus) {
        Write-Host "   Final Status: $($taskStatus.status)" -ForegroundColor Green
    }
}

# Summary
Write-Host ""
Write-Host "=" * 70 -ForegroundColor Cyan
if ($AllTestsPassed) {
    Write-Host "  ✅ All Tests Passed!" -ForegroundColor Green
    Write-Host "=" * 70 -ForegroundColor Green
    Write-Host ""
    Write-Host "🎉 System is fully operational and integrated!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "  • Try orchestration: POST /mcp/tools/gpt/orchestrate" -ForegroundColor White
    Write-Host "  • Create Linear task: POST /mcp/tools/gpt/create_task" -ForegroundColor White
    Write-Host "  • Run browser test: POST /mcp/tools/test/browser" -ForegroundColor White
    Write-Host ""
    Write-Host "Documentation: http://127.0.0.1:8012/docs" -ForegroundColor Cyan
    exit 0
} else {
    Write-Host "  ❌ Some Tests Failed" -ForegroundColor Red
    Write-Host "=" * 70 -ForegroundColor Red
    Write-Host ""
    Write-Host "Check the errors above and ensure both services are running:" -ForegroundColor Yellow
    Write-Host "  • Orchestrator: $OrchestratorUrl/health" -ForegroundColor White
    Write-Host "  • MCP Server: $McpServerUrl/health" -ForegroundColor White
    Write-Host ""
    Write-Host "Start system with: .\START_SYSTEM.ps1" -ForegroundColor Cyan
    exit 1
}
