#!/bin/bash
# scripts/deploy-ui-agent.sh

set -e

echo "🚀 Starting UI Selection Agent Deployment"

# 1. 검증 실행
echo "📋 Running final validations..."
python -m pytest tests/final_validation/ -v

# 2. 빌드 및 푸시
echo "🔨 Building Docker image..."
docker build -t t-developer/ui-selection-agent:v1.0.0 .
docker push t-developer/ui-selection-agent:v1.0.0

# 3. 배포 전 백업
echo "💾 Creating backup..."
./scripts/backup-ui-agent.sh

# 4. Canary 배포
echo "🐤 Starting canary deployment..."
kubectl apply -f k8s/canary/

# 5. Canary 검증 (10% 트래픽)
echo "✅ Validating canary..."
sleep 300  # 5분 대기

CANARY_ERROR_RATE=$(kubectl exec -n t-developer deploy/prometheus -- \
  promtool query instant 'rate(ui_selection_requests_total{status="error",version="canary"}[5m])' | \
  jq -r '.data.result[0].value[1]')

if (( $(echo "$CANARY_ERROR_RATE > 0.001" | bc -l) )); then
    echo "❌ Canary error rate too high: ${CANARY_ERROR_RATE}"
    kubectl delete -f k8s/canary/
    exit 1
fi

# 6. 전체 배포
echo "🎯 Rolling out to all pods..."
kubectl set image deployment/ui-selection-agent \
  agent=t-developer/ui-selection-agent:v1.0.0 \
  -n t-developer

# 7. 배포 대기
kubectl rollout status deployment/ui-selection-agent -n t-developer

# 8. 최종 검증
echo "🔍 Final verification..."
./scripts/post-deployment-check.sh

echo "✅ UI Selection Agent v1.0.0 deployed successfully!"

# 9. 알림 발송
curl -X POST $SLACK_WEBHOOK_URL \
  -H 'Content-Type: application/json' \
  -d '{
    "text": "🎉 UI Selection Agent v1.0.0 deployed successfully!",
    "attachments": [{
      "color": "good",
      "fields": [
        {"title": "Version", "value": "v1.0.0", "short": true},
        {"title": "Environment", "value": "Production", "short": true},
        {"title": "Replicas", "value": "5", "short": true},
        {"title": "Status", "value": "Healthy", "short": true}
      ]
    }]
  }'