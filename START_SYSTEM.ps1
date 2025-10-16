# START_SYSTEM.ps1 - 220 linii, pornire automată MCP System
# Pornește MCP Server (8012) și Orchestrator (3030)

Write-Host "🚀 Starting AutoPro MCP System..." -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Check if ports are available
function Test-Port {
    param($Port)
    $connection = Test-NetConnection -ComputerName localhost -Port $Port -InformationLevel Quiet -WarningAction SilentlyContinue
    return $connection
}

# Kill process on port if exists
function Stop-ProcessOnPort {
    param($Port)
    $process = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique
    if ($process) {
        Write-Host "⚠️  Port $Port is in use. Stopping process..." -ForegroundColor Yellow
        Stop-Process -Id $process -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 2
    }
}

# Step 1: Setup Environment
Write-Host "📋 Step 1: Setting up environment..." -ForegroundColor Green

# Check if .env exists in mcp_orchestrator
if (-not (Test-Path "mcp_orchestrator/.env")) {
    Write-Host "⚠️  Creating .env for orchestrator..." -ForegroundColor Yellow
    Copy-Item "mcp_orchestrator/.env.example" "mcp_orchestrator/.env" -ErrorAction SilentlyContinue
    
    # Load from workspace .env if exists
    if (Test-Path ".env") {
        $envContent = Get-Content ".env"
        foreach ($line in $envContent) {
            if ($line -match "^([^#][^=]+)=(.+)$") {
                $key = $matches[1].Trim()
                $value = $matches[2].Trim()
                
                # Add to orchestrator .env if not exists
                $orchEnv = Get-Content "mcp_orchestrator/.env"
                if ($orchEnv -notmatch "^$key=") {
                    Add-Content "mcp_orchestrator/.env" "$key=$value"
                }
            }
        }
    }
}

# Check if .env exists in mcp_server
if (-not (Test-Path "mcp_server/.env")) {
    Write-Host "⚠️  Creating .env for MCP server..." -ForegroundColor Yellow
    Copy-Item "mcp_server/.env.example" "mcp_server/.env" -ErrorAction SilentlyContinue
    
    # Load from workspace .env if exists
    if (Test-Path ".env") {
        $envContent = Get-Content ".env"
        foreach ($line in $envContent) {
            if ($line -match "^([^#][^=]+)=(.+)$") {
                $key = $matches[1].Trim()
                $value = $matches[2].Trim()
                
                # Add to server .env if not exists
                $serverEnv = Get-Content "mcp_server/.env"
                if ($serverEnv -notmatch "^$key=") {
                    Add-Content "mcp_server/.env" "$key=$value"
                }
            }
        }
    }
}

Write-Host "✅ Environment configured" -ForegroundColor Green
Write-Host ""

# Step 2: Install Dependencies
Write-Host "📦 Step 2: Installing dependencies..." -ForegroundColor Green

# Install Python dependencies for MCP Server
Write-Host "   Installing Python packages..." -ForegroundColor Cyan
Set-Location mcp_server
pip install -r requirements.txt --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install Python dependencies" -ForegroundColor Red
    exit 1
}
Set-Location ..

# Install Node.js dependencies for Orchestrator
Write-Host "   Installing Node.js packages..." -ForegroundColor Cyan
Set-Location mcp_orchestrator
npm install --silent
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install Node.js dependencies" -ForegroundColor Red
    exit 1
}

# Build TypeScript
Write-Host "   Building TypeScript..." -ForegroundColor Cyan
npm run build
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to build TypeScript" -ForegroundColor Red
    exit 1
}
Set-Location ..

Write-Host "✅ Dependencies installed" -ForegroundColor Green
Write-Host ""

# Step 3: Clear ports
Write-Host "🔧 Step 3: Preparing ports..." -ForegroundColor Green
Stop-ProcessOnPort 3030
Stop-ProcessOnPort 8012
Write-Host "✅ Ports cleared" -ForegroundColor Green
Write-Host ""

# Step 4: Start Orchestrator
Write-Host "🎯 Step 4: Starting MCP Orchestrator (port 3030)..." -ForegroundColor Green

$orchestratorJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    Set-Location mcp_orchestrator
    node http-bridge.js
}

Write-Host "   Waiting for orchestrator to start..." -ForegroundColor Cyan
Start-Sleep -Seconds 5

# Check if orchestrator is running
$orchRunning = Test-Port 3030
if ($orchRunning) {
    Write-Host "✅ Orchestrator started successfully on port 3030" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to start orchestrator" -ForegroundColor Red
    Stop-Job $orchestratorJob
    Remove-Job $orchestratorJob
    exit 1
}
Write-Host ""

# Step 5: Start MCP Server
Write-Host "🚀 Step 5: Starting MCP Server (port 8012)..." -ForegroundColor Green

$mcpJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    Set-Location mcp_server
    $env:PYTHONPATH = "."
    python main.py
}

Write-Host "   Waiting for MCP server to start..." -ForegroundColor Cyan
Start-Sleep -Seconds 5

# Check if MCP server is running
$mcpRunning = Test-Port 8012
if ($mcpRunning) {
    Write-Host "✅ MCP Server started successfully on port 8012" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to start MCP server" -ForegroundColor Red
    Stop-Job $orchestratorJob, $mcpJob
    Remove-Job $orchestratorJob, $mcpJob
    exit 1
}
Write-Host ""

# Step 6: Health Checks
Write-Host "🏥 Step 6: Running health checks..." -ForegroundColor Green

# Check Orchestrator health
try {
    $orchHealth = Invoke-RestMethod -Uri "http://localhost:3030/health" -Method Get
    Write-Host "   ✅ Orchestrator: $($orchHealth.status)" -ForegroundColor Green
    Write-Host "      - Linear: $(if ($orchHealth.clients.linear) { '✅' } else { '❌' })" -ForegroundColor Cyan
    Write-Host "      - GitHub: $(if ($orchHealth.clients.github) { '✅' } else { '❌' })" -ForegroundColor Cyan
    Write-Host "      - Supabase: $(if ($orchHealth.clients.supabase) { '✅' } else { '❌' })" -ForegroundColor Cyan
    Write-Host "      - Playwright: $(if ($orchHealth.clients.playwright) { '✅' } else { '❌' })" -ForegroundColor Cyan
} catch {
    Write-Host "   ❌ Orchestrator health check failed: $_" -ForegroundColor Red
}

# Check MCP Server health
try {
    $mcpHealth = Invoke-RestMethod -Uri "http://localhost:8012/health" -Method Get
    Write-Host "   ✅ MCP Server: $($mcpHealth.status)" -ForegroundColor Green
} catch {
    Write-Host "   ❌ MCP Server health check failed: $_" -ForegroundColor Red
}

Write-Host ""

# Step 7: Display URLs and Info
Write-Host "🎉 ============================================" -ForegroundColor Green
Write-Host "✅ MCP SYSTEM STARTED SUCCESSFULLY!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "📡 Service URLs:" -ForegroundColor Cyan
Write-Host "   - MCP Server:        http://localhost:8012" -ForegroundColor White
Write-Host "   - API Docs:          http://localhost:8012/docs" -ForegroundColor White
Write-Host "   - Orchestrator:      http://localhost:3030" -ForegroundColor White
Write-Host "   - Orchestrator Health: http://localhost:3030/health" -ForegroundColor White
Write-Host ""
Write-Host "🔑 ChatGPT Connector Details:" -ForegroundColor Cyan
Write-Host "   - URL: http://localhost:8012" -ForegroundColor Yellow
Write-Host "   - Auth: API Key" -ForegroundColor Yellow
Write-Host "   - Header: X-API-Key" -ForegroundColor Yellow
Write-Host "   - Key: dev-key-12345" -ForegroundColor Yellow
Write-Host ""
Write-Host "📚 Available Endpoints:" -ForegroundColor Cyan
Write-Host "   - GET  /api/gpt/capabilities" -ForegroundColor White
Write-Host "   - GET  /api/gpt/schema" -ForegroundColor White
Write-Host "   - POST /api/tasks/execute" -ForegroundColor White
Write-Host "   - POST /api/linear/create-issue" -ForegroundColor White
Write-Host "   - POST /api/github/create-issue" -ForegroundColor White
Write-Host "   - POST /api/supabase/select" -ForegroundColor White
Write-Host "   - POST /api/browser/navigate" -ForegroundColor White
Write-Host ""
Write-Host "⚙️  Background Jobs:" -ForegroundColor Cyan
Write-Host "   - Orchestrator Job ID: $($orchestratorJob.Id)" -ForegroundColor White
Write-Host "   - MCP Server Job ID: $($mcpJob.Id)" -ForegroundColor White
Write-Host ""
Write-Host "🛑 To stop the system:" -ForegroundColor Yellow
Write-Host "   Stop-Job $($orchestratorJob.Id), $($mcpJob.Id); Remove-Job $($orchestratorJob.Id), $($mcpJob.Id)" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to view logs or Q to quit monitoring..." -ForegroundColor Gray

# Monitor jobs
while ($true) {
    if ($Host.UI.RawUI.KeyAvailable) {
        $key = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        if ($key.Character -eq 'q' -or $key.Character -eq 'Q') {
            break
        }
    }
    
    # Check if jobs are still running
    if ($orchestratorJob.State -ne "Running") {
        Write-Host "⚠️  Orchestrator job stopped!" -ForegroundColor Red
        Receive-Job $orchestratorJob
        break
    }
    if ($mcpJob.State -ne "Running") {
        Write-Host "⚠️  MCP Server job stopped!" -ForegroundColor Red
        Receive-Job $mcpJob
        break
    }
    
    Start-Sleep -Seconds 1
}

Write-Host ""
Write-Host "✅ System monitoring ended" -ForegroundColor Green
