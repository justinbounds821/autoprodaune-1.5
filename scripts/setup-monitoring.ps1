# AutoPro Daune - Monitoring Setup Script
Write-Host "📊 Setting up Monitoring Stack for AutoPro Daune..." -ForegroundColor Green

# Check if Docker is running
try {
    docker version | Out-Null
    Write-Host "✅ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not running. Please start Docker Desktop first." -ForegroundColor Red
    exit 1
}

# Start Monitoring Stack
Write-Host "🚀 Starting Monitoring Stack (Prometheus + Grafana + Redis)..." -ForegroundColor Yellow
docker compose -f docker-compose.monitoring.yml up -d

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Monitoring stack started successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📊 Monitoring URLs:" -ForegroundColor Cyan
    Write-Host "   • Grafana Dashboard: http://localhost:3001" -ForegroundColor White
    Write-Host "   • Prometheus: http://localhost:9090" -ForegroundColor White
    Write-Host "   • AlertManager: http://localhost:9093" -ForegroundColor White
    Write-Host "   • Node Exporter: http://localhost:9100" -ForegroundColor White
    Write-Host ""
    Write-Host "🔑 Default Credentials:" -ForegroundColor Cyan
    Write-Host "   • Grafana: admin / autopro123" -ForegroundColor White
    Write-Host "   • Redis: no password (local development)" -ForegroundColor White
    Write-Host ""
    Write-Host "📈 Grafana Dashboard Import:" -ForegroundColor Cyan
    Write-Host "   1. Go to http://localhost:3001" -ForegroundColor White
    Write-Host "   2. Login with admin/autopro123" -ForegroundColor White
    Write-Host "   3. Import dashboard from monitoring/grafana-dashboard.json" -ForegroundColor White
    Write-Host ""
    Write-Host "🔧 Make sure your backend is running on http://localhost:8001" -ForegroundColor Yellow
    Write-Host "   The monitoring stack will automatically scrape metrics from your API" -ForegroundColor Gray
} else {
    Write-Host "❌ Failed to start monitoring stack" -ForegroundColor Red
    exit 1
}

Write-Host "🎉 Monitoring setup completed!" -ForegroundColor Green
