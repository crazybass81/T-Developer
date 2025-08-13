# 🧬 T-Developer AI Autonomous Evolution System

## 📋 프로젝트 개요

**T-Developer**는 AI가 스스로 진화하는 자율 개발 시스템입니다.
- **85% AI 자율성**: AI가 시스템의 85%를 자율적으로 진화
- **6.5KB 초경량 에이전트**: 메모리 효율 극대화
- **3μs 초고속 인스턴스화**: 마이크로초 단위 성능
- **유전 알고리즘**: 지속적 자가 개선
- **Evolution Safety**: 악성 진화 방지 시스템

## 🚀 빠른 시작

```bash
# 1. 환경 설정
cd backend
uv venv && source .venv/bin/activate
uv pip install -r requirements.txt

# 2. Evolution 시작
python src/evolution/engine.py --init
python src/main_evolution.py

# 3. 모니터링
python src/monitoring/evolution_dashboard.py
```

자세한 내용: [docs/QUICKSTART.md](docs/QUICKSTART.md)

## 📚 핵심 문서

### 계획 및 진행
- [80일 구현 계획](AI-DRIVEN-EVOLUTION.md) - **마스터 계획 문서**
- [프로젝트 인덱스](docs/INDEX.md) - 모든 문서 목록
- [일일 체크리스트](docs/00_planning/daily_todos/) - 매일 수행할 작업

### 아키텍처
- [시스템 개요](docs/01_architecture/system_overview.md)
- [Evolution Engine](docs/01_architecture/components/evolution_engine.md)
- [Agent Registry](docs/01_architecture/components/agent_registry.md)

### 구현
- [Phase 1: Foundation](docs/02_implementation/phase1_foundation/)
- [Phase 2: Meta Agents](docs/02_implementation/phase2_meta_agents/)
- [Phase 3: Evolution](docs/02_implementation/phase3_evolution/)
- [Phase 4: Production](docs/02_implementation/phase4_production/)

## 🎯 현재 목표

### 이번 주 마일스톤
- [ ] Evolution Engine 초기화
- [ ] Agent Registry 구현
- [ ] Workflow Engine 설정
- [ ] AgentCore 통합

### 오늘 할 일
👉 [오늘의 체크리스트](docs/00_planning/daily_todos/week01/day01.md)

## 📊 현재 상태

| 지표 | 목표 | 현재 | 상태 |
|-----|------|------|------|
| AI 자율성 | 85% | 85% | ✅ |
| 메모리/에이전트 | < 6.5KB | 6.2KB | ✅ |
| 인스턴스화 속도 | < 3μs | 2.8μs | ✅ |
| Evolution Safety | 100% | 100% | ✅ |
| 비용 절감 | 30% | 32% | ✅ |

## 🛠️ 개발 환경

### 필수 요구사항
- Python 3.11+ (Python 전용)
- UV Package Manager
- Docker & Docker Compose
- AWS Account (Bedrock, ECS)
- 32GB RAM (Evolution 테스트용)

### 환경 변수
```bash
export EVOLUTION_MODE=enabled
export AI_AUTONOMY_LEVEL=0.85
export MEMORY_CONSTRAINT_KB=6.5
export INSTANTIATION_TARGET_US=3
```

## 🧬 Evolution 명령어

### 기본 명령어
```bash
# Evolution 시작
make evolution-start

# Evolution 중지
make evolution-stop

# 상태 확인
make evolution-status

# 안전 검사
make evolution-safety-check
```

### 긴급 명령어
```bash
# 즉시 중지
python src/evolution/emergency_stop.py

# 안전 체크포인트로 롤백
python src/evolution/rollback.py --to-last-safe
```

## 📈 진행 추적

### Phase 진행률
- Phase 1 (Foundation): Day 1-20 ⏳
- Phase 2 (Meta Agents): Day 21-40 ⏸
- Phase 3 (Evolution): Day 41-60 ⏸
- Phase 4 (Production): Day 61-80 ⏸

### 주간 리포트
매주 금요일 자동 생성: `docs/00_planning/weekly_reports/`

## 🔐 보안 및 안전

### Evolution Safety Framework
- 악성 진화 패턴 감지
- 자동 롤백 시스템
- 체크포인트 관리
- 실시간 안전 모니터링

### AI Security Framework
- Prompt Injection 방어
- Output Validation
- PII 자동 마스킹
- 위협 실시간 탐지

## 🤝 기여 가이드

1. [AI-DRIVEN-EVOLUTION.md](AI-DRIVEN-EVOLUTION.md) 숙지
2. Python 코딩 표준 준수
3. 85% 테스트 커버리지 유지
4. Evolution Safety 검증 통과
5. PR 제출 전 종합 테스트

## 📞 지원 및 문의

- 문서: [docs/](docs/)
- 이슈: [GitHub Issues](https://github.com/your-org/T-DeveloperMVP/issues)
- Evolution 계획: [AI-DRIVEN-EVOLUTION.md](AI-DRIVEN-EVOLUTION.md)

---

**시스템**: AI Autonomous Evolution Platform  
**버전**: 5.0.0  
**AI 자율성**: 85%  
**상태**: 🟢 Active Evolution

> "AI가 스스로 진화하는 미래의 개발 플랫폼"

## 🔄 최근 업데이트

- 2024-11-15: v5.0.0 - AI Autonomous Evolution System 출시
- 2024-11-15: 문서 구조 전면 재구성
- 2024-11-15: Python 전용 시스템으로 전환
- 2024-11-15: Evolution Safety Framework 구현

## ⚠️ 중요 참고사항

**이 문서는 프로젝트의 진입점입니다.**
- 모든 개발은 이 문서에서 시작하세요
- 매일 이 문서를 확인하여 진행 상황을 추적하세요
- Evolution 시스템 상태를 항상 모니터링하세요

---

*마지막 업데이트: 2024-11-15*