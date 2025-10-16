# ========================================
# MCP System Startup Script
# Pornește Orchestrator (Node.js) și MCP Server (Python)
# ========================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  MCP SYSTEM STARTUP" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Node.js
Write-Host "[1/6] Checking Node.js..." -ForegroundColor Yellow
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Node.js not found!" -ForegroundColor Red
    exit 1
}
$nodeVersion = node --version
Write-Host "  ✅ Node.js $nodeVersion found" -ForegroundColor Green

# Check Python
Write-Host "[2/6] Checking Python..." -ForegroundColor Yellow
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Python not found!" -ForegroundColor Red
    exit 1
}
$pythonVersion = python --version
Write-Host "  ✅ $pythonVersion found" -ForegroundColor Green

# Install Orchestrator dependencies
Write-Host "[3/6] Installing Orchestrator dependencies..." -ForegroundColor Yellow
Set-Location "$PSScriptRoot/mcp-orchestrator"

if (-not (Test-Path "node_modules")) {
    Write-Host "  Installing npm packages..." -ForegroundColor Gray
    npm install --legacy-peer-deps 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  ERROR: npm install failed!" -ForegroundColor Red
        exit 1
    }
}
Write-Host "  ✅ Dependencies installed" -ForegroundColor Green

# Compile TypeScript
Write-Host "[4/6] Compiling TypeScript..." -ForegroundColor Yellow
if (-not (Test-Path "dist/http-bridge.js") -or ((Get-Item "src/http-bridge.ts").LastWriteTime -gt (Get-Item "dist/http-bridge.js").LastWriteTime)) {
    npm run build 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  ERROR: TypeScript compilation failed!" -ForegroundColor Red
        exit 1
    }
    Write-Host "  ✅ Compiled successfully" -ForegroundColor Green
} else {
    Write-Host "  ✅ Already compiled" -ForegroundColor Green
}

# Install MCP Server dependencies
Write-Host "[5/6] Installing MCP Server dependencies..." -ForegroundColor Yellow
Set-Location "$PSScriptRoot/mcp_server"

if (-not (Test-Path ".venv")) {
    Write-Host "  Creating virtual environment..." -ForegroundColor Gray
    python -m venv .venv
}

& ".\.venv\Scripts\Activate.ps1"

if (-not (Test-Path ".venv/Lib/site-packages/fastapi")) {
    Write-Host "  Installing Python packages..." -ForegroundColor Gray
    pip install -q -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  ERROR: pip install failed!" -ForegroundColor Red
        exit 1
    }
}
Write-Host "  ✅ Dependencies installed" -ForegroundColor Green

# Start services
Write-Host "[6/6] Starting services..." -ForegroundColor Yellow
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  STARTING MCP SERVICES" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Start Orchestrator in background
Write-Host "🚀 Starting Orchestrator on port 3030..." -ForegroundColor Cyan
Set-Location "$PSScriptRoot/mcp-orchestrator"
$orchestratorJob = Start-Job -ScriptBlock {
    Set-Location $using:PSScriptRoot/mcp-orchestrator
    node dist/http-bridge.js
}

Start-Sleep -Seconds 2

# Check Orchestrator health
try {
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:3030/health" -UseBasicParsing -TimeoutSec 5
    Write-Host "  ✅ Orchestrator running on http://127.0.0.1:3030" -ForegroundColor Green
} catch {
    Write-Host "  ⚠️  Orchestrator health check failed (might still be starting...)" -ForegroundColor Yellow
}

Write-Host ""

# Start MCP Server in background
Write-Host "🚀 Starting MCP Server on port 8012..." -ForegroundColor Cyan
Set-Location "$PSScriptRoot/mcp_server"
$mcpJob = Start-Job -ScriptBlock {
    Set-Location $using:PSScriptRoot/mcp_server
    & ".\.venv\Scripts\Activate.ps1"
    python -m uvicorn main:app --host 127.0.0.1 --port 8012
}

Start-Sleep -Seconds 3

# Check MCP Server health
try {
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:8012/health" -UseBasicParsing -TimeoutSec 5
    $health = $response.Content | ConvertFrom-Json
    Write-Host "  ✅ MCP Server running on http://127.0.0.1:8012" -ForegroundColor Green
    Write-Host "  ✅ Orchestrator connected: $($health.orchestrator_connected)" -ForegroundColor Green
} catch {
    Write-Host "  ⚠️  MCP Server health check failed (might still be starting...)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  ✅ MCP SYSTEM RUNNING" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Service URLs:" -ForegroundColor Cyan
Write-Host "  • Orchestrator:  http://127.0.0.1:3030/health" -ForegroundColor White
Write-Host "  • MCP Server:    http://127.0.0.1:8012/health" -ForegroundColor White
Write-Host "  • API Docs:      http://127.0.0.1:8012/docs" -ForegroundColor White
Write-Host "  • OpenAPI Spec:  http://127.0.0.1:8012/openapi.json" -ForegroundColor White
Write-Host ""
Write-Host "🔗 ChatGPT Developer Mode:" -ForegroundColor Cyan
Write-Host "  URL: http://127.0.0.1:8012/openapi.json" -ForegroundColor Yellow
Write-Host ""
Write-Host "⌨️  Press Ctrl+C to stop all services" -ForegroundColor Gray
Write-Host ""

# Keep script running and monitor jobs
try {
    while ($true) {
        Start-Sleep -Seconds 5
        
        # Check if jobs are still running
        if ($orchestratorJob.State -ne "Running") {
            Write-Host "⚠️  Orchestrator stopped!" -ForegroundColor Red
            break
        }
        if ($mcpJob.State -ne "Running") {
            Write-Host "⚠️  MCP Server stopped!" -ForegroundColor Red
            break
        }
    }
} finally {
    Write-Host ""
    Write-Host "Stopping services..." -ForegroundColor Yellow
    Stop-Job -Job $orchestratorJob, $mcpJob
    Remove-Job -Job $orchestratorJob, $mcpJob -Force
    Write-Host "✅ All services stopped" -ForegroundColor Green
}
