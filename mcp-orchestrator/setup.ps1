# AutoPro MCP Orchestrator - Quick Setup Script
# Run with: powershell -ExecutionPolicy Bypass -File setup.ps1

Write-Host "🎯 AutoPro MCP Orchestrator - Quick Setup" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Check Node.js
Write-Host "Checking Node.js..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version
    Write-Host "✅ Node.js found: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js not found. Please install Node.js 18+ from https://nodejs.org" -ForegroundColor Red
    exit 1
}

# Check npm
Write-Host "Checking npm..." -ForegroundColor Yellow
try {
    $npmVersion = npm --version
    Write-Host "✅ npm found: $npmVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ npm not found" -ForegroundColor Red
    exit 1
}

# Install dependencies
Write-Host ""
Write-Host "Installing dependencies..." -ForegroundColor Yellow
npm install

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ npm install failed" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Dependencies installed" -ForegroundColor Green

# Build TypeScript
Write-Host ""
Write-Host "Building TypeScript..." -ForegroundColor Yellow
npm run build

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Build failed" -ForegroundColor Red
    exit 1
}
Write-Host "✅ TypeScript built successfully" -ForegroundColor Green

# Check .env file
Write-Host ""
Write-Host "Checking configuration..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    Write-Host "⚠️  .env file not found. Creating from template..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "✅ .env file created" -ForegroundColor Green
    Write-Host ""
    Write-Host "⚠️  IMPORTANT: Edit .env file and add your API keys:" -ForegroundColor Yellow
    Write-Host "   - LINEAR_API_KEY" -ForegroundColor Yellow
    Write-Host "   - GITHUB_TOKEN" -ForegroundColor Yellow
    Write-Host "   - SUPABASE_URL and SUPABASE_ANON_KEY" -ForegroundColor Yellow
    Write-Host ""
} else {
    Write-Host "✅ .env file exists" -ForegroundColor Green
}

# Create reports directory
Write-Host ""
Write-Host "Creating reports directory..." -ForegroundColor Yellow
$reportsPath = Join-Path $PSScriptRoot "..\reports"
if (-not (Test-Path $reportsPath)) {
    New-Item -ItemType Directory -Path $reportsPath | Out-Null
    Write-Host "✅ Reports directory created at: $reportsPath" -ForegroundColor Green
} else {
    Write-Host "✅ Reports directory exists" -ForegroundColor Green
}

# Check Cursor MCP config
Write-Host ""
Write-Host "Checking Cursor MCP configuration..." -ForegroundColor Yellow
$mcpConfigPath = "$env:USERPROFILE\.cursor\mcp.json"
$orchestratorPath = Join-Path $PSScriptRoot "dist\index.js"

if (Test-Path $mcpConfigPath) {
    $mcpConfig = Get-Content $mcpConfigPath -Raw | ConvertFrom-Json
    if ($mcpConfig.mcpServers."autopro-orchestrator") {
        Write-Host "✅ MCP Orchestrator already configured in Cursor" -ForegroundColor Green
    } else {
        Write-Host "⚠️  MCP Orchestrator not found in Cursor config" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Add this to $mcpConfigPath :" -ForegroundColor Yellow
        Write-Host @"
{
  "mcpServers": {
    "autopro-orchestrator": {
      "command": "node",
      "args": ["$($orchestratorPath.Replace('\', '\\'))"],
      "env": {
        "NODE_ENV": "production"
      }
    }
  }
}
"@ -ForegroundColor Cyan
        Write-Host ""
    }
} else {
    Write-Host "⚠️  Cursor MCP config not found at $mcpConfigPath" -ForegroundColor Yellow
    Write-Host "   This is normal if Cursor hasn't been run yet." -ForegroundColor Yellow
}

# Final summary
Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "✅ Setup Complete!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Edit .env file with your API keys" -ForegroundColor White
Write-Host "2. Add MCP server to Cursor (see SETUP_GUIDE.md)" -ForegroundColor White
Write-Host "3. Restart Cursor" -ForegroundColor White
Write-Host "4. Test with: system_health_check tool" -ForegroundColor White
Write-Host ""
Write-Host "Documentation:" -ForegroundColor Yellow
Write-Host "- README.md - Usage guide" -ForegroundColor White
Write-Host "- SETUP_GUIDE.md - Detailed setup instructions" -ForegroundColor White
Write-Host "- GPT_MASTER_PROMPT.md - GPT orchestration setup" -ForegroundColor White
Write-Host ""
Write-Host "🚀 Ready to orchestrate!" -ForegroundColor Cyan
