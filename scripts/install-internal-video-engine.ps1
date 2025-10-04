# ============================================
# Internal Video Engine - Dependencies Installation
# ============================================

Write-Host "🚀 Installing Internal Video Engine Dependencies..." -ForegroundColor Green
Write-Host ""

# Check if we're in the right directory
if (!(Test-Path "services/api/app/main.py")) {
    Write-Host "❌ Error: Please run this script from the project root directory" -ForegroundColor Red
    exit 1
}

Write-Host "📁 Project root: $(Get-Location)" -ForegroundColor Gray
Write-Host ""

# 1) Common dependencies
Write-Host "📦 Installing common dependencies..." -ForegroundColor Yellow
pip install fastapi uvicorn httpx pydantic moviepy pydub opencv-python ffmpeg-python
Write-Host "✅ Common dependencies installed" -ForegroundColor Green

# 2) PyTorch (CPU version - choose appropriate for your system)
Write-Host "🔥 Installing PyTorch (CPU version)..." -ForegroundColor Yellow
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
Write-Host "✅ PyTorch installed" -ForegroundColor Green

# 3) Add third_party directory and submodules
Write-Host "📁 Setting up third-party modules..." -ForegroundColor Yellow
if (!(Test-Path "third_party")) {
    New-Item -ItemType Directory -Path "third_party"
}

# Initialize git submodules
Write-Host "   Adding SadTalker submodule..." -ForegroundColor Cyan
git submodule add https://github.com/OpenTalker/SadTalker third_party/SadTalker

Write-Host "   Adding Wav2Lip submodule..." -ForegroundColor Cyan
git submodule add https://github.com/Rudrabha/Wav2Lip third_party/Wav2Lip

# Install requirements for submodules
Write-Host "📦 Installing SadTalker requirements..." -ForegroundColor Yellow
pip install -r third_party/SadTalker/requirements.txt

Write-Host "📦 Installing Wav2Lip requirements..." -ForegroundColor Yellow
pip install -r third_party/Wav2Lip/requirements.txt

# 4) Download model weights
Write-Host "⬇️ Downloading model weights..." -ForegroundColor Yellow

# SadTalker models
Write-Host "   Downloading SadTalker models..." -ForegroundColor Cyan
try {
    python third_party/SadTalker/scripts/download_models.py
    Write-Host "✅ SadTalker models downloaded" -ForegroundColor Green
} catch {
    Write-Host "⚠️ SadTalker download script failed, will use manual download" -ForegroundColor Yellow
}

# Wav2Lip model
Write-Host "   Downloading Wav2Lip model..." -ForegroundColor Cyan
$wav2lipPath = "third_party/Wav2Lip/checkpoints"
if (!(Test-Path $wav2lipPath)) {
    New-Item -ItemType Directory -Path $wav2lipPath -Force
}

$modelUrl = "https://huggingface.co/spaces/akshay-kr/Real-Time-Wav2Lip/resolve/main/Wav2Lip.pth"
$modelPath = "$wav2lipPath/Wav2Lip.pth"

if (!(Test-Path $modelPath)) {
    Write-Host "   Downloading Wav2Lip.pth..." -ForegroundColor Cyan
    Invoke-WebRequest -Uri $modelUrl -OutFile $modelPath
    Write-Host "✅ Wav2Lip model downloaded" -ForegroundColor Green
} else {
    Write-Host "✅ Wav2Lip model already exists" -ForegroundColor Green
}

# 5) Create assets directory
Write-Host "📁 Creating assets directory..." -ForegroundColor Yellow
$assetsPath = "services/api/assets"
if (!(Test-Path $assetsPath)) {
    New-Item -ItemType Directory -Path $assetsPath -Force
}

# Create a placeholder background image
$bgImagePath = "$assetsPath/bg.jpg"
if (!(Test-Path $bgImagePath)) {
    Write-Host "   Creating placeholder background image..." -ForegroundColor Cyan
    # Create a simple 1280x720 placeholder image using PowerShell
    Add-Type -AssemblyName System.Drawing
    $bitmap = New-Object System.Drawing.Bitmap(1280, 720)
    $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
    $brush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::LightGray)
    $graphics.FillRectangle($brush, 0, 0, 1280, 720)
    $font = New-Object System.Drawing.Font("Arial", 48, [System.Drawing.FontStyle]::Bold)
    $textBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::DarkGray)
    $graphics.DrawString("AutoPro Daune", $font, $textBrush, 400, 300)
    $bitmap.Save($bgImagePath, [System.Drawing.Imaging.ImageFormat]::Jpeg)
    $graphics.Dispose()
    $bitmap.Dispose()
    Write-Host "✅ Placeholder background image created" -ForegroundColor Green
}

Write-Host ""
Write-Host "🎉 Internal Video Engine Dependencies Installation Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 What was installed:" -ForegroundColor Cyan
Write-Host "   • Common dependencies (FastAPI, MoviePy, OpenCV, FFmpeg)" -ForegroundColor White
Write-Host "   • PyTorch (CPU version)" -ForegroundColor White
Write-Host "   • SadTalker submodule and requirements" -ForegroundColor White
Write-Host "   • Wav2Lip submodule and requirements" -ForegroundColor White
Write-Host "   • Model weights (SadTalker + Wav2Lip)" -ForegroundColor White
Write-Host "   • Assets directory with placeholder background" -ForegroundColor White
Write-Host ""
Write-Host "🔧 Next steps:" -ForegroundColor Cyan
Write-Host "   1. Update your .env file with internal video engine settings" -ForegroundColor White
Write-Host "   2. Run the backend with USE_INTERNAL_VIDEO_ENGINE=true" -ForegroundColor White
Write-Host "   3. Test with scripts/test-internal-video-engine.ps1" -ForegroundColor White
Write-Host ""
Write-Host "💡 Note: If SadTalker download failed, manually download models from:" -ForegroundColor Yellow
Write-Host "   https://github.com/OpenTalker/SadTalker#installation" -ForegroundColor White
