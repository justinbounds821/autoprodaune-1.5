# AutoPro Daune - Redis Setup Script
Write-Host "🔴 Setting up Redis for AutoPro Daune..." -ForegroundColor Green

# Check if Docker is running
try {
    docker version | Out-Null
    Write-Host "✅ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not running. Please start Docker Desktop first." -ForegroundColor Red
    exit 1
}

# Start Redis
Write-Host "🚀 Starting Redis container..." -ForegroundColor Yellow
docker compose -f docker-compose.redis.yml up -d

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Redis started successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🔗 Redis Information:" -ForegroundColor Cyan
    Write-Host "   • Host: localhost" -ForegroundColor White
    Write-Host "   • Port: 6379" -ForegroundColor White
    Write-Host "   • Password: autopro123" -ForegroundColor White
    Write-Host "   • URL: redis://localhost:6379/0" -ForegroundColor White
    Write-Host ""
    Write-Host "🔧 Update your backend .env file:" -ForegroundColor Cyan
    Write-Host "   REDIS_URL=redis://localhost:6379/0" -ForegroundColor White
    Write-Host "   REDIS_HOST=localhost" -ForegroundColor White
    Write-Host "   REDIS_PORT=6379" -ForegroundColor White
    Write-Host ""
    Write-Host "📊 To view Redis data, you can use:" -ForegroundColor Cyan
    Write-Host "   • Redis CLI: redis-cli -h localhost -p 6379" -ForegroundColor White
    Write-Host "   • RedisInsight: docker run -d --name redisinsight -p 5540:5540 redis/redisinsight" -ForegroundColor White
} else {
    Write-Host "❌ Failed to start Redis" -ForegroundColor Red
    exit 1
}

Write-Host "🎉 Redis setup completed!" -ForegroundColor Green
