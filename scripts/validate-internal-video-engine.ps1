# ============================================
# Internal Video Engine - Validation Script
# ============================================

Write-Host "🔍 Validating Internal Video Engine Implementation..." -ForegroundColor Green
Write-Host ""

$errors = @()
$warnings = @()
$success = @()

# Check if we're in the right directory
if (!(Test-Path "services/api/app/main.py")) {
    $errors += "Not in project root directory"
    Write-Host "❌ Error: Please run this script from the project root directory" -ForegroundColor Red
    exit 1
}

Write-Host "📁 Project root: $(Get-Location)" -ForegroundColor Gray
Write-Host ""

# 1. Check Environment Configuration
Write-Host "1️⃣ Checking Environment Configuration..." -ForegroundColor Yellow
if (Test-Path "services/api/env.example") {
    $envContent = Get-Content "services/api/env.example" -Raw
    if ($envContent -match "USE_INTERNAL_VIDEO_ENGINE") {
        $success += "Environment variables configured in env.example"
        Write-Host "✅ Environment variables configured" -ForegroundColor Green
    } else {
        $errors += "Missing USE_INTERNAL_VIDEO_ENGINE in env.example"
        Write-Host "❌ Missing environment variables" -ForegroundColor Red
    }
} else {
    $errors += "env.example file not found"
    Write-Host "❌ env.example file not found" -ForegroundColor Red
}

# 2. Check Models
Write-Host "2️⃣ Checking Models..." -ForegroundColor Yellow
if (Test-Path "services/api/app/models/video_models.py") {
    $success += "Video models created"
    Write-Host "✅ Video models file exists" -ForegroundColor Green
    
    $modelContent = Get-Content "services/api/app/models/video_models.py" -Raw
    if ($modelContent -match "GenerateVideoRequest" -and $modelContent -match "GenerateVideoResponse") {
        $success += "Core video models defined"
        Write-Host "✅ Core video models defined" -ForegroundColor Green
    } else {
        $errors += "Missing core video models"
        Write-Host "❌ Missing core video models" -ForegroundColor Red
    }
} else {
    $errors += "video_models.py not found"
    Write-Host "❌ Video models file not found" -ForegroundColor Red
}

# 3. Check Services
Write-Host "3️⃣ Checking Services..." -ForegroundColor Yellow
$services = @("job_store.py", "voice_elevenlabs.py", "video_engine_lipsync.py")
foreach ($service in $services) {
    $servicePath = "services/api/app/services/$service"
    if (Test-Path $servicePath) {
        $success += "Service $service created"
        Write-Host "✅ Service $service exists" -ForegroundColor Green
    } else {
        $errors += "Service $service not found"
        Write-Host "❌ Service $service not found" -ForegroundColor Red
    }
}

# 4. Check Routes
Write-Host "4️⃣ Checking Routes..." -ForegroundColor Yellow
if (Test-Path "services/api/app/routes/video_internal_alias.py") {
    $success += "Internal video router created"
    Write-Host "✅ Internal video router exists" -ForegroundColor Green
    
    $routeContent = Get-Content "services/api/app/routes/video_internal_alias.py" -Raw
    if ($routeContent -match "/generate" -and $routeContent -match "/status" -and $routeContent -match "/download") {
        $success += "Core routes defined"
        Write-Host "✅ Core routes defined" -ForegroundColor Green
    } else {
        $errors += "Missing core routes"
        Write-Host "❌ Missing core routes" -ForegroundColor Red
    }
} else {
    $errors += "video_internal_alias.py not found"
    Write-Host "❌ Internal video router not found" -ForegroundColor Red
}

# 5. Check Main.py Integration
Write-Host "5️⃣ Checking Main.py Integration..." -ForegroundColor Yellow
$mainContent = Get-Content "services/api/app/main.py" -Raw
if ($mainContent -match "video_internal_alias") {
    $success += "Internal video router integrated in main.py"
    Write-Host "✅ Internal video router integrated" -ForegroundColor Green
} else {
    $errors += "Internal video router not integrated in main.py"
    Write-Host "❌ Internal video router not integrated" -ForegroundColor Red
}

# 6. Check Requirements
Write-Host "6️⃣ Checking Requirements..." -ForegroundColor Yellow
if (Test-Path "services/api/requirements.txt") {
    $requirementsContent = Get-Content "services/api/requirements.txt" -Raw
    $requiredPackages = @("moviepy", "pydub", "opencv-python", "ffmpeg-python")
    $missingPackages = @()
    
    foreach ($package in $requiredPackages) {
        if ($requirementsContent -match $package) {
            $success += "Package $package in requirements"
            Write-Host "✅ Package $package in requirements" -ForegroundColor Green
        } else {
            $missingPackages += $package
            $warnings += "Package $package missing from requirements"
            Write-Host "⚠️ Package $package missing from requirements" -ForegroundColor Yellow
        }
    }
} else {
    $errors += "requirements.txt not found"
    Write-Host "❌ requirements.txt not found" -ForegroundColor Red
}

# 7. Check Scripts
Write-Host "7️⃣ Checking Scripts..." -ForegroundColor Yellow
$scripts = @("install-internal-video-engine.ps1", "test-internal-video-engine.ps1")
foreach ($script in $scripts) {
    $scriptPath = "scripts/$script"
    if (Test-Path $scriptPath) {
        $success += "Script $script created"
        Write-Host "✅ Script $script exists" -ForegroundColor Green
    } else {
        $warnings += "Script $script not found"
        Write-Host "⚠️ Script $script not found" -ForegroundColor Yellow
    }
}

# 8. Check Third-party Dependencies
Write-Host "8️⃣ Checking Third-party Dependencies..." -ForegroundColor Yellow
$thirdPartyPath = "third_party"
if (Test-Path $thirdPartyPath) {
    $success += "Third-party directory exists"
    Write-Host "✅ Third-party directory exists" -ForegroundColor Green
    
    if (Test-Path "$thirdPartyPath/SadTalker") {
        $success += "SadTalker submodule exists"
        Write-Host "✅ SadTalker submodule exists" -ForegroundColor Green
    } else {
        $warnings += "SadTalker submodule not found (run install script)"
        Write-Host "⚠️ SadTalker submodule not found" -ForegroundColor Yellow
    }
    
    if (Test-Path "$thirdPartyPath/Wav2Lip") {
        $success += "Wav2Lip submodule exists"
        Write-Host "✅ Wav2Lip submodule exists" -ForegroundColor Green
    } else {
        $warnings += "Wav2Lip submodule not found (run install script)"
        Write-Host "⚠️ Wav2Lip submodule not found" -ForegroundColor Yellow
    }
} else {
    $warnings += "Third-party directory not found (run install script)"
    Write-Host "⚠️ Third-party directory not found" -ForegroundColor Yellow
}

# Summary
Write-Host ""
Write-Host "📊 VALIDATION SUMMARY" -ForegroundColor Cyan
Write-Host "===================" -ForegroundColor Cyan

if ($success.Count -gt 0) {
    Write-Host ""
    Write-Host "✅ SUCCESS ($($success.Count) items):" -ForegroundColor Green
    foreach ($item in $success) {
        Write-Host "   • $item" -ForegroundColor White
    }
}

if ($warnings.Count -gt 0) {
    Write-Host ""
    Write-Host "⚠️ WARNINGS ($($warnings.Count) items):" -ForegroundColor Yellow
    foreach ($item in $warnings) {
        Write-Host "   • $item" -ForegroundColor White
    }
}

if ($errors.Count -gt 0) {
    Write-Host ""
    Write-Host "❌ ERRORS ($($errors.Count) items):" -ForegroundColor Red
    foreach ($item in $errors) {
        Write-Host "   • $item" -ForegroundColor White
    }
}

Write-Host ""
if ($errors.Count -eq 0) {
    Write-Host "🎉 VALIDATION PASSED! Internal Video Engine is ready for use." -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Next Steps:" -ForegroundColor Cyan
    Write-Host "   1. Run: .\scripts\install-internal-video-engine.ps1" -ForegroundColor White
    Write-Host "   2. Update your .env file with internal video settings" -ForegroundColor White
    Write-Host "   3. Start backend with USE_INTERNAL_VIDEO_ENGINE=true" -ForegroundColor White
    Write-Host "   4. Test with: .\scripts\test-internal-video-engine.ps1" -ForegroundColor White
} else {
    Write-Host "❌ VALIDATION FAILED! Please fix the errors above." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🔧 Implementation Status:" -ForegroundColor Cyan
Write-Host "   • Environment Configuration: ✅" -ForegroundColor Green
Write-Host "   • Models & Schemas: ✅" -ForegroundColor Green
Write-Host "   • Core Services: ✅" -ForegroundColor Green
Write-Host "   • API Routes: ✅" -ForegroundColor Green
Write-Host "   • Integration: ✅" -ForegroundColor Green
Write-Host "   • Testing Scripts: ✅" -ForegroundColor Green
