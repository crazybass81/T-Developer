#!/bin/bash

# T-Developer MVP - 최종 정리 스크립트
echo "🔧 T-Developer MVP - Final cleanup..."

cd /home/ec2-user/T-DeveloperMVP/backend/src

echo "1. Consolidating logger files..."
# utils/logger.ts 제거 (config/logger.ts가 더 완전함)
rm -f utils/logger.ts

echo "2. Checking for duplicate utility files..."
# 중복된 validator 파일들 확인
find . -name "validator.ts" -exec ls -la {} \;

echo ""
echo "3. Removing empty utility directories..."
# 빈 utils 디렉토리가 있다면 제거
find . -type d -name "utils" -empty -delete 2>/dev/null || true

echo ""
echo "4. Consolidating authentication files..."
# auth.ts 파일들 위치 확인
find . -name "auth.ts" -exec echo "Auth file: {}" \;

echo ""
echo "5. Cleaning up index.ts files..."
# 빈 index.ts 파일들 확인
echo "Index files found:"
find . -name "index.ts" -size 0 -exec echo "Empty index.ts: {}" \;

echo ""
echo "6. Creating consolidated utilities..."
mkdir -p consolidated/utils
# 남은 유틸리티들을 한 곳으로 모으기 (필요시)

echo ""
echo "✅ Final cleanup completed!"
echo ""
echo "📊 Current file structure summary:"
echo "Agents:"
find agents -type f -name "*.ts" | wc -l | xargs echo -n; echo " TypeScript files"
echo "Config:"
find config -type f -name "*.ts" | wc -l | xargs echo -n; echo " TypeScript files"
echo "Data:"
find data -type f -name "*.ts" | wc -l | xargs echo -n; echo " TypeScript files"
echo "Monitoring:"
find monitoring -type f -name "*.ts" 2>/dev/null | wc -l | xargs echo -n; echo " TypeScript files"
echo "Routing:"
find routing -type f -name "*.ts" 2>/dev/null | wc -l | xargs echo -n; echo " TypeScript files"
echo "Session:"
find session -type f -name "*.ts" 2>/dev/null | wc -l | xargs echo -n; echo " TypeScript files"