#!/bin/bash
# init-repository.sh - Git 저장소 초기화 스크립트

echo "🔧 Git 저장소 초기화 중..."

# Git 초기화 (이미 초기화된 경우 스킵)
if [ ! -d ".git" ]; then
    git init
    echo "✅ Git 저장소 초기화 완료"
else
    echo "ℹ️ Git 저장소가 이미 초기화되어 있습니다"
fi

# 기본 브랜치를 main으로 설정
git config init.defaultBranch main
git branch -M main

# Git 사용자 정보 확인
if [ -z "$(git config user.name)" ] || [ -z "$(git config user.email)" ]; then
    echo "⚠️ Git 사용자 정보가 설정되지 않았습니다"
    echo "다음 명령으로 설정하세요:"
    echo "git config --global user.name \"Your Name\""
    echo "git config --global user.email \"your.email@example.com\""
fi

# 현재 상태 확인
echo ""
echo "📊 현재 Git 상태:"
git status --short

echo ""
echo "✅ 저장소 초기화 완료!"
echo ""
echo "📋 다음 단계:"
echo "1. 원격 저장소 추가: git remote add origin <repository-url>"
echo "2. 변경사항 푸시: git push -u origin main"