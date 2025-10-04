# AutoPro Daune - Configure Real API Keys
# This script adds the real API keys extracted from screenshots

Write-Host "🔑 AutoPro Daune - API Keys Configuration" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

$envPath = "services\api\.env"

# Check if .env exists
if (Test-Path $envPath) {
    Write-Host "⚠️  .env file already exists!" -ForegroundColor Yellow
    $overwrite = Read-Host "Do you want to append real keys? (y/n)"
    if ($overwrite -ne 'y') {
        Write-Host "❌ Cancelled" -ForegroundColor Red
        exit
    }
} else {
    # Copy from example
    if (Test-Path "services\api\.env.backend.example") {
        Copy-Item "services\api\.env.backend.example" $envPath
        Write-Host "✅ Created .env from example" -ForegroundColor Green
    } else {
        Write-Host "❌ .env.backend.example not found!" -ForegroundColor Red
        exit
    }
}

Write-Host ""
Write-Host "📝 Adding real API keys..." -ForegroundColor Cyan

# Append real keys
$realKeys = @"

# ============================================
# REAL API KEYS - Configured $(Get-Date -Format 'yyyy-MM-dd HH:mm')
# ============================================

# ElevenLabs Voice Cloning (REAL KEY ✅)
ELEVENLABS_API_KEY=sk_fbb9a0055155cfcb8b4c9575df1427ff6f2f64efa832c84f3
ELEVENLABS_VOICE_ID=manole_voice

# TikTok API (REAL CLIENT CREDENTIALS ✅)
TIKTOK_CLIENT_KEY=awna26k858tnrwwn
TIKTOK_CLIENT_SECRET=u4J3JYbSD30WKFFYLUdPfwFiuabhqzc5
# TIKTOK_ACCESS_TOKEN=get-via-oauth-flow
# TIKTOK_REFRESH_TOKEN=get-via-oauth-flow
# TIKTOK_USER_ID=get-after-oauth

# YouTube API (REAL API KEY ✅)
YOUTUBE_API_KEY=AIzaSyDj7oPCt9Z6R6xMBqIynEhFhadWjbJ3voI

# WhatsApp (REAL GROUP LINK ✅)
WHATSAPP_LINK=https://chat.whatsapp.com/Kz8GEkh4MJV4qg8JmiQmZL
WHATSAPP_DIRECT_NUMBER=40700000000

# Video Storage: Use Supabase Storage (already configured)
# SUPABASE_URL + SUPABASE_SERVICE_KEY already configured above
# Videos will upload to: https://orctxxpyiqzbordibqxi.supabase.co/storage/v1/object/public/video-outputs/{job_id}.mp4
# Free tier: 1 GB storage + 2 GB bandwidth/month (sufficient for ~100 videos/month)

# Cloudflare R2 (OPTIONAL - only if Supabase storage exceeds limits)
# CLOUDFLARE_R2_ENDPOINT=https://026d4eb7409b0baea2767863f22a76c1.r2.cloudflarestorage.com
# CLOUDFLARE_R2_BUCKET=autoprodaune
# AWS_ACCESS_KEY_ID=20ee531191486$acd521e47c2dcd70dd
# AWS_SECRET_ACCESS_KEY=qahGHManKdmqqVQFQ-PrVY4-gb-Mk2c_M
# AWS_REGION=auto

# Video Generator Provider
VEO_PROVIDER=ManoleVideoGenerator
EDGE_TTS_VOICE=ro-RO-EmilNeural

# Automation
AUTOMATION_ENABLED=true
DAILY_VIDEO_COUNT=3
"@

# Write to file
$realKeys | Out-File -FilePath $envPath -Encoding UTF8 -Append

Write-Host "✅ Real API keys added to .env" -ForegroundColor Green
Write-Host ""

# Summary
Write-Host "📊 Configuration Summary:" -ForegroundColor Cyan
Write-Host "========================" -ForegroundColor Cyan
Write-Host ""
Write-Host "✅ ElevenLabs: Voice cloning ACTIVE" -ForegroundColor Green
Write-Host "✅ TikTok: Client credentials configured (need OAuth token)" -ForegroundColor Yellow
Write-Host "✅ YouTube: API key configured" -ForegroundColor Green
Write-Host "✅ WhatsApp: Group link configured" -ForegroundColor Green
Write-Host "✅ Supabase Storage: Using built-in storage (1GB free, already configured)" -ForegroundColor Green
Write-Host ""
Write-Host "⚠️  Still need (optional):" -ForegroundColor Yellow
Write-Host "   - TikTok access token (complete OAuth flow)" -ForegroundColor White
Write-Host "   - Instagram access token (from Facebook)" -ForegroundColor White
Write-Host ""
Write-Host "🎬 READY TO TEST:" -ForegroundColor Green
Write-Host "   1. Manole Video Generator (ElevenLabs voice + Supabase upload)" -ForegroundColor White
Write-Host "   2. YouTube follower tracking" -ForegroundColor White
Write-Host "   3. Videos auto-upload to Supabase Storage (1GB free)!" -ForegroundColor White
Write-Host ""
Write-Host "🚀 Start the system with:" -ForegroundColor Cyan
Write-Host "   .\scripts\start-all.ps1" -ForegroundColor White
Write-Host ""
Write-Host "💡 After video generation, get public URL:" -ForegroundColor Cyan
Write-Host "   https://orctxxpyiqzbordibqxi.supabase.co/storage/v1/object/public/video-outputs/{job_id}.mp4" -ForegroundColor White
Write-Host ""
