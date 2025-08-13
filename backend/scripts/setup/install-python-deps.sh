#!/bin/bash
# scripts/install-python-deps.sh

echo "🔧 Python 의존성 설치 중..."

# 가상 환경 생성
if [ ! -d "venv" ]; then
    echo "📦 Python 가상 환경 생성 중..."
    python3 -m venv venv
    echo "✅ 가상 환경 생성 완료"
else
    echo "✅ 가상 환경이 이미 존재합니다"
fi

# 가상 환경 활성화 및 의존성 설치
echo "📦 Python 패키지 설치 중..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Python 의존성 설치 완료!"
echo "📋 다음 단계:"
echo "   - source venv/bin/activate (가상 환경 활성화)"
echo "   - python scripts/setup-aws-profile.py (AWS 설정 확인)"
