#!/bin/bash

# T-Developer MVP - 문서 정리 스크립트
echo "📚 Organizing documentation files..."

cd /home/ec2-user/T-DeveloperMVP

# docs 디렉토리 구조 생성
mkdir -p docs/{agents,cleanup-reports,phase-reports}

echo "Moving agent documentation..."
# 에이전트별 문서들을 docs/agents로 이동
find backend/src/agents/implementations -name "*.md" -exec mv {} docs/agents/ \;

# README 파일들도 이동하되 이름 변경
find backend/src/agents/implementations -name "README.md" -path "*/ui_selection/*" -exec mv {} docs/agents/ui_selection_README.md \; 2>/dev/null || true
find backend/src/agents/implementations -name "README.md" -path "*/parser/*" -exec mv {} docs/agents/parser_README.md \; 2>/dev/null || true

# cleanup reports 이동
mv backend/src/agents/implementations/docs/cleanup_reports/*.md docs/cleanup-reports/ 2>/dev/null || true

# Phase 보고서들 이동
mv PHASE*_COMPLETION.md docs/phase-reports/ 2>/dev/null || true

# 빈 디렉토리 제거
rmdir backend/src/agents/implementations/docs/cleanup_reports 2>/dev/null || true
rmdir backend/src/agents/implementations/docs 2>/dev/null || true

# 최종 상태 보고서는 루트에 유지
echo "✅ Documentation organized!"
echo ""
echo "📁 New documentation structure:"
echo "docs/"
echo "├── agents/           # Agent-specific documentation"
echo "├── cleanup-reports/  # Cleanup reports"
echo "└── phase-reports/    # Phase completion reports"
echo ""
echo "📋 Files in root:"
ls -1 *.md 2>/dev/null | head -5