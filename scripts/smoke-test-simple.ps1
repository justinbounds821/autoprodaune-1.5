# FAZA 5.9: Smoke Test Script (nu creează duplicate, doar execută)
Write-Host "Health:";        curl.exe http://127.0.0.1:8001/health
Write-Host "Automation:";    curl.exe http://127.0.0.1:8001/api/automation/status
Write-Host "Payments:";      curl.exe http://127.0.0.1:8001/api/financial/payments
Write-Host "HeyGen avatars:";curl.exe http://127.0.0.1:8001/api/video/video/heygen/avatars
Write-Host "HeyGen generate:";curl.exe -X POST http://127.0.0.1:8001/api/video/video/heygen/generate -H "Content-Type: application/json" -d "{}"
Write-Host "Growth status:"; curl.exe http://127.0.0.1:8001/api/growth-engine/growth-status
