#!/bin/bash

echo "📦 Phase 0 아카이브 시작..."

# 1. Phase 0 태그 생성
git tag -a "phase0-complete" -m "Phase 0: 사전 준비 및 환경 설정 완료"

# 2. 문서 정리
mkdir -p docs/archive/phase0
cp -r docs/phases docs/archive/phase0/ 2>/dev/null || true

# 3. 설정 파일 백업
mkdir -p backups/phase0
cp .env.example backups/phase0/ 2>/dev/null || true
cp package.json backups/phase0/
cp commitlint.config.js backups/phase0/ 2>/dev/null || true

# 4. 통계 생성
echo "📊 Phase 0 통계 생성 중..."
cat > docs/archive/phase0/statistics.md << EOF
# Phase 0 통계

## 코드 통계
- 총 파일 수: $(find . -type f -name "*.ts" -o -name "*.js" | wc -l)
- TypeScript 라인 수: $(find . -name "*.ts" -exec wc -l {} + 2>/dev/null | tail -1 | awk '{print $1}' || echo "0")
- 테스트 파일 수: $(find . -name "*.test.ts" -o -name "*.spec.ts" | wc -l)

## Git 통계
- 총 커밋 수: $(git rev-list --count HEAD)
- 기여자 수: $(git shortlog -sn | wc -l)

## 의존성
- Backend 패키지: $(cd backend 2>/dev/null && npm ls --depth=0 2>/dev/null | wc -l || echo "N/A")

생성일: $(date)
EOF

echo "✅ Phase 0 아카이브 완료!"
echo "📁 아카이브 위치: docs/archive/phase0/"