Param(
  [string]$Host = "127.0.0.1",
  [int]$Port = 8055,
  [string]$FrontendDir = "..\02_FRONTEND_UI_CLEAN"
)

$ErrorActionPreference = 'Stop'
Push-Location (Join-Path $PSScriptRoot '.')
try {
  if (-not (Test-Path '.venv')) { python -m venv .venv }
  & .\.venv\Scripts\Activate.ps1
  pip install -r requirements.txt | Out-Null
  if (-not (Test-Path '.env') -and (Test-Path '.env.example')) { Copy-Item '.env.example' '.env' }

  $env:MCP_SERVER_HOST = $Host
  $env:MCP_SERVER_PORT = $Port

  Write-Host "[E2E] Starting FastMCP server..."
  $proc = Start-Process python -ArgumentList "-m","uvicorn","mcp_server.main:app","--host",$Host,"--port",$Port -PassThru -WindowStyle Hidden

  # Wait for port
  $ok = $false
  1..30 | ForEach-Object {
    Start-Sleep -Milliseconds 300
    $res = Test-NetConnection $Host -Port $Port -WarningAction SilentlyContinue
    if ($res.TcpTestSucceeded) { $ok = $true; return }
  }
  if (-not $ok) { throw "Server didn't start on $Host:$Port" }
  Write-Host "[E2E] Server is up"

  # Health
  $health = curl.exe -sS http://$Host:`$Port/health
  Write-Host "[E2E] Health: $health"

  # Execute task
  $resp = curl.exe -sS -X POST http://$Host:`$Port/mcp/execute -H "Content-Type: application/json" -d '{"task":"End2End Test Task"}'
  $obj = $resp | ConvertFrom-Json
  $taskId = $obj.task_id
  if (-not $taskId) { throw "Missing task_id" }
  Write-Host "[E2E] Task queued: $taskId"

  # Poll status
  1..40 | ForEach-Object {
    Start-Sleep -Milliseconds 500
    $s = curl.exe -sS http://$Host:`$Port/mcp/task/$taskId/status | ConvertFrom-Json
    if ($s.status -in @('completed','error')) { $global:status = $s; return }
  }
  if (-not $global:status) { throw "Task did not complete" }
  Write-Host "[E2E] Final status: $($global:status.status)"

  # Optional: frontend build smoke
  $fe = Resolve-Path $FrontendDir -ErrorAction SilentlyContinue
  if ($fe) {
    Write-Host "[E2E] Frontend build: $fe"
    pushd $fe
    if (-not (Test-Path 'node_modules')) { npm install | Out-Null }
    npm run -s build | Out-String | Out-Null
    popd
    Write-Host "[E2E] Frontend build OK"
  }

  Write-Host "[E2E] DONE"
}
finally {
  if ($proc -and !$proc.HasExited) { $proc | Stop-Process -Force }
  Pop-Location
}

