Param(
  [string]$Host = "127.0.0.1",
  [int]$Port = 8055
)

$ErrorActionPreference = 'Stop'
Push-Location (Join-Path $PSScriptRoot '.')
try {
  Write-Host "[MCP] Using Python: " -NoNewline; python --version

  if (-not (Test-Path '.venv')) {
    Write-Host '[MCP] Creating venv .venv'
    python -m venv .venv
  }
  & .\.venv\Scripts\Activate.ps1
  Write-Host '[MCP] Installing requirements'
  pip install -r requirements.txt

  if (-not (Test-Path '.env') -and (Test-Path '.env.example')) {
    Copy-Item '.env.example' '.env'
    Write-Host '[MCP] Created .env from .env.example (fill in tokens as needed)'
  }

  Write-Host "[MCP] Starting server on http://$Host:$Port"
  python -m uvicorn mcp_server.main:app --host $Host --port $Port --reload
}
finally {
  Pop-Location
}

