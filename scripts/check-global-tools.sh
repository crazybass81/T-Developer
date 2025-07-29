#!/bin/bash
# scripts/check-global-tools.sh

echo "🔍 개발 도구 설치 상태 확인..."

check_tool() {
    local tool=$1
    local cmd=$2
    
    if command -v $cmd &> /dev/null; then
        echo "✅ $tool: $(${cmd} --version 2>/dev/null | head -1)"
    elif npx $cmd --version &> /dev/null; then
        echo "📦 $tool: $(npx ${cmd} --version 2>/dev/null | head -1) (local)"
    else
        echo "❌ $tool: Not installed"
    fi
}

check_tool "TypeScript" "tsc"
check_tool "AWS CDK" "cdk"
check_tool "Serverless" "serverless"
check_tool "PM2" "pm2"
check_tool "Lerna" "lerna"

echo -e "\n📋 권장사항:"
echo "- 전역 설치 권한이 없는 경우 npx 사용"
echo "- 또는 scripts/install-global-tools-local.sh 실행"