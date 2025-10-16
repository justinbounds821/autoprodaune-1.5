# start_with_ngrok.ps1 - Quick Start MCP + Ngrok

Write-Host "🚀 Starting MCP System with Ngrok..." -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Start MCP System
Write-Host "📦 Step 1: Starting MCP System..." -ForegroundColor Green
$mcpJob = Start-Job -ScriptBlock { 
    Set-Location $using:PWD
    .\START_SYSTEM.ps1 
}

Write-Host "   Waiting for services to start..." -ForegroundColor Cyan
Start-Sleep -Seconds 15

# Check if services are running
try {
    $health = Invoke-RestMethod http://localhost:8012/health -ErrorAction Stop
    Write-Host "   ✅ MCP Server running" -ForegroundColor Green
} catch {
    Write-Host "   ❌ MCP Server failed to start" -ForegroundColor Red
    Stop-Job $mcpJob
    Remove-Job $mcpJob
    exit 1
}

Write-Host ""

# Step 2: Check ngrok
Write-Host "🔍 Step 2: Checking ngrok..." -ForegroundColor Green
$ngrokInstalled = Get-Command ngrok -ErrorAction SilentlyContinue

if (-not $ngrokInstalled) {
    Write-Host "   ⚠️  Ngrok not found!" -ForegroundColor Yellow
    Write-Host "   Install with: choco install ngrok" -ForegroundColor White
    Write-Host "   Or download from: https://ngrok.com/download" -ForegroundColor White
    Write-Host ""
    Write-Host "   After installing, run this script again." -ForegroundColor Cyan
    Stop-Job $mcpJob
    Remove-Job $mcpJob
    exit 1
}

Write-Host "   ✅ Ngrok found" -ForegroundColor Green
Write-Host ""

# Step 3: Start ngrok
Write-Host "🌐 Step 3: Starting ngrok tunnel..." -ForegroundColor Green
$ngrokJob = Start-Job -ScriptBlock {
    ngrok http 8012 --log=stdout
}

Write-Host "   Waiting for tunnel..." -ForegroundColor Cyan
Start-Sleep -Seconds 5

# Step 4: Get ngrok URL
try {
    $tunnels = Invoke-RestMethod http://localhost:4040/api/tunnels
    $ngrokUrl = $tunnels.tunnels[0].public_url
    
    if (-not $ngrokUrl) {
        throw "No tunnel URL found"
    }
    
    Write-Host "   ✅ Tunnel created: $ngrokUrl" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Failed to get ngrok URL: $_" -ForegroundColor Red
    Write-Host "   Make sure ngrok is authenticated:" -ForegroundColor Yellow
    Write-Host "   ngrok config add-authtoken YOUR_TOKEN" -ForegroundColor White
    Stop-Job $mcpJob, $ngrokJob
    Remove-Job $mcpJob, $ngrokJob
    exit 1
}

Write-Host ""

# Step 5: Display Info
Write-Host "╔═══════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║                                                       ║" -ForegroundColor Green
Write-Host "║     ✅ MCP SYSTEM READY FOR CHATGPT! 🚀              ║" -ForegroundColor Green
Write-Host "║                                                       ║" -ForegroundColor Green
Write-Host "╠═══════════════════════════════════════════════════════╣" -ForegroundColor Green
Write-Host "║                                                       ║" -ForegroundColor Green
Write-Host "║  🔗 Public URL (copy this):                          ║" -ForegroundColor Cyan
Write-Host "║     $ngrokUrl" -ForegroundColor Yellow
Write-Host "║                                                       ║" -ForegroundColor Green
Write-Host "║  🔑 API Key:                                         ║" -ForegroundColor Cyan
Write-Host "║     dev-key-12345                                    ║" -ForegroundColor Yellow
Write-Host "║                                                       ║" -ForegroundColor Green
Write-Host "║  📋 ChatGPT Configuration:                           ║" -ForegroundColor Cyan
Write-Host "║     Name:        AutoPro MCP Server                  ║" -ForegroundColor White
Write-Host "║     Description: Model Context Protocol AutoPro      ║" -ForegroundColor White
Write-Host "║     URL:         $ngrokUrl" -ForegroundColor White
Write-Host "║     Auth Type:   API Key                             ║" -ForegroundColor White
Write-Host "║     Header:      X-API-Key                           ║" -ForegroundColor White
Write-Host "║     Key Value:   dev-key-12345                       ║" -ForegroundColor White
Write-Host "║                                                       ║" -ForegroundColor Green
Write-Host "║  🌐 Ngrok Dashboard:                                 ║" -ForegroundColor Cyan
Write-Host "║     http://localhost:4040                            ║" -ForegroundColor White
Write-Host "║                                                       ║" -ForegroundColor Green
Write-Host "║  📚 API Docs:                                        ║" -ForegroundColor Cyan
Write-Host "║     $ngrokUrl/docs" -ForegroundColor White
Write-Host "║                                                       ║" -ForegroundColor Green
Write-Host "╚═══════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "⚡ Test Connection:" -ForegroundColor Yellow
Write-Host "   curl $ngrokUrl/health" -ForegroundColor White
Write-Host ""
Write-Host "🛑 To stop:" -ForegroundColor Yellow
Write-Host "   Press Ctrl+C" -ForegroundColor White
Write-Host ""
Write-Host "📊 Monitoring requests at: http://localhost:4040" -ForegroundColor Gray
Write-Host ""

# Test the connection
Write-Host "🧪 Testing connection..." -ForegroundColor Cyan
try {
    $testResult = Invoke-RestMethod "$ngrokUrl/health"
    Write-Host "✅ Connection test successful!" -ForegroundColor Green
    Write-Host "   Status: $($testResult.status)" -ForegroundColor White
} catch {
    Write-Host "⚠️  Connection test failed: $_" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "System is running... Press Ctrl+C to stop" -ForegroundColor Gray
Write-Host ""

# Monitor and keep alive
$lastCheck = Get-Date
while ($true) {
    Start-Sleep -Seconds 5
    
    # Check every 30 seconds
    if (((Get-Date) - $lastCheck).TotalSeconds -ge 30) {
        try {
            $health = Invoke-RestMethod http://localhost:8012/health -ErrorAction SilentlyContinue
            Write-Host "$(Get-Date -Format 'HH:mm:ss') - System healthy ✅" -ForegroundColor Green
        } catch {
            Write-Host "$(Get-Date -Format 'HH:mm:ss') - System check failed ⚠️" -ForegroundColor Yellow
        }
        $lastCheck = Get-Date
    }
    
    # Check if jobs are running
    if ($mcpJob.State -ne "Running") {
        Write-Host "⚠️  MCP job stopped! Restarting..." -ForegroundColor Red
        $mcpJob = Start-Job -ScriptBlock { 
            Set-Location $using:PWD
            .\START_SYSTEM.ps1 
        }
        Start-Sleep -Seconds 10
    }
    
    if ($ngrokJob.State -ne "Running") {
        Write-Host "⚠️  Ngrok job stopped! Restarting..." -ForegroundColor Red
        $ngrokJob = Start-Job -ScriptBlock {
            ngrok http 8012 --log=stdout
        }
        Start-Sleep -Seconds 5
    }
}

# Cleanup on exit
trap {
    Write-Host ""
    Write-Host "🛑 Stopping services..." -ForegroundColor Yellow
    Stop-Job $mcpJob, $ngrokJob -ErrorAction SilentlyContinue
    Remove-Job $mcpJob, $ngrokJob -ErrorAction SilentlyContinue
    Write-Host "✅ Cleanup complete" -ForegroundColor Green
    exit
}
