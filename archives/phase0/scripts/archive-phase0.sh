#!/bin/bash

# Phase 0 아카이브 스크립트
echo "📦 Phase 0 아카이브 시작..."

# 아카이브 디렉토리 생성
mkdir -p archives/phase0

# 현재 날짜
DATE=$(date +"%Y%m%d_%H%M%S")

# Phase 0 관련 파일들 아카이브
echo "📁 Phase 0 파일들을 아카이브 중..."

# 설정 파일들
cp .env.example archives/phase0/
cp .gitignore archives/phase0/
cp .eslintrc.js archives/phase0/
cp .prettierrc archives/phase0/
cp docker-compose.yml archives/phase0/
cp docker-compose.dev.yml archives/phase0/

# 스크립트들
cp -r scripts/ archives/phase0/scripts/

# 백엔드 설정
mkdir -p archives/phase0/backend
cp backend/package.json archives/phase0/backend/
cp backend/tsconfig.json archives/phase0/backend/
cp backend/jest.config.js archives/phase0/backend/

# 테스트 설정
cp -r backend/tests/ archives/phase0/backend/tests/

# 보안 및 유틸리티
mkdir -p archives/phase0/backend/src
cp -r backend/src/utils/ archives/phase0/backend/src/
cp -r backend/src/security/ archives/phase0/backend/src/
cp -r backend/src/performance/ archives/phase0/backend/src/
cp -r backend/src/agents/ archives/phase0/backend/src/

# GitHub Actions
cp -r .github/ archives/phase0/

# 문서
cp -r docs/ archives/phase0/

# 아카이브 압축
echo "🗜️  아카이브 압축 중..."
cd archives
tar -czf "phase0_${DATE}.tar.gz" phase0/

echo "✅ Phase 0 아카이브 완료!"
echo "📍 아카이브 위치: archives/phase0_${DATE}.tar.gz"

# Phase 0 완료 마크 생성
echo "Phase 0 completed on $(date)" > ../PHASE0_COMPLETED.md
echo "Archive: phase0_${DATE}.tar.gz" >> ../PHASE0_COMPLETED.md

echo "🎉 Phase 0 완료 마크 생성됨: PHASE0_COMPLETED.md"