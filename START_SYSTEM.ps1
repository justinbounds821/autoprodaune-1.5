#Requires -Version 5.1
<#
.SYNOPSIS
    Start complete MCP system (orchestrator + mcp_server)

.DESCRIPTION
    Starts both HTTP bridge orchestrator and FastAPI mcp_server
    in correct order with health checks

.EXAMPLE
    .\START_SYSTEM.ps1
#>

$ErrorActionPreference = 'Stop'

Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "  🚀 Starting AutoPro MCP System" -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host ""

# Configuration
$OrchestratorPort = 3030
$McpServerPort = 8012
$MaxWaitSeconds = 30

# Function to check if port is in use
function Test-Port {
    param([int]$Port)
    $tcpConnection = Test-NetConnection -ComputerName localhost -Port $Port -WarningAction SilentlyContinue
    return $tcpConnection.TcpTestSucceeded
}

# Function to wait for service
function Wait-ForService {
    param(
        [string]$Name,
        [int]$Port,
        [int]$MaxWait = $MaxWaitSeconds
    )
    
    Write-Host "⏳ Waiting for $Name on port $Port..." -ForegroundColor Yellow
    
    $elapsed = 0
    while ($elapsed -lt $MaxWait) {
        if (Test-Port -Port $Port) {
            Write-Host "✅ $Name is ready!" -ForegroundColor Green
            return $true
        }
        Start-Sleep -Seconds 1
        $elapsed++
    }
    
    Write-Host "❌ $Name failed to start within ${MaxWait}s" -ForegroundColor Red
    return $false
}

try {
    # Step 1: Start Orchestrator HTTP Bridge
    Write-Host ""
    Write-Host "📡 Step 1: Starting MCP Orchestrator HTTP Bridge" -ForegroundColor Cyan
    Write-Host "   Port: $OrchestratorPort" -ForegroundColor Gray
    Write-Host ""
    
    if (Test-Port -Port $OrchestratorPort) {
        Write-Host "⚠️  Port $OrchestratorPort already in use" -ForegroundColor Yellow
        $response = Read-Host "Kill existing process? (y/n)"
        if ($response -eq 'y') {
            $proc = Get-NetTCPConnection -LocalPort $OrchestratorPort -ErrorAction SilentlyContinue
            if ($proc) {
                Stop-Process -Id $proc.OwningProcess -Force
                Start-Sleep -Seconds 2
            }
        } else {
            Write-Host "✅ Using existing orchestrator" -ForegroundColor Green
        }
    }
    
    if (-not (Test-Port -Port $OrchestratorPort)) {
        Push-Location mcp-orchestrator
        try {
            $orchestratorJob = Start-Job -ScriptBlock {
                param($dir)
                Set-Location $dir
                node dist/http-bridge.js
            } -ArgumentList (Get-Location).Path
            Pop-Location
            
            if (-not (Wait-ForService -Name "Orchestrator" -Port $OrchestratorPort)) {
                throw "Orchestrator failed to start"
            }
        } catch {
            Pop-Location
            throw
        }
    }
    
    # Step 2: Start FastAPI MCP Server
    Write-Host ""
    Write-Host "🐍 Step 2: Starting FastAPI MCP Server" -ForegroundColor Cyan
    Write-Host "   Port: $McpServerPort" -ForegroundColor Gray
    Write-Host ""
    
    if (Test-Port -Port $McpServerPort) {
        Write-Host "⚠️  Port $McpServerPort already in use" -ForegroundColor Yellow
        $response = Read-Host "Kill existing process? (y/n)"
        if ($response -eq 'y') {
            $proc = Get-NetTCPConnection -LocalPort $McpServerPort -ErrorAction SilentlyContinue
            if ($proc) {
                Stop-Process -Id $proc.OwningProcess -Force
                Start-Sleep -Seconds 2
            }
        } else {
            Write-Host "✅ Using existing mcp_server" -ForegroundColor Green
        }
    }
    
    if (-not (Test-Port -Port $McpServerPort)) {
        Push-Location mcp_server
        try {
            # Activate venv if exists
            if (Test-Path ".venv\Scripts\Activate.ps1") {
                & .\.venv\Scripts\Activate.ps1
            }
            
            $mcpJob = Start-Job -ScriptBlock {
                param($dir, $port)
                Set-Location $dir
                if (Test-Path ".venv\Scripts\Activate.ps1") {
                    & .\.venv\Scripts\Activate.ps1
                }
                $env:PORT = $port
                python -m uvicorn main:app --host 127.0.0.1 --port $port
            } -ArgumentList (Get-Location).Path, $McpServerPort
            Pop-Location
            
            if (-not (Wait-ForService -Name "MCP Server" -Port $McpServerPort)) {
                throw "MCP Server failed to start"
            }
        } catch {
            Pop-Location
            throw
        }
    }
    
    # Step 3: Health Checks
    Write-Host ""
    Write-Host "🏥 Step 3: Running Health Checks" -ForegroundColor Cyan
    Write-Host ""
    
    # Check orchestrator
    try {
        $orchHealth = Invoke-RestMethod -Uri "http://127.0.0.1:$OrchestratorPort/health" -TimeoutSec 5
        Write-Host "✅ Orchestrator: " -NoNewline -ForegroundColor Green
        Write-Host "$($orchHealth.status)" -ForegroundColor White
    } catch {
        Write-Host "❌ Orchestrator health check failed" -ForegroundColor Red
    }
    
    # Check mcp_server
    try {
        $mcpHealth = Invoke-RestMethod -Uri "http://127.0.0.1:$McpServerPort/health" -TimeoutSec 5
        Write-Host "✅ MCP Server: " -NoNewline -ForegroundColor Green
        Write-Host "$($mcpHealth.status)" -ForegroundColor White
        Write-Host "   Orchestrator Connected: " -NoNewline -ForegroundColor Gray
        Write-Host "$($mcpHealth.orchestrator_connected)" -ForegroundColor $(if ($mcpHealth.orchestrator_connected) { 'Green' } else { 'Red' })
    } catch {
        Write-Host "❌ MCP Server health check failed" -ForegroundColor Red
    }
    
    # Success
    Write-Host ""
    Write-Host "=" * 70 -ForegroundColor Green
    Write-Host "  ✅ System Started Successfully!" -ForegroundColor Green
    Write-Host "=" * 70 -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Services:" -ForegroundColor Yellow
    Write-Host "   • Orchestrator: http://127.0.0.1:$OrchestratorPort" -ForegroundColor White
    Write-Host "   • MCP Server:   http://127.0.0.1:$McpServerPort" -ForegroundColor White
    Write-Host "   • API Docs:     http://127.0.0.1:$McpServerPort/docs" -ForegroundColor White
    Write-Host ""
    Write-Host "📘 Quick Commands:" -ForegroundColor Yellow
    Write-Host "   • Health: curl http://127.0.0.1:$McpServerPort/health" -ForegroundColor Gray
    Write-Host "   • Orchestrate: POST /mcp/tools/gpt/orchestrate" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Press Ctrl+C to stop all services" -ForegroundColor Yellow
    Write-Host ""
    
    # Keep running
    while ($true) {
        Start-Sleep -Seconds 5
        
        # Check if services are still running
        if (-not (Test-Port -Port $OrchestratorPort)) {
            Write-Host "⚠️  Orchestrator stopped unexpectedly" -ForegroundColor Red
            break
        }
        if (-not (Test-Port -Port $McpServerPort)) {
            Write-Host "⚠️  MCP Server stopped unexpectedly" -ForegroundColor Red
            break
        }
    }
    
} catch {
    Write-Host ""
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
} finally {
    # Cleanup jobs on exit
    if ($orchestratorJob) {
        Stop-Job -Job $orchestratorJob -ErrorAction SilentlyContinue
        Remove-Job -Job $orchestratorJob -Force -ErrorAction SilentlyContinue
    }
    if ($mcpJob) {
        Stop-Job -Job $mcpJob -ErrorAction SilentlyContinue
        Remove-Job -Job $mcpJob -Force -ErrorAction SilentlyContinue
    }
}
