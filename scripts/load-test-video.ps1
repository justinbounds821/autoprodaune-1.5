# scripts/load-test-video.ps1
"""
AutoPro Video Engine - Load Test Script
Tests concurrent video generation with performance metrics and success rate analysis.
"""

param(
    [int]$ConcurrentJobs = 10,
    [int]$MaxWaitTimeSeconds = 300,  # 5 minutes max per job
    [string]$BaseUrl = "http://127.0.0.1:8001",
    [switch]$Verbose = $false
)

Write-Host "🔥 AutoPro Video Engine Load Test" -ForegroundColor Green
Write-Host "Concurrent Jobs: $ConcurrentJobs" -ForegroundColor Cyan
Write-Host "Max Wait Time: $($MaxWaitTimeSeconds)s" -ForegroundColor Cyan
Write-Host "Base URL: $BaseUrl" -ForegroundColor Cyan

# Test configuration
$testScript = "Acesta este un test de încărcare pentru motorul video AutoPro. Sistemul trebuie să gestioneze multiple joburi concurente eficient și să mențină stabilitatea."
$jobs = @()
$results = @()

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

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠️  $Message" -ForegroundColor Yellow
}

# Test 1: Health check
Write-Step "Testing health endpoint..."
try {
    $response = Invoke-RestMethod -Uri "$BaseUrl/health" -Method Get -TimeoutSec 10
    Write-Success "Health check passed: $($response.status)"
} catch {
    Write-Error "Health check failed: $_"
    exit 1
}

# Test 2: Check queue limits
Write-Step "Testing queue capacity..."
try {
    $queueStats = Invoke-RestMethod -Uri "$BaseUrl/api/video/video/heygen/health" -Method Get -TimeoutSec 10

    if ($Verbose) {
        Write-Host "Queue Status:" -ForegroundColor Gray
        Write-Host "  Engine Enabled: $($queueStats.engine_enabled)" -ForegroundColor Gray
        Write-Host "  Backend: $($queueStats.backend)" -ForegroundColor Gray
        Write-Host "  FFmpeg Available: $($queueStats.ffmpeg_available)" -ForegroundColor Gray
    }

    if (-not $queueStats.engine_enabled) {
        Write-Warning "Video engine is disabled, but continuing with test"
    }
} catch {
    Write-Warning "Could not check queue status: $_"
}

# Test 3: Start concurrent jobs
Write-Step "Starting $ConcurrentJobs concurrent video generation jobs..."

$startTime = Get-Date

for ($i = 1; $i -le $ConcurrentJobs; $i++) {
    Write-Host "  Starting job $i/$ConcurrentJobs..." -ForegroundColor Gray

    try {
        $formData = @{
            script = "$testScript (Job $i)"
            voice_id = "Rachel"
            style = "realistic"
            quality = "medium"
            language = "ro"
            avatar_image_url = "https://picsum.photos/512/512?random=$i"
        }

        $response = Invoke-WebRequest -Uri "$BaseUrl/api/video/video/heygen/generate" -Method Post -Body $formData -TimeoutSec 30
        $result = $response.Content | ConvertFrom-Json

        if ($result.job_id) {
            $jobs += @{
                JobId = $result.job_id
                JobNumber = $i
                StartTime = Get-Date
                Status = "queued"
                Completed = $false
                Error = $null
            }
            Write-Success "Job $i started: $($result.job_id)"
        } else {
            Write-Error "Job $i failed to start: No job_id in response"
        }
    } catch {
        Write-Error "Job $i failed to start: $_"
        $jobs += @{
            JobId = $null
            JobNumber = $i
            StartTime = Get-Date
            Status = "failed"
            Completed = $true
            Error = $_.Exception.Message
        }
    }

    # Small delay between job starts to avoid overwhelming
    Start-Sleep -Milliseconds 500
}

$totalJobs = $jobs.Count
Write-Host "Started $totalJobs jobs in $( (Get-Date) - $startTime | Select-Object -ExpandProperty TotalSeconds ) seconds" -ForegroundColor Green

# Test 4: Monitor job progress
Write-Step "Monitoring job progress..."

$completedJobs = 0
$failedJobs = 0
$timeoutJobs = 0

while ($completedJobs + $failedJobs + $timeoutJobs -lt $totalJobs) {
    foreach ($job in $jobs) {
        if ($job.Completed) {
            continue
        }

        try {
            $response = Invoke-RestMethod -Uri "$BaseUrl/api/video/video/heygen/status/$($job.JobId)" -Method Get -TimeoutSec 10
            $job.Status = $response.status

            if ($response.status -eq "completed") {
                $job.Completed = $true
                $job.EndTime = Get-Date
                $job.Duration = ($job.EndTime - $job.StartTime).TotalSeconds
                $completedJobs++
                Write-Success "Job $($job.JobNumber) completed in $($job.Duration)s"
            } elseif ($response.status -eq "failed") {
                $job.Completed = $true
                $job.EndTime = Get-Date
                $job.Duration = ($job.EndTime - $job.StartTime).TotalSeconds
                $job.Error = $response.error
                $failedJobs++
                Write-Error "Job $($job.JobNumber) failed after $($job.Duration)s: $($response.error)"
            }
        } catch {
            # Status check failed, continue polling
        }
    }

    # Check for timeouts
    $currentTime = Get-Date
    foreach ($job in $jobs) {
        if (-not $job.Completed -and $job.JobId) {
            $elapsed = ($currentTime - $job.StartTime).TotalSeconds
            if ($elapsed -gt $MaxWaitTimeSeconds) {
                $job.Completed = $true
                $job.EndTime = $currentTime
                $job.Duration = $elapsed
                $job.Error = "Timeout after $($MaxWaitTimeSeconds)s"
                $timeoutJobs++
                Write-Warning "Job $($job.JobNumber) timed out after $($elapsed)s"
            }
        }
    }

    # Progress update
    $progress = (($completedJobs + $failedJobs + $timeoutJobs) / $totalJobs) * 100
    Write-Host "Progress: $(($completedJobs + $failedJobs + $timeoutJobs))/$totalJobs ($($progress.ToString('F1'))%) - Completed: $completedJobs, Failed: $failedJobs, Timeout: $timeoutJobs" -ForegroundColor Cyan

    if (($completedJobs + $failedJobs + $timeoutJobs) -lt $totalJobs) {
        Start-Sleep -Seconds 2
    }
}

$totalDuration = (Get-Date - $startTime).TotalSeconds

# Test 5: Test download for completed jobs
$downloadableJobs = $jobs | Where-Object { $_.Status -eq "completed" -and $_.JobId }

if ($downloadableJobs.Count -gt 0) {
    Write-Step "Testing video downloads for completed jobs..."

    $downloadSuccess = 0
    $downloadFailed = 0

    foreach ($job in $downloadableJobs | Select-Object -First 3) {  # Test first 3 only
        try {
            $tempFile = "test_video_$($job.JobId).mp4"
            $response = Invoke-WebRequest -Uri "$BaseUrl/api/video/video/heygen/download/$($job.JobId)" -Method Get -OutFile $tempFile -TimeoutSec 60

            if (Test-Path $tempFile) {
                $fileSize = (Get-Item $tempFile).Length
                Write-Success "Downloaded $($job.JobNumber): $([math]::Round($fileSize / 1MB, 2)) MB"
                Remove-Item $tempFile -ErrorAction SilentlyContinue
                $downloadSuccess++
            } else {
                Write-Error "Download failed for $($job.JobNumber): File not created"
                $downloadFailed++
            }
        } catch {
            Write-Error "Download failed for $($job.JobNumber): $_"
            $downloadFailed++
        }
    }

    Write-Host "Download test: $downloadSuccess success, $downloadFailed failed" -ForegroundColor Cyan
}

# Test 6: Check metrics endpoint
Write-Step "Testing metrics endpoint..."
try {
    $metricsResponse = Invoke-RestMethod -Uri "$BaseUrl/metrics" -Method Get -TimeoutSec 10

    if ($metricsResponse -and $metricsResponse.Contains("autopro_video_jobs_total")) {
        Write-Success "Metrics endpoint working"
        if ($Verbose) {
            Write-Host "Sample metrics:" -ForegroundColor Gray
            $lines = $metricsResponse -split "`n" | Select-Object -First 5
            $lines | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }
        }
    } else {
        Write-Warning "Metrics endpoint returned unexpected content"
    }
} catch {
    Write-Warning "Metrics endpoint not available: $_"
}

# Test 7: Check detailed health
Write-Step "Testing detailed health endpoint..."
try {
    $healthResponse = Invoke-RestMethod -Uri "$BaseUrl/health/detailed" -Method Get -TimeoutSec 10

    if ($healthResponse.status) {
        Write-Success "Detailed health check passed: $($healthResponse.status)"
        if ($Verbose) {
            Write-Host "Health details:" -ForegroundColor Gray
            $healthResponse.dependencies.PSObject.Properties | ForEach-Object {
                Write-Host "  $($_.Name): $($_.Value.status)" -ForegroundColor Gray
            }
        }
    } else {
        Write-Warning "Detailed health check returned unexpected format"
    }
} catch {
    Write-Warning "Detailed health endpoint not available: $_"
}

# Results Summary
Write-Host ""
Write-Host "🎉 Load Test Results Summary" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan

Write-Host "📊 Job Statistics:" -ForegroundColor Cyan
Write-Host "  Total Jobs: $totalJobs" -ForegroundColor White
Write-Host "  Completed: $completedJobs" -ForegroundColor Green
Write-Host "  Failed: $failedJobs" -ForegroundColor Red
Write-Host "  Timed Out: $timeoutJobs" -ForegroundColor Yellow

$successRate = ($completedJobs / $totalJobs) * 100
Write-Host "  Success Rate: $($successRate.ToString('F1'))%" -ForegroundColor $(if ($successRate -ge 90) { "Green" } elseif ($successRate -ge 70) { "Yellow" } else { "Red" })

Write-Host ""
Write-Host "⏱️  Performance Metrics:" -ForegroundColor Cyan
Write-Host "  Total Duration: $($totalDuration.ToString('F1'))s" -ForegroundColor White
Write-Host "  Avg Job Duration: $(($totalDuration / $totalJobs).ToString('F1'))s" -ForegroundColor White

if ($completedJobs -gt 0) {
    $completedDurations = $jobs | Where-Object { $_.Status -eq "completed" } | ForEach-Object { $_.Duration }
    $avgCompletionTime = ($completedDurations | Measure-Object -Average).Average
    Write-Host "  Avg Completion Time: $($avgCompletionTime.ToString('F1'))s" -ForegroundColor White
}

Write-Host ""
Write-Host "🔧 System Load:" -ForegroundColor Cyan
Write-Host "  Jobs/Second: $(($totalJobs / $totalDuration).ToString('F2'))" -ForegroundColor White
Write-Host "  Concurrent Capacity: Tested with $ConcurrentJobs parallel jobs" -ForegroundColor White

# Recommendations
Write-Host ""
Write-Host "💡 Recommendations:" -ForegroundColor Cyan

if ($successRate -ge 90) {
    Write-Host "  ✅ Excellent! System handled load well" -ForegroundColor Green
    Write-Host "  💡 Consider increasing VIDEO_ENGINE_MAX_CONCURRENCY for higher throughput" -ForegroundColor Yellow
} elseif ($successRate -ge 70) {
    Write-Host "  ⚠️  Good performance, but some jobs failed" -ForegroundColor Yellow
    Write-Host "  💡 Check error logs and consider retry configuration" -ForegroundColor Yellow
} else {
    Write-Host "  ❌ Poor performance - investigate failures" -ForegroundColor Red
    Write-Host "  💡 Check system resources and error logs" -ForegroundColor Red
}

if ($timeoutJobs -gt 0) {
    Write-Host "  ⏰ Some jobs timed out - consider increasing MaxWaitTimeSeconds" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🚀 Load test completed!" -ForegroundColor Green

# Exit code based on success rate
if ($successRate -ge 90) {
    exit 0
} elseif ($successRate -ge 70) {
    exit 0  # Warning but acceptable
} else {
    exit 1  # Too many failures
}