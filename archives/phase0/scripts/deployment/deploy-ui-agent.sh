#!/bin/bash
# UI Selection Agent Deployment Script

set -e

echo "🚀 Starting UI Selection Agent Deployment"

VERSION="v1.0.0"
NAMESPACE="t-developer"

# 1. Pre-deployment validation
echo "📋 Running pre-deployment checks..."
python -m pytest backend/tests/agents/ui_selection/ -v
if [ $? -ne 0 ]; then
    echo "❌ Tests failed"
    exit 1
fi

# 2. Build Docker image
echo "🔨 Building Docker image..."
docker build -t t-developer/ui-selection-agent:${VERSION} backend/

# 3. Create namespace if not exists
kubectl create namespace ${NAMESPACE} --dry-run=client -o yaml | kubectl apply -f -

# 4. Apply Kubernetes manifests
echo "📦 Deploying to Kubernetes..."
cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ui-selection-agent
  namespace: ${NAMESPACE}
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ui-selection-agent
  template:
    metadata:
      labels:
        app: ui-selection-agent
    spec:
      containers:
      - name: agent
        image: t-developer/ui-selection-agent:${VERSION}
        ports:
        - containerPort: 8000
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: ui-selection-agent-service
  namespace: ${NAMESPACE}
spec:
  selector:
    app: ui-selection-agent
  ports:
  - port: 80
    targetPort: 8000
EOF

# 5. Wait for rollout
echo "⏳ Waiting for deployment..."
kubectl rollout status deployment/ui-selection-agent -n ${NAMESPACE} --timeout=300s

# 6. Health check
echo "🔍 Running health checks..."
sleep 30

READY_PODS=$(kubectl get pods -l app=ui-selection-agent -n ${NAMESPACE} -o jsonpath='{.items[?(@.status.phase=="Running")].metadata.name}' | wc -w)

if [ "$READY_PODS" -ge 3 ]; then
    echo "✅ Deployment successful: ${VERSION}"
    echo "📊 Ready pods: ${READY_PODS}/3"
else
    echo "❌ Deployment failed: Only ${READY_PODS}/3 pods ready"
    exit 1
fi

echo "🎉 UI Selection Agent ${VERSION} deployed successfully!"