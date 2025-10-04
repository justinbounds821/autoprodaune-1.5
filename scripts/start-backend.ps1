# FAZA 5.9: Scripts PS (nu creează duplicate, doar execută)
cd services\api
$env:BACKEND_CORS_ORIGINS="http://localhost:3006,http://127.0.0.1:3006,http://localhost:3007,http://127.0.0.1:3007"
$env:RATE_LIMIT_MODE="memory"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload