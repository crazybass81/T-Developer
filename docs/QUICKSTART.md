# 🚀 T-Developer AI Evolution System - Quick Start

## 📋 시작하기 전에 (Prerequisites)

### 필수 요구사항
- **Python 3.11+** (TypeScript 제거됨)
- **UV Package Manager** (pip 대체)
- **AWS CLI v2** 
- **Docker** (선택사항)
- **16GB+ RAM**
- **50GB+ 저장공간**

## ⚡ 5분 안에 시작하기

### 1️⃣ 환경 설정 (30초)
```bash
# UV 설치 (필수!)
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc

# 프로젝트 클론
git clone https://github.com/your-org/T-DeveloperMVP.git
cd T-DeveloperMVP
```

### 2️⃣ 의존성 설치 (1분)
```bash
# Python 환경 생성
uv venv evolution-env
source evolution-env/bin/activate

# 의존성 설치 (UV 사용!)
uv pip install -r requirements.txt
```

### 3️⃣ 환경변수 설정 (1분)
```bash
# .env 파일 생성
cat > .env << EOF
# Evolution Settings
EVOLUTION_MODE=autonomous
AI_AUTONOMY_LEVEL=85
AGENT_MEMORY_LIMIT=6656  # 6.5KB
INSTANTIATION_TARGET_US=3

# AWS Settings
AWS_REGION=us-east-1
AWS_BEDROCK_ENDPOINT=https://bedrock-runtime.us-east-1.amazonaws.com

# Safety Settings
EVOLUTION_SAFETY_ENABLED=true
MAX_GENERATIONS=50
EOF
```

### 4️⃣ 시스템 시작 (30초)
```bash
# Evolution System 시작
python -m src.evolution.start --autonomy=0.85

# 별도 터미널에서 모니터링
python -m src.evolution.monitor --dashboard
```

### 5️⃣ 첫 에이전트 생성 (2분)
```bash
# Agno Framework로 에이전트 생성
python -m agno.create_agent \
  --name=my_first_agent \
  --memory-limit=6.5kb \
  --instantiation-target=3us

# 에이전트 테스트
python -m tests.validate_agent my_first_agent
```

## 🧬 Evolution 시작하기

### 자동 진화 활성화
```python
from src.evolution import EvolutionEngine

# Evolution Engine 초기화
engine = EvolutionEngine(
    autonomy_level=0.85,       # 85% AI 자율성
    memory_constraint_kb=6.5,   # 6.5KB 메모리 제한
    instantiation_target_us=3.0, # 3μs 속도 목표
    safety_mode="strict"        # 안전 모드
)

# 진화 시작
engine.start_evolution(
    target_fitness=0.95,        # 목표 적합도
    max_generations=1000,       # 최대 세대
    improvement_target=0.05     # 세대당 5% 개선
)
```

### 진화 모니터링
```python
from src.monitoring import EvolutionMonitor

monitor = EvolutionMonitor()
monitor.track_metrics([
    "fitness_score",
    "memory_usage",
    "instantiation_speed",
    "autonomy_level"
])

# 실시간 대시보드
monitor.show_dashboard()
```

## 🎯 주요 명령어

### Evolution 관리
```bash
# 진화 시작
python -m src.evolution.start

# 진화 중지
python -m src.evolution.stop

# 상태 확인
python -m src.evolution.status

# 롤백
python -m src.evolution.rollback --generation=10
```

### 에이전트 관리
```bash
# 에이전트 목록
python -m src.agents.list

# 에이전트 상태
python -m src.agents.status --name=agent_name

# 제약 검증
python -m src.agents.validate --memory --speed
```

### 성능 모니터링
```bash
# 메모리 프로파일링
python -m memory_profiler src/agents/my_agent.py

# 속도 벤치마크
python -m performance.benchmark --target=3us

# 전체 시스템 체크
python -m src.health_check
```

## 📊 대시보드 접속

### Web Dashboard
```bash
# 대시보드 서버 시작
python -m src.dashboard.server --port=8080

# 브라우저에서 접속
# http://localhost:8080
```

### CLI Dashboard
```bash
# 터미널 대시보드
python -m src.dashboard.cli --refresh=1s
```

## 🔍 문제 해결

### 메모리 초과 (>6.5KB)
```bash
# 메모리 분석
python -m src.optimization.analyze_memory agent_name

# 자동 최적화
python -m src.optimization.optimize_memory agent_name
```

### 속도 미달 (>3μs)
```bash
# 속도 프로파일링
python -m src.optimization.profile_speed agent_name

# 속도 최적화
python -m src.optimization.optimize_speed agent_name
```

### Evolution 실패
```bash
# 안전 체크
python -m src.evolution.safety_check

# 로그 확인
tail -f logs/evolution.log

# 강제 롤백
python -m src.evolution.force_rollback
```

## 📚 다음 단계

1. **[전체 문서 읽기](INDEX.md)** - 시스템 이해하기
2. **[Architecture 학습](01_architecture/system/architecture.md)** - 구조 파악
3. **[Evolution Plan 확인](00_planning/AGENT_EVOLUTION_PLAN.md)** - 진화 계획
4. **[개발 가이드](02_implementation/phase1_foundation/development-guide.md)** - 개발 시작

## 💡 유용한 팁

### 🚀 Brave Mode 사용
```bash
# 자율 실행 모드 (Claude Code)
claude --brave "진화 시스템 최적화"
```

### 📈 Evolution 가속화
```python
# 병렬 진화 활성화
engine.enable_parallel_evolution(workers=10)

# 엘리트 선택 강화
engine.set_elite_ratio(0.2)  # 상위 20% 보존
```

### 🛡️ 안전 우선
```python
# 항상 안전 모드 활성화
engine.safety_mode = "strict"

# 체크포인트 자주 생성
engine.checkpoint_interval = 5  # 5세대마다
```

## 🆘 도움말

### 명령어 도움말
```bash
python -m src.evolution --help
python -m src.agents --help
python -m src.monitoring --help
```

### 문서
- [FAQ](faq.md)
- [Troubleshooting](05_operations/troubleshooting.md)
- [API Reference](03_api/rest/api-reference.md)

### 지원
- GitHub Issues: [Report Bug](https://github.com/your-org/T-DeveloperMVP/issues)
- Email: evolution@t-developer.ai

---

**🎉 축하합니다!**  
이제 AI가 스스로 진화하는 시스템을 시작했습니다.  
85% AI 자율성으로 시스템이 스스로 개선됩니다.

> "Evolution begins now - let AI lead the way"
