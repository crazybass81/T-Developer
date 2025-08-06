#!/bin/bash

echo "🚀 Installing Agno Framework..."

# Python 가상환경 활성화 확인
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  Virtual environment not activated. Activating..."
    source venv/bin/activate
fi

# Agno 프레임워크 설치
echo "📦 Installing Agno core..."
pip install agno

echo "📦 Installing Agno with all extensions..."
pip install agno[all]

echo "📦 Installing Agno monitoring..."
pip install agno[monitoring]

echo "📦 Installing Agno tracing..."
pip install agno[tracing]

# 필수 의존성 설치
echo "📦 Installing required dependencies..."
pip install pydantic>=2.0
pip install httpx>=0.24
pip install rich>=13.0

# 추가 성능 최적화 패키지
echo "📦 Installing performance optimization packages..."
pip install numba>=0.58.0
pip install psutil>=5.9.0

echo "✅ Agno Framework installation completed!"

# 설치 확인
echo "🔍 Verifying installation..."
python -c "
try:
    import agno
    print('✅ Agno imported successfully')
    print(f'✅ Agno version: {agno.__version__}')
except ImportError as e:
    print(f'❌ Agno import failed: {e}')
    exit(1)

try:
    from agno.monitoring import MonitoringConfig
    from agno.tracing import TracingConfig
    print('✅ Agno monitoring and tracing modules available')
except ImportError as e:
    print(f'❌ Agno extensions import failed: {e}')
    exit(1)

try:
    import pydantic
    import httpx
    import rich
    print('✅ All dependencies available')
except ImportError as e:
    print(f'❌ Dependency import failed: {e}')
    exit(1)
"

if [ $? -eq 0 ]; then
    echo "🎉 Agno Framework ready for use!"
else
    echo "❌ Installation verification failed"
    exit 1
fi