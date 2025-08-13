#!/bin/bash

echo "🚀 Starting T-Developer monitoring stack..."

# Start monitoring services
docker-compose -f docker-compose.monitoring.yml up -d

echo "✅ Monitoring services started!"
echo ""
echo "📊 Access URLs:"
echo "- Grafana: http://localhost:3001 (admin/admin)"
echo "- Prometheus: http://localhost:9090"
echo "- StatsD: localhost:8125 (UDP)"
echo ""
echo "⏳ Services may take a few moments to fully initialize..."
