#!/bin/bash

# T-Developer MVP - 불필요한 파일 정리 스크립트
echo "🧹 T-Developer MVP - Cleaning up unnecessary files..."

# 작업 디렉토리로 이동
cd /home/ec2-user/T-DeveloperMVP

# 백업 파일 목록 생성
echo "📋 Creating list of files to remove..."

# 1. 중복된 complete 파일들 제거
echo "Removing duplicate *_complete.py files..."
find ./backend/src/agents/implementations -name "*_complete.py" -type f -delete

# 2. 백업 파일 제거
echo "Removing backup files..."
find ./backend/src/agents/implementations -name "*_backup.py" -type f -delete
find . -name "*.bak" -type f -delete
find . -name "*~" -type f -delete

# 3. 중복된 config 파일 정리 (오래된 것 제거)
echo "Cleaning duplicate config files..."
rm -f ./backend/src/config/agno-config.py  # agno_config.py를 사용
rm -f ./backend/src/config/agent-squad-example.env  # 예제 파일
rm -f ./backend/src/config/agno-example.env  # 예제 파일

# 4. 빈 __init__.py 파일들은 유지 (Python 패키지 구조에 필요)

# 5. 테스트 파일들은 유지 (나중에 필요할 수 있음)

# 6. 임시 파일 제거
echo "Removing temporary files..."
find . -name "*.tmp" -type f -delete
find . -name "*.swp" -type f -delete
find . -name ".DS_Store" -type f -delete

# 7. 빈 디렉토리 제거
echo "Removing empty directories..."
find ./backend/src -type d -empty -delete

# 8. Phase 문서 파일들 정리 (백업)
echo "Organizing phase documentation..."
mkdir -p ./docs/phases-backup
cp ./backend/phase*.md ./docs/phases-backup/ 2>/dev/null || true
rm -f ./backend/phase*.md

# 9. 중복된 테스트 agent 파일 제거
rm -f ./backend/src/agents/implementations/test-agent.ts

echo "✅ Cleanup completed!"
echo ""
echo "📊 Summary of cleanup:"
echo "- Removed duplicate *_complete.py files"
echo "- Removed backup files (*_backup.py, *.bak, *~)"
echo "- Cleaned duplicate config files"
echo "- Removed temporary files (*.tmp, *.swp, .DS_Store)"
echo "- Removed empty directories"
echo "- Organized phase documentation"
echo ""
echo "⚠️ Note: Test files were preserved for future use"