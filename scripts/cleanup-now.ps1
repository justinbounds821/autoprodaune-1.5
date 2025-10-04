# scripts/cleanup-now.ps1
"""
AutoPro Video Engine - Manual Housekeeping Script
Runs housekeeping cleanup immediately for development/testing.
"""

param(
    [string]$BaseUrl = "http://127.0.0.1:8001",
    [switch]$Verbose = $false
)

Write-Host "🧹 AutoPro Video Engine Manual Housekeeping" -ForegroundColor Green
Write-Host "Base URL: $BaseUrl" -ForegroundColor Cyan

function Write-Step {
    param([string]$Message)
    Write-Host "➡️  $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Error {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

# Test 1: Run housekeeping cleanup
Write-Step "Running manual housekeeping cleanup..."
try {
    $cleanupUrl = "$BaseUrl/api/video/housekeeping/run"
    $response = Invoke-RestMethod -Uri $cleanupUrl -Method Post -TimeoutSec 60

    Write-Success "Housekeeping cleanup completed"

    if ($Verbose) {
        Write-Host "Cleanup Results:" -ForegroundColor Gray
        Write-Host "  Database Cleanup:" -ForegroundColor Gray
        Write-Host "    Deleted Jobs: $($response.database_cleanup.deleted_jobs)" -ForegroundColor Gray
        Write-Host "    Errors: $($response.database_cleanup.errors -join ', ')" -ForegroundColor Gray

        Write-Host "  Local Cleanup:" -ForegroundColor Gray
        Write-Host "    Deleted Files: $($response.local_cleanup.deleted_files)" -ForegroundColor Gray
        Write-Host "    Errors: $($response.local_cleanup.errors -join ', ')" -ForegroundColor Gray

        Write-Host "  R2 Cleanup:" -ForegroundColor Gray
        Write-Host "    Deleted Objects: $($response.r2_cleanup.deleted_objects)" -ForegroundColor Gray
        Write-Host "    Errors: $($response.r2_cleanup.errors -join ', ')" -ForegroundColor Gray
    }

    # Calculate totals
    $totalDeleted = $response.database_cleanup.deleted_jobs + $response.local_cleanup.deleted_files + $response.r2_cleanup.deleted_objects
    Write-Host "Total items cleaned up: $totalDeleted" -ForegroundColor Cyan

} catch {
    Write-Error "Housekeeping cleanup failed: $_"
    exit 1
}

# Test 2: Check queue status after cleanup
Write-Step "Checking queue status after cleanup..."
try {
    $healthUrl = "$BaseUrl/health/detailed"
    $healthResponse = Invoke-RestMethod -Uri $healthUrl -Method Get -TimeoutSec 10

    Write-Success "Queue status retrieved after cleanup"

    if ($Verbose) {
        Write-Host "Queue Information:" -ForegroundColor Gray
        $queue = $healthResponse.queue
        Write-Host "  Total Jobs: $($queue.total_jobs)" -ForegroundColor Gray
        Write-Host "  Processing: $($queue.processing_count)" -ForegroundColor Gray
        Write-Host "  Queue Length: $($queue.queue_length)" -ForegroundColor Gray
        Write-Host "  Status Counts:" -ForegroundColor Gray
        $queue.status_counts.PSObject.Properties | ForEach-Object {
            Write-Host "    $($_.Name): $($_.Value)" -ForegroundColor Gray
        }
    }

} catch {
    Write-Warning "Could not check queue status: $_"
}

Write-Host ""
Write-Host "🧹 Manual housekeeping completed!" -ForegroundColor Green