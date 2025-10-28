#!/bin/bash
# AutoPro Microservices - Quick Start Script

set -e

echo "🚀 AutoPro Microservices - Quick Start"
echo "========================================"
echo ""

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker: $(docker --version)"
echo "✅ Docker Compose: $(docker-compose --version)"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    cp .env.example .env
    echo "✅ .env file created. Please edit it with your configuration."
    echo ""
    echo "Press ENTER to continue or CTRL+C to exit and edit .env first..."
    read
fi

# Build and start services
echo "🔨 Building and starting all services..."
echo ""

docker-compose up --build -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

# Health check
echo ""
echo "🔍 Checking service health..."
echo ""

services=(
    "lead-service:8001"
    "video-service:8002"
    "social-service:8003"
    "financial-service:8004"
    "referral-service:8005"
    "automation-service:8006"
    "notification-service:8007"
    "analytics-service:8008"
    "whatsapp-service:8009"
    "mcp-service:8010"
)

healthy_count=0
total_count=${#services[@]}

for service in "${services[@]}"; do
    IFS=':' read -r name port <<< "$service"
    if curl -f -s "http://localhost:$port/health/live" > /dev/null 2>&1; then
        echo "✅ $name (port $port) - HEALTHY"
        ((healthy_count++))
    else
        echo "⚠️  $name (port $port) - NOT READY"
    fi
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 AutoPro Microservices Started Successfully!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 Services: $healthy_count/$total_count healthy"
echo ""
echo "🌐 Access Points:"
echo "   • Kong Gateway:      http://localhost:8000"
echo "   • Kong Admin:        http://localhost:8001"
echo "   • Prometheus:        http://localhost:9090"
echo "   • Grafana:           http://localhost:3000 (admin/admin)"
echo "   • Jaeger:            http://localhost:16686"
echo "   • RabbitMQ:          http://localhost:15672 (guest/guest)"
echo ""
echo "🔧 Direct Service Access:"
echo "   • Lead Service:      http://localhost:8001/docs"
echo "   • Video Service:     http://localhost:8002/docs"
echo "   • Social Service:    http://localhost:8003/docs"
echo "   • Financial Service: http://localhost:8004/docs"
echo "   • Referral Service:  http://localhost:8005/docs"
echo ""
echo "📝 Useful Commands:"
echo "   • View logs:         docker-compose logs -f [service-name]"
echo "   • Stop services:     docker-compose down"
echo "   • Restart service:   docker-compose restart [service-name]"
echo "   • Check status:      docker-compose ps"
echo ""
echo "🧪 Test Endpoint:"
echo "   curl http://localhost:8000/api/leads"
echo ""
echo "📖 Documentation:"
echo "   • README.md"
echo "   • ARCHITECTURE.md"
echo "   • DEPLOYMENT_GUIDE.md"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✨ Happy coding!"
echo ""
