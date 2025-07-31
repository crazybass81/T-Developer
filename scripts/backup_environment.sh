#!/bin/bash
# scripts/backup_environment.sh

BACKUP_DIR="backup/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

echo "💾 환경 백업 시작: $BACKUP_DIR"

# 1. Python 환경 정보
if command -v pip &> /dev/null; then
    pip freeze > "$BACKUP_DIR/pip_freeze.txt"
    pip list --format=json > "$BACKUP_DIR/pip_list.json"
fi

python3 -V > "$BACKUP_DIR/python_version.txt"
if command -v pip &> /dev/null; then
    pip -V >> "$BACKUP_DIR/python_version.txt"
fi

# 2. 시스템 정보
uname -a > "$BACKUP_DIR/system_info.txt"
cat /etc/os-release >> "$BACKUP_DIR/system_info.txt" 2>/dev/null || true

# 3. 환경 변수
env | grep -E "PYTHON|PIP|PATH" > "$BACKUP_DIR/env_vars.txt"

# 4. pip 설정
if command -v pip &> /dev/null; then
    pip config list > "$BACKUP_DIR/pip_config.txt" 2>/dev/null || echo "No pip config" > "$BACKUP_DIR/pip_config.txt"
fi

# 5. 가상환경 메타데이터
if [ -d ".venv" ]; then
    cp .venv/pyvenv.cfg "$BACKUP_DIR/" 2>/dev/null || true
fi

# 6. 백업 검증
tar -czf "$BACKUP_DIR.tar.gz" "$BACKUP_DIR"
echo "✅ 백업 완료: $BACKUP_DIR.tar.gz"