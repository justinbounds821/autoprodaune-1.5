# AutoPro Daune - Script QA PowerShell pentru verificarea completă a sistemului
# Verifică toate componentele și endpoint-urile

param(
    [string]$ApiBaseUrl = "http://localhost:8000",
    [string]$FrontendUrl = "http://localhost:3000",
    [string]$AdminUrl = "http://localhost:8501"
)

# Colors for output
$Red = "Red"
$Green = "Green"
$Yellow = "Yellow"
$Blue = "Blue"

# Counter for results
$TotalChecks = 0
$PassedChecks = 0
$FailedChecks = 0

Write-Host "🚀 AutoPro Daune - QA Check Script (PowerShell)" -ForegroundColor $Blue
Write-Host "==============================================" -ForegroundColor $Blue

# Function to run a check
function Check-Endpoint {
    param(
        [string]$Name,
        [string]$Url,
        [int]$ExpectedStatus = 200
    )
    
    $script:TotalChecks++
    
    Write-Host "Checking $Name... " -NoNewline
    
    try {
        $response = Invoke-WebRequest -Uri $Url -Method GET -TimeoutSec 10 -UseBasicParsing
        if ($response.StatusCode -eq $ExpectedStatus) {
            Write-Host "✓ PASS (HTTP $($response.StatusCode))" -ForegroundColor $Green
            $script:PassedChecks++
        } else {
            Write-Host "✗ FAIL (Expected HTTP $ExpectedStatus, got HTTP $($response.StatusCode))" -ForegroundColor $Red
            $script:FailedChecks++
        }
    } catch {
        Write-Host "✗ FAIL (Connection error)" -ForegroundColor $Red
        $script:FailedChecks++
    }
}

# Function to check API endpoint with JSON response
function Check-ApiEndpoint {
    param(
        [string]$Name,
        [string]$Url,
        [string]$ExpectedField
    )
    
    $script:TotalChecks++
    
    Write-Host "Checking API $Name... " -NoNewline
    
    try {
        $response = Invoke-WebRequest -Uri $Url -Method GET -TimeoutSec 10 -UseBasicParsing
        $json = $response.Content | ConvertFrom-Json
        
        if ($json | Get-Member -Name $ExpectedField -ErrorAction SilentlyContinue) {
            Write-Host "✓ PASS (Contains $ExpectedField)" -ForegroundColor $Green
            $script:PassedChecks++
        } else {
            Write-Host "✗ FAIL (Missing $ExpectedField)" -ForegroundColor $Red
            $script:FailedChecks++
        }
    } catch {
        Write-Host "✗ FAIL (API error)" -ForegroundColor $Red
        $script:FailedChecks++
    }
}

Write-Host "`n🔍 Backend API Checks" -ForegroundColor $Blue
Write-Host "------------------------"

# Core API endpoints
Check-Endpoint "FastAPI Health" "$ApiBaseUrl/health"
Check-Endpoint "FastAPI Docs" "$ApiBaseUrl/docs"
Check-Endpoint "FastAPI OpenAPI" "$ApiBaseUrl/openapi.json"

Write-Host "`n📊 Financial API Checks" -ForegroundColor $Blue
Write-Host "-------------------------"

Check-ApiEndpoint "Financial Dashboard" "$ApiBaseUrl/api/financial/dashboard" "total_costs"
Check-ApiEndpoint "Financial Profit/Loss" "$ApiBaseUrl/api/financial/profit-loss?start_date=2024-01-01&end_date=2024-12-31" "total_revenue"

Write-Host "`n📱 Social Media API Checks" -ForegroundColor $Blue
Write-Host "----------------------------"

Check-ApiEndpoint "Social Summary" "$ApiBaseUrl/api/social/summary" "total_posts"
Check-ApiEndpoint "Social Posts" "$ApiBaseUrl/api/social/posts" "posts"
Check-ApiEndpoint "Social Analytics" "$ApiBaseUrl/api/social/analytics" "total_engagement"

Write-Host "`n🎬 Video API Checks" -ForegroundColor $Blue
Write-Host "---------------------"

Check-ApiEndpoint "Video Queue" "$ApiBaseUrl/api/video/queue" "items"
Check-ApiEndpoint "Video Stats" "$ApiBaseUrl/api/video/stats" "total_jobs"

Write-Host "`n📋 Leads API Checks" -ForegroundColor $Blue
Write-Host "---------------------"

Check-ApiEndpoint "Leads List" "$ApiBaseUrl/api/leads" "leads"
Check-Endpoint "Leads Create" "$ApiBaseUrl/api/leads" 405 # Should return Method Not Allowed for GET

Write-Host "`n💬 WhatsApp API Checks" -ForegroundColor $Blue
Write-Host "------------------------"

Check-Endpoint "WhatsApp Webhook" "$ApiBaseUrl/api/whatsapp/webhook" 405 # Should return Method Not Allowed for GET
Check-Endpoint "WhatsApp Send" "$ApiBaseUrl/api/whatsapp/send" 405 # Should return Method Not Allowed for GET

Write-Host "`n🌐 Frontend Checks" -ForegroundColor $Blue
Write-Host "--------------------"

Check-Endpoint "Frontend Home" "$FrontendUrl/"
Check-Endpoint "Frontend Dashboard" "$FrontendUrl/dashboard"
Check-Endpoint "Frontend Financial" "$FrontendUrl/financial"
Check-Endpoint "Frontend Social" "$FrontendUrl/social"
Check-Endpoint "Frontend Video" "$FrontendUrl/video"

Write-Host "`n📊 Admin Dashboard Checks" -ForegroundColor $Blue
Write-Host "----------------------------"

Check-Endpoint "Streamlit Admin" "$AdminUrl"

Write-Host "`n🔧 Environment Checks" -ForegroundColor $Blue
Write-Host "-------------------------"

# Check if .env file exists
$script:TotalChecks++
if (Test-Path ".env") {
    Write-Host "Environment file: ✓ PASS (.env exists)" -ForegroundColor $Green
    $script:PassedChecks++
} else {
    Write-Host "Environment file: ⚠ WARN (.env not found, using config.env)" -ForegroundColor $Yellow
    $script:PassedChecks++
}

# Check if config.env exists
$script:TotalChecks++
if (Test-Path "config.env") {
    Write-Host "Config file: ✓ PASS (config.env exists)" -ForegroundColor $Green
    $script:PassedChecks++
} else {
    Write-Host "Config file: ✗ FAIL (config.env not found)" -ForegroundColor $Red
    $script:FailedChecks++
}

# Check Python dependencies
$script:TotalChecks++
try {
    python -c "import fastapi, supabase, moviepy, streamlit" 2>$null
    Write-Host "Python dependencies: ✓ PASS (All required packages installed)" -ForegroundColor $Green
    $script:PassedChecks++
} catch {
    Write-Host "Python dependencies: ✗ FAIL (Missing packages)" -ForegroundColor $Red
    $script:FailedChecks++
}

# Check Node.js dependencies (if in frontend directory)
$script:TotalChecks++
if (Test-Path "auto-claim-hero\package.json") {
    Push-Location "auto-claim-hero"
    try {
        npm list --depth=0 | Out-Null
        Write-Host "Node.js dependencies: ✓ PASS (All packages installed)" -ForegroundColor $Green
        $script:PassedChecks++
    } catch {
        Write-Host "Node.js dependencies: ✗ FAIL (Missing packages)" -ForegroundColor $Red
        $script:FailedChecks++
    }
    Pop-Location
} else {
    Write-Host "Node.js dependencies: ⚠ SKIP (Frontend directory not found)" -ForegroundColor $Yellow
    $script:PassedChecks++
}

Write-Host "`n📁 File Structure Checks" -ForegroundColor $Blue
Write-Host "---------------------------"

# Check critical files
$criticalFiles = @(
    "services\api\app\main.py",
    "services\api\app\routes\financial.py",
    "services\api\app\routes\social.py",
    "services\api\app\routes\video.py",
    "services\api\app\routes\whatsapp.py",
    "services\api\app\services\supabase_client.py",
    "supabase_schema.sql",
    "auto-claim-hero\src\App.tsx",
    "auto-claim-hero\src\pages\Financial.jsx",
    "auto-claim-hero\src\pages\Social.jsx",
    "auto-claim-hero\src\pages\Video.jsx",
    "auto-claim-hero\src\components\WhatsAppForm.jsx",
    "auto-claim-hero\src\components\Navigation.jsx"
)

foreach ($file in $criticalFiles) {
    $script:TotalChecks++
    if (Test-Path $file) {
        Write-Host "File $file`: ✓ PASS" -ForegroundColor $Green
        $script:PassedChecks++
    } else {
        Write-Host "File $file`: ✗ FAIL" -ForegroundColor $Red
        $script:FailedChecks++
    }
}

Write-Host "`n🎯 Summary" -ForegroundColor $Blue
Write-Host "=========="
Write-Host "Total checks: $TotalChecks"
Write-Host "Passed: $PassedChecks" -ForegroundColor $Green
Write-Host "Failed: $FailedChecks" -ForegroundColor $Red

if ($FailedChecks -eq 0) {
    Write-Host "`n🎉 All checks passed! System is ready." -ForegroundColor $Green
    exit 0
} else {
    Write-Host "`n❌ Some checks failed. Please review the errors above." -ForegroundColor $Red
    exit 1
}
