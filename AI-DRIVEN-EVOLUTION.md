# 🧬 T-Developer 자기진화 시스템 - 마스터 플랜

> **📅 Last Updated**: 2025-08-14  
> **🎯 Current Phase**: MVP 재설계 (Day 46)  
> **📍 Status**: 자기진화 아키텍처 구현중

## 🎯 프로젝트 비전

**T-Developer는 자기 자신을 진화시키는 AI 개발 시스템입니다.**

```
현재: Human + Claude Code → T-Developer MVP
미래: T-Developer v1 → T-Developer v2 → T-Developer v3 → ... (무한 진화)
```

## 🏗️ 핵심 아키텍처

### 4대 핵심 에이전트 시스템

```yaml
자기진화 루프:
  1. ResearchAgent: 정보 수집
     - GitHub 유사 프로젝트 분석
     - 최신 기술 트렌드 조사  
     - MCP 도구 탐색
     
  2. PlannerAgent: 계획 수립
     - 목표 설정
     - 계층적 분해 (4시간 단위)
     - 우선순위 결정
     
  3. RefactorAgent: 실행/개선
     - 코드 리팩터링
     - 새 기능 구현
     - 최적화
     
  4. EvaluatorAgent: 평가/검증
     - 품질 평가
     - 성능 측정
     - 피드백 생성
     
  ↻ 무한 반복 → 100% 목표 달성
```

### Agent Registry - 모든 기능은 최소 단위 에이전트

```python
# 계층 구조
MetaAgent (4대 핵심)
└── MinimalAgent (20+ 최소 단위)
    ├── GitHubSearchAgent
    ├── TrendAnalyzerAgent
    ├── MCPDiscoveryAgent
    ├── GoalSetterAgent
    ├── TaskDecomposerAgent
    ├── CodeAnalyzerAgent
    ├── OptimizerAgent
    ├── QualityCheckerAgent
    └── ... (재사용 가능 모듈)
```

## 📅 구현 로드맵 (재정의)

### Phase 1: MVP Core (Day 46-50) 🚧 현재
- [x] Day 46: 아키텍처 재설계
  - ✅ BaseEvolutionAgent 인터페이스
  - ✅ PlannerAgent (계층적 계획)
  - ✅ ResearchAgent (정보 수집)
  - ⏳ RefactorAgent
  - ⏳ EvaluatorAgent
  
- [ ] Day 47: Agent Registry 구현
  - [ ] 최소 단위 에이전트 등록
  - [ ] 에이전트 디스커버리
  - [ ] 버전 관리
  
- [ ] Day 48: 첫 자기개선 사이클
  - [ ] T-Developer 코드 분석
  - [ ] 문서화 개선 실행
  - [ ] 평가 및 검증
  
- [ ] Day 49: 통합 테스트
  - [ ] 4대 에이전트 연동
  - [ ] 자기진화 루프 검증
  - [ ] 성능 측정
  
- [ ] Day 50: MVP 완성
  - [ ] 자기진화 데모
  - [ ] 문서 정리
  - [ ] v2 계획 수립

### Phase 2: Self-Evolution (Day 51-60)
- **목표**: T-Developer가 스스로 v2 생성
- **방법**: MVP가 자신의 코드를 프로젝트로 인식
- **결과**: 개선된 T-Developer v2

### Phase 3: Advanced Evolution (Day 61-70)
- **목표**: 복잡한 진화 능력
- **내용**: 
  - 새 에이전트 자동 생성
  - 아키텍처 레벨 변경
  - 크로스 프로젝트 학습

### Phase 4: Production (Day 71-80)
- **목표**: 상용화 준비
- **내용**:
  - MCP 서버 구현
  - VSCode Extension
  - GitHub Actions 통합
  - 커뮤니티 배포

## 📊 성공 지표

| 지표 | MVP 목표 | 현재 | 상태 |
|-----|---------|------|------|
| 자기진화 실행 | 1회 이상 | 0 | ⏳ |
| 코드 개선율 | 10%+ | - | ⏳ |
| 계획 정확도 | 80%+ | - | ⏳ |
| 에이전트 수 | 20+ | 2 | 🚧 |
| 재사용성 | 100% | 100% | ✅ |

## 🛠️ 기술 스택

```yaml
Core:
  - Python 3.11+
  - FastAPI (API Server)
  - AsyncIO (비동기 처리)

AI:
  - Claude API (코드 생성)
  - OpenAI Embeddings (유사도)
  - Local LLM (평가)

Infrastructure:
  - Docker (컨테이너)
  - GitHub Actions (CI/CD)
  - AWS Bedrock (프로덕션)

Frontend:
  - Next.js 15 (대시보드)
  - TailwindCSS (스타일)
  - Real-time Updates
```

## 📝 핵심 문서

- **[CLAUDE.md](CLAUDE.md)** - 프로젝트 컨텍스트
- **[자기진화 아키텍처](docs/SELF_EVOLUTION_ARCHITECTURE.md)** - 상세 설계
- **[Agent Registry](docs/AGENT_REGISTRY.md)** - 에이전트 관리
- **진행 보고서**:
  - [Phase 1 완료](docs/00_planning/progress/phase1_complete.md)
  - [Phase 2 완료](docs/00_planning/progress/phase2_week3-4_summary.md)
  - [Phase 3 진행중](docs/00_planning/progress/phase3_week1_summary.md)

## 🚀 Quick Start

```bash
# 1. 환경 설정
cd backend
source .venv/bin/activate
export ENVIRONMENT=development

# 2. 백엔드 실행
python -m uvicorn src.main_api:app --reload

# 3. 프론트엔드 실행 (별도 터미널)
cd frontend
npm run dev

# 4. 자기진화 테스트
python -m src.agents.evolution.research_agent
python -m src.agents.evolution.planner_agent
```

## ⚠️ 중요 규칙

1. **자기진화 우선**: 모든 기능은 T-Developer 자신을 개선하는데 초점
2. **4시간 작업 단위**: 모든 계획은 4시간 이하로 분해
3. **최소 단위 에이전트**: 모든 기능은 재사용 가능한 에이전트로
4. **문서 동기화**: 코드 변경시 반드시 문서 업데이트

## 🎯 다음 단계

- [ ] RefactorAgent 구현 완료
- [ ] EvaluatorAgent 구현 완료
- [ ] Agent Registry 시스템 구축
- [ ] 첫 자기개선 사이클 실행
- [ ] MVP 데모 준비

---

*"T-Developer: Building itself, by itself, for itself"*
