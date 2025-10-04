# scripts/db-migrate-video.ps1
"""
AutoPro Video Engine - Database Migration Script
Applies video engine schema to Supabase database.
"""

param(
    [switch]$DryRun = $false,
    [string]$SupabaseUrl,
    [string]$SupabaseKey
)

Write-Host "🗄️ AutoPro Video Engine Database Migration" -ForegroundColor Green

# Check for Supabase credentials
if (-not $SupabaseUrl -or -not $SupabaseKey) {
    Write-Host "🔑 Supabase credentials not provided as parameters" -ForegroundColor Yellow
    Write-Host "Checking environment variables..." -ForegroundColor Blue

    $SupabaseUrl = $env:SUPABASE_URL
    $SupabaseKey = $env:SUPABASE_SERVICE_KEY

    if (-not $SupabaseUrl -or -not $SupabaseKey) {
        Write-Error "❌ Supabase credentials not found!"
        Write-Host "Please provide either:" -ForegroundColor Yellow
        Write-Host "  1. Parameters: -SupabaseUrl 'your-url' -SupabaseKey 'your-key'" -ForegroundColor Yellow
        Write-Host "  2. Environment variables: SUPABASE_URL and SUPABASE_SERVICE_KEY" -ForegroundColor Yellow
        exit 1
    }
}

Write-Host "✅ Supabase credentials found" -ForegroundColor Green
Write-Host "📍 URL: $SupabaseUrl" -ForegroundColor Cyan

# Check if migration file exists
$migrationFile = "services/api/database/video_engine.sql"
if (-not (Test-Path $migrationFile)) {
    Write-Error "❌ Migration file not found: $migrationFile"
    exit 1
}

Write-Host "📄 Found migration file: $migrationFile" -ForegroundColor Green

# Read migration SQL
try {
    # Check if phase 6 migration exists and include it
    $phase6File = "services/api/database/video_engine_phase6.sql"
    if (Test-Path $phase6File) {
        Write-Host "📄 Including phase 6 migration file: $phase6File" -ForegroundColor Green
        $phase6Sql = Get-Content $phase6File -Raw -Encoding UTF8
        $migrationSql = $migrationSql + "`n`n-- Phase 6 Migration`n" + $phase6Sql
    }

    $migrationSql = Get-Content $migrationFile -Raw -Encoding UTF8
} catch {
    Write-Error "❌ Failed to read migration file: $_"
    exit 1
}

if ($DryRun) {
    Write-Host "🔍 DRY RUN MODE" -ForegroundColor Yellow
    Write-Host "Would execute the following SQL migration:" -ForegroundColor Blue
    Write-Host "----------------------------------------" -ForegroundColor Gray
    Write-Host $migrationSql -ForegroundColor Gray
    Write-Host "----------------------------------------" -ForegroundColor Gray
    exit 0
}

# Confirm before applying
Write-Host ""
Write-Warning "⚠️ This will modify your Supabase database!"
Write-Host "Make sure you have a backup before proceeding." -ForegroundColor Yellow
$response = Read-Host "Do you want to continue? (yes/no)"

if ($response -ne "yes" -and $response -ne "y") {
    Write-Host "❌ Migration cancelled by user" -ForegroundColor Yellow
    exit 0
}

# Apply migration via Supabase REST API
Write-Host "🚀 Applying migration to Supabase..." -ForegroundColor Green

try {
    # Create the SQL execution request
    $headers = @{
        "apikey" = $SupabaseKey
        "Authorization" = "Bearer $SupabaseKey"
        "Content-Type" = "application/json"
    }

    $body = @{
        "query" = $migrationSql
    } | ConvertTo-Json

    # Execute via Supabase SQL API
    $response = Invoke-RestMethod -Uri "$SupabaseUrl/rest/v1/rpc/execute_sql" -Method Post -Headers $headers -Body $body

    if ($response) {
        Write-Success "✅ Migration applied successfully!"
    } else {
        Write-Error "❌ Migration failed - no response"
        exit 1
    }

} catch {
    Write-Error "❌ Migration failed: $_"
    Write-Host ""
    Write-Host "🔧 Troubleshooting tips:" -ForegroundColor Yellow
    Write-Host "  1. Check your Supabase credentials" -ForegroundColor Gray
    Write-Host "  2. Ensure your IP is whitelisted in Supabase" -ForegroundColor Gray
    Write-Host "  3. Verify the database is accessible" -ForegroundColor Gray
    Write-Host "  4. Check Supabase logs for detailed error messages" -ForegroundColor Gray
    exit 1
}

# Verify migration was applied
Write-Host ""
Write-Host "🔍 Verifying migration..." -ForegroundColor Blue

try {
    # Check if tables exist
    $tablesResponse = Invoke-RestMethod -Uri "$SupabaseUrl/rest/v1/" -Method Get -Headers $headers
    $tables = $tablesResponse | Where-Object { $_.name -in @("video_jobs", "video_assets", "video_costs", "video_webhooks") }

    Write-Host "✅ Tables created:" -ForegroundColor Green
    $tables | ForEach-Object {
        Write-Host "  - $($_.name)" -ForegroundColor Gray
    }

    $missingTables = @("video_jobs", "video_assets", "video_costs", "video_webhooks") | Where-Object { $_ -notin $tables.name }
    if ($missingTables) {
        Write-Warning "⚠️ Some tables may be missing: $($missingTables -join ', ')"
    }

} catch {
    Write-Warning "⚠️ Could not verify table creation: $_"
}

Write-Host ""
Write-Host "🎉 AutoPro Video Engine database migration completed!" -ForegroundColor Green
Write-Host "🚀 Your database is now ready for video generation!" -ForegroundColor Green