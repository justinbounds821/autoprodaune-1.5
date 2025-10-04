# ============================================
# Internal Video Engine - Testing Script
# ============================================

Write-Host "🧪 Testing Internal Video Engine..." -ForegroundColor Green
Write-Host ""

# Check if we're in the right directory
if (!(Test-Path "services/api/app/main.py")) {
    Write-Host "❌ Error: Please run this script from the project root directory" -ForegroundColor Red
    exit 1
}

# Configuration
$BACKEND_URL = "http://127.0.0.1:8001"
$TEST_AVATAR_URL = "https://raw.githubusercontent.com/OpenTalker/SadTalker/main/examples/source_image/full_body_1.png"

Write-Host "📁 Project root: $(Get-Location)" -ForegroundColor Gray
Write-Host "🌐 Backend URL: $BACKEND_URL" -ForegroundColor Gray
Write-Host ""

# Test 1: Health Check
Write-Host "1️⃣ Testing Internal Video Engine Health..." -ForegroundColor Yellow
try {
    $healthResponse = Invoke-RestMethod -Uri "$BACKEND_URL/api/video/video/heygen/health" -Method GET
    Write-Host "✅ Health Check Response:" -ForegroundColor Green
    Write-Host "   Engine Enabled: $($healthResponse.engine_enabled)" -ForegroundColor White
    Write-Host "   Backend: $($healthResponse.backend)" -ForegroundColor White
    Write-Host "   SadTalker Available: $($healthResponse.sadtalker_available)" -ForegroundColor White
    Write-Host "   Wav2Lip Available: $($healthResponse.wav2lip_available)" -ForegroundColor White
    Write-Host "   FFmpeg Available: $($healthResponse.ffmpeg_available)" -ForegroundColor White
    Write-Host "   ElevenLabs Configured: $($healthResponse.elevenlabs_configured)" -ForegroundColor White
} catch {
    Write-Host "❌ Health Check Failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Test 2: List Avatars
Write-Host "2️⃣ Testing Avatar List..." -ForegroundColor Yellow
try {
    $avatarsResponse = Invoke-RestMethod -Uri "$BACKEND_URL/api/video/video/heygen/avatars" -Method GET
    Write-Host "✅ Avatars Response:" -ForegroundColor Green
    foreach ($avatar in $avatarsResponse.items) {
        Write-Host "   ID: $($avatar.id) - $($avatar.label)" -ForegroundColor White
    }
} catch {
    Write-Host "❌ Avatar List Failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Test 3: Generate Video (JSON)
Write-Host "3️⃣ Testing Video Generation (JSON)..." -ForegroundColor Yellow
try {
    $generatePayload = @{
        script = "Bună! Sunt avocatul tău virtual AutoPro Daune. Te ajut cu daunele auto."
        quality = "high"
        style = "realistic"
        voice_id = "Rachel"
        avatar_image_url = $TEST_AVATAR_URL
    } | ConvertTo-Json

    Write-Host "   Sending generation request..." -ForegroundColor Cyan
    $generateResponse = Invoke-RestMethod -Uri "$BACKEND_URL/api/video/video/heygen/generate-json" -Method POST -Body $generatePayload -ContentType "application/json"
    
    Write-Host "✅ Generation Response:" -ForegroundColor Green
    Write-Host "   Job ID: $($generateResponse.job_id)" -ForegroundColor White
    Write-Host "   Provider: $($generateResponse.provider)" -ForegroundColor White
    Write-Host "   Status: $($generateResponse.status)" -ForegroundColor White
    
    $jobId = $generateResponse.job_id
    
    # Test 4: Check Job Status (loop until completed or failed)
    Write-Host ""
    Write-Host "4️⃣ Monitoring Job Status..." -ForegroundColor Yellow
    $maxAttempts = 30
    $attempt = 0
    $completed = $false
    
    do {
        $attempt++
        Start-Sleep -Seconds 5
        
        try {
            $statusResponse = Invoke-RestMethod -Uri "$BACKEND_URL/api/video/video/heygen/status/$jobId" -Method GET
            Write-Host "   Attempt $attempt/$maxAttempts - Status: $($statusResponse.status)" -ForegroundColor Cyan
            
            if ($statusResponse.status -eq "completed") {
                Write-Host "✅ Job Completed Successfully!" -ForegroundColor Green
                Write-Host "   Video URL: $($statusResponse.video_url)" -ForegroundColor White
                Write-Host "   Processing Time: $($statusResponse.meta.processing_time)s" -ForegroundColor White
                $completed = $true
                break
            } elseif ($statusResponse.status -eq "failed") {
                Write-Host "❌ Job Failed: $($statusResponse.error)" -ForegroundColor Red
                break
            }
        } catch {
            Write-Host "⚠️ Status check failed: $($_.Exception.Message)" -ForegroundColor Yellow
        }
        
    } while ($attempt -lt $maxAttempts -and !$completed)
    
    if (!$completed -and $attempt -eq $maxAttempts) {
        Write-Host "⏰ Job monitoring timeout after $maxAttempts attempts" -ForegroundColor Yellow
    }
    
    # Test 5: Download Video (if completed)
    if ($completed) {
        Write-Host ""
        Write-Host "5️⃣ Testing Video Download..." -ForegroundColor Yellow
        try {
            $downloadUrl = "$BACKEND_URL/api/video/video/heygen/download/$jobId"
            $outputFile = "test_video_$jobId.mp4"
            
            Write-Host "   Downloading video to: $outputFile" -ForegroundColor Cyan
            Invoke-WebRequest -Uri $downloadUrl -OutFile $outputFile
            
            if (Test-Path $outputFile) {
                $fileSize = (Get-Item $outputFile).Length
                Write-Host "✅ Video Downloaded Successfully!" -ForegroundColor Green
                Write-Host "   File: $outputFile" -ForegroundColor White
                Write-Host "   Size: $([math]::Round($fileSize/1MB, 2)) MB" -ForegroundColor White
            } else {
                Write-Host "❌ Video file not found after download" -ForegroundColor Red
            }
        } catch {
            Write-Host "❌ Video Download Failed: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
    
} catch {
    Write-Host "❌ Video Generation Failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Test 6: Form Data Generation
Write-Host "6️⃣ Testing Video Generation (Form Data)..." -ForegroundColor Yellow
try {
    $formData = @{
        script = "Test form data generation pentru AutoPro Daune."
        avatar_id = "internal_default"
        voice_id = "Rachel"
        style = "realistic"
        quality = "high"
        language = "ro"
        avatar_image_url = $TEST_AVATAR_URL
    }
    
    Write-Host "   Sending form data request..." -ForegroundColor Cyan
    $formResponse = Invoke-RestMethod -Uri "$BACKEND_URL/api/video/video/heygen/generate" -Method POST -Body $formData -ContentType "multipart/form-data"
    
    Write-Host "✅ Form Generation Response:" -ForegroundColor Green
    Write-Host "   Job ID: $($formResponse.job_id)" -ForegroundColor White
    Write-Host "   Provider: $($formResponse.provider)" -ForegroundColor White
    
} catch {
    Write-Host "❌ Form Generation Failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "🎉 Internal Video Engine Testing Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Test Summary:" -ForegroundColor Cyan
Write-Host "   • Health Check: API status and dependencies" -ForegroundColor White
Write-Host "   • Avatar List: Available avatars" -ForegroundColor White
Write-Host "   • JSON Generation: Video generation with JSON payload" -ForegroundColor White
Write-Host "   • Status Monitoring: Job progress tracking" -ForegroundColor White
Write-Host "   • Video Download: Generated video retrieval" -ForegroundColor White
Write-Host "   • Form Generation: Video generation with form data" -ForegroundColor White
Write-Host ""
Write-Host "💡 Tips:" -ForegroundColor Yellow
Write-Host "   • Set USE_INTERNAL_VIDEO_ENGINE=true in .env to enable" -ForegroundColor White
Write-Host "   • Configure ELEVENLABS_API_KEY for better TTS quality" -ForegroundColor White
Write-Host "   • Use high-quality avatar images (1024px+) for best results" -ForegroundColor White
Write-Host "   • Processing time depends on video length and complexity" -ForegroundColor White
