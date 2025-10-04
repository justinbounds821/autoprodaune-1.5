# scripts/export-billing.ps1
"""
AutoPro Video Engine - Billing Export Script
Exports monthly billing data to CSV and uploads to R2.
"""

param(
    [Parameter(Mandatory=$true)]
    [string]$Month,

    [string]$BaseUrl = "http://127.0.0.1:8001",
    [switch]$Verbose = $false
)

Write-Host "💰 AutoPro Video Engine Billing Export" -ForegroundColor Green
Write-Host "Month: $Month" -ForegroundColor Cyan
Write-Host "Base URL: $BaseUrl" -ForegroundColor Cyan

# Validate month format
if ($Month -notmatch '^\d{4}-\d{2}$') {
    Write-Error "Invalid month format. Expected YYYY-MM (e.g., 2025-01)"
    exit 1
}

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

# Test 1: Export billing data
Write-Step "Exporting billing data for month $Month..."
try {
    $exportUrl = "$BaseUrl/api/video/billing/export?month=$Month"
    Write-Host "Requesting: $exportUrl" -ForegroundColor Gray

    $response = Invoke-RestMethod -Uri $exportUrl -Method Get -TimeoutSec 30

    if ($response.success) {
        Write-Success "Billing export created successfully"
        Write-Host "Export Details:" -ForegroundColor Gray
        Write-Host "  Export ID: $($response.export_id)" -ForegroundColor Gray
        Write-Host "  Rows: $($response.rows_count)" -ForegroundColor Gray
        Write-Host "  Total Cost: $($response.amount_cents) cents" -ForegroundColor Gray
        Write-Host "  File URL: $($response.file_url)" -ForegroundColor Gray

        if ($Verbose) {
            Write-Host "Full Response:" -ForegroundColor Gray
            $response | ConvertTo-Json | Write-Host -ForegroundColor Gray
        }

        # Test file accessibility if it's a local file
        if ($response.file_url -like "file://*") {
            $localPath = $response.file_url -replace "file://", ""
            if (Test-Path $localPath) {
                $fileSize = (Get-Item $localPath).Length
                Write-Success "Local CSV file created: $([math]::Round($fileSize / 1KB, 2)) KB"
            } else {
                Write-Warning "Local CSV file not found at expected location"
            }
        } else {
            # Test R2 URL accessibility
            try {
                $headResponse = Invoke-WebRequest -Uri $response.file_url -Method Head -TimeoutSec 10
                Write-Success "R2 CSV file accessible (HTTP $($headResponse.StatusCode))"
            } catch {
                Write-Warning "R2 CSV file not accessible: $_"
            }
        }

    } else {
        Write-Error "Billing export failed: $($response.error)"
        exit 1
    }

} catch {
    Write-Error "Failed to export billing data: $_"
    exit 1
}

# Test 2: List available exports
Write-Step "Checking available billing exports..."
try {
    $exportsUrl = "$BaseUrl/api/video/billing/exports"
    $exportsResponse = Invoke-RestMethod -Uri $exportsUrl -Method Get -TimeoutSec 10

    Write-Success "Billing exports retrieved: $($exportsResponse.total) exports"

    if ($Verbose -and $exportsResponse.exports.Count -gt 0) {
        Write-Host "Recent exports:" -ForegroundColor Gray
        $exportsResponse.exports | Select-Object -First 3 | ForEach-Object {
            Write-Host "  $($_.month): $($_.rows_count) rows, $($_.amount_cents) cents" -ForegroundColor Gray
        }
    }

} catch {
    Write-Warning "Could not retrieve billing exports: $_"
}

Write-Host ""
Write-Host "💰 Billing export completed successfully!" -ForegroundColor Green
Write-Host "📄 File available at: $($response.file_url)" -ForegroundColor Cyan