#!/bin/bash
# init-repository.sh

echo "🚀 T-Developer 저장소 초기화 시작..."

# 기본 .gitignore 생성
cat > .gitignore << 'EOF'
# Dependencies
node_modules/
.pnp
.pnp.js

# Testing
coverage/
*.lcov
.nyc_output

# Production
build/
dist/
*.log

# Environment
.env
.env.local
.env.*.local

# AWS
.aws/
*.pem

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Python
__pycache__/
*.py[cod]
*$py.class
.Python
venv/
ENV/

# Terraform
*.tfstate
*.tfstate.*
.terraform/
EOF

# 기본 디렉토리 구조 생성
mkdir -p {backend,frontend,scripts,docs,tests,docker}

# Git 초기화 (이미 초기화되어 있으면 건너뛰기)
if [ ! -d ".git" ]; then
    git init
    echo "✅ Git 저장소 초기화 완료"
else
    echo "✅ Git 저장소가 이미 초기화되어 있습니다"
fi

# 변경사항 추가 및 커밋
git add .
git commit -m "feat: Initial project setup with basic structure" 2>/dev/null || echo "✅ 커밋할 변경사항이 없습니다"

echo "✅ 저장소 초기화 완료!"
echo "📁 생성된 디렉토리:"
echo "  - backend/    (백엔드 코드)"
echo "  - frontend/   (프론트엔드 코드)"
echo "  - scripts/    (유틸리티 스크립트)"
echo "  - docs/       (문서)"
echo "  - tests/      (테스트)"
echo "  - docker/     (Docker 설정)"