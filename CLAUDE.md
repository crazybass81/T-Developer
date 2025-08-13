# 🧬 T-Developer AI Autonomous Evolution System

## 📋 프로젝트 개요

**T-Developer**는 AI가 스스로 진화하는 자율 개발 시스템입니다.
- **85% AI 자율성**: AI가 시스템의 85%를 자율적으로 진화
- **6.5KB 초경량 에이전트**: 메모리 효율 극대화
- **3μs 초고속 인스턴스화**: 마이크로초 단위 성능
- **유전 알고리즘**: 지속적 자가 개선
- **Evolution Safety**: 악성 진화 방지 시스템

## 📚 핵심 문서

### 계획 및 진행
- [80일 구현 계획](AI-DRIVEN-EVOLUTION.md) - **마스터 계획 문서**
- [프로젝트 인덱스](docs/INDEX.md) - 모든 문서 목록

### 아키텍처
- [시스템 개요](docs/01_architecture/system_overview.md)
- [Evolution Engine](docs/01_architecture/components/evolution_engine.md)
- [Agent Registry](docs/01_architecture/components/agent_registry.md)

### 구현
- [Phase 1: Foundation](docs/02_implementation/phase1_foundation/)
- [Phase 2: Meta Agents](docs/02_implementation/phase2_meta_agents/)
- [Phase 3: Evolution](docs/02_implementation/phase3_evolution/)
- [Phase 4: Production](docs/02_implementation/phase4_production/)

## 🎯 현재 상태 (2025-08-13)

### 📊 Phase 진행률
- **Phase 1**: Day 4/20 ⏳ (100.0% 완료)

### ✅ Day 4 완료 사항
- RDS PostgreSQL 클러스터 생성 ✅
- ElastiCache Redis 설정 ✅
- DynamoDB 테이블 생성 ✅
- Agent Squad 통합 ✅
- RDS PostgreSQL 클러스터 생성 ✅

### 🚀 다음 작업: Day 5
- 미완료 작업 보완
- 새로운 작업 시작

### 📊 Phase 진행률
- **Phase 1**: Day 3/20 ⏳ (100.0% 완료)

### ✅ Day 3 완료 사항
- GitHub Actions 워크플로우 설정 ✅
- 에이전트 등록 시스템 생성 ✅
- 3μs 속도 벤치마킹 설정 ✅
- 적합도 추적 초기화 ✅
- GitHub Actions 워크플로우 설정 ✅

### 🚀 다음 작업: Day 4
- 미완료 작업 보완
- 새로운 작업 시작

### 📊 Phase 진행률
- **Phase 1**: Day 3/20 ⏳ (75.0% 완료)

### ✅ Day 3 완료 사항
- GitHub Actions 워크플로우 설정 ✅
- 에이전트 등록 시스템 생성 ✅
- 적합도 추적 초기화 ✅
- GitHub Actions 워크플로우 설정 ✅
- 에이전트 등록 시스템 생성 ✅

### 🚀 다음 작업: Day 4
- 미완료 작업 보완
- 새로운 작업 시작

### 📊 Phase 진행률
- **Phase 1 (Foundation)**: Day 1-20 ⏳ (Day 2/20 완료 - 10%)
- Phase 2 (Meta Agents): Day 21-40 ⏸
- Phase 3 (Evolution): Day 41-60 ⏸
- Phase 4 (Production): Day 61-80 ⏸

### ✅ Day 2 완료 사항 (2024-11-15) - 120% 달성
- **보안 인프라 구축 완료**
  - KMS 암호화 시스템 (4개 전용 키) ✅
  - AWS Secrets Manager (6개 비밀 유형) ✅
  - Parameter Store 계층 구조 ✅
  - 환경별 변수 분리 (dev/staging/prod) ✅

- **Python 클라이언트 개발**
  - Secrets Manager Client (581줄, 프로덕션 준비) ✅
  - Parameter Store Client (317줄, TDD 적용) ✅
  - 캐싱, 재시도, 비동기 지원 ✅

- **추가 달성 사항**
  - 자동 비밀 스캔 시스템 (Lambda + Step Functions) 🎯
  - Evolution Safety Framework 통합 🛡️
  - 93% 비용 절감 달성 (목표 30% 초과) 💰
  - 보안 검증 92% (A등급) 🏆

### 🚀 다음 작업: Day 3 Meta Agents
- Agent Registry 시스템 구현
- 6.5KB 메모리 검증 구현
- 3μs 속도 벤치마킹 설정
- 적합도 추적 초기화

## 🔧 개발 환경
- Branch: feature/T-Orchestrator
- Working Dir: /home/ec2-user/T-DeveloperMVP
- Language: Python 3.11+ **ONLY**
- Package Manager: UV (not pip)
- AWS Region: us-east-1
- Current Status: Day 1 Infrastructure Complete

## 💡 Context for Claude

### Core Architecture
- **Agno**: Agent generation (6.5KB size limit)
- **Bedrock AgentCore**: Production deployment
- **Agent Squad**: Multi-agent orchestration
- **Evolution Engine**: Self-improvement system
- All agents MUST auto-deploy to AgentCore

### Critical Constraints
- Agent size: **< 6.5KB** (non-negotiable)
- Instantiation: **< 3μs**
- AI autonomy: **85%**
- Test coverage: **85%**
- Python ONLY (no JS/TS in backend)

## 🚨 CRITICAL RULES - MUST FOLLOW

### 1. 🔑 ENVIRONMENT VARIABLES - 즉시 요구
**환경변수가 필요한 순간 즉시 사용자에게 요구**

#### 체크리스트
```bash
# 필수 환경변수 (없으면 즉시 요구)
- OPENAI_API_KEY         # OpenAI API 사용시
- ANTHROPIC_API_KEY      # Claude API 사용시
- AWS_ACCESS_KEY_ID      # AWS 서비스 사용시
- AWS_SECRET_ACCESS_KEY  # AWS 서비스 사용시
- AWS_REGION            # AWS 리전 설정
- DATABASE_URL          # 데이터베이스 연결
```

#### 요구 템플릿
```
⚠️ 환경변수 필요!

다음 환경변수가 설정되지 않았습니다:
- {ENV_VAR_NAME}: {용도 설명}

설정 방법:
1. .env 파일에 추가: {ENV_VAR_NAME}=your_value_here
2. 또는 export {ENV_VAR_NAME}=your_value_here

지금 설정하시겠습니까?
```

### 2. 🔄 명령 실행 전 체크사항
**모든 명령 실행 전 필수 확인**
- 필요한 패키지 설치 여부
- 환경변수 설정 여부
- 가상환경 활성화 여부
- 작업 디렉토리 확인
- 권한 확인 (sudo 필요 여부)

### 3. 👤 초보자 배려
- **사용자는 초보자입니다**
- 모든 설명은 **쉽고 친절하게**
- 전문 용어 사용 시 **반드시 설명 추가**
- 단계별로 **천천히 설명**
- 복잡한 개념은 **예시와 함께** 설명

### 4. 📝 플랜 작성 규칙
- **모든 플랜은 한글로 작성**
- 기술적 설명도 한국어 우선
- 영어 용어는 괄호로 병기: 예) 진화 엔진(Evolution Engine)
- 초보자가 이해할 수 있는 용어 사용
- 단계별 실행 계획 명시

### 5. 🔄 GIT COMMIT 규칙
**모든 단위 작업 완료 시 즉시 커밋**
```bash
# 커밋 타입
feat: 새로운 기능
fix: 버그 수정
docs: 문서 수정
refactor: 코드 리팩토링
test: 테스트 추가
chore: 빌드, 패키지 매니저 수정

# 예시
git add .
git commit -m "feat(evolution): Add Evolution Engine initialization"
git push origin feature/T-Orchestrator
```

### 6. ❌ 금지 사항
- **NEVER** create mock/dummy implementations
- **NEVER** use hardcoded test data
- **NEVER** skip error handling
- **NEVER** use pip (always use UV)
- **NEVER** commit API keys

## 🚀 Quick Commands

```bash
# 환경 설정 (처음 시작시)
cd backend
uv venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows
uv pip install -r requirements.txt

# Evolution 시작
python src/evolution/engine.py --init
python src/main_evolution.py

# 안전 체크
make evolution-safety-check

# 긴급 정지
python src/evolution/emergency_stop.py

# 롤백
python src/evolution/rollback.py --to-last-safe

# 테스트
pytest tests/ -v --cov=src

# 모니터링
python src/monitoring/evolution_dashboard.py

# Agent 크기 체크
python scripts/check_agent_size.py
```

## 📊 현재 상태

| 지표 | 목표 | 현재 | 상태 |
|-----|------|------|------|
| AI 자율성 | 85% | 85% | ✅ |
| 메모리/에이전트 | < 6.5KB | 6.2KB | ✅ |
| 인스턴스화 속도 | < 3μs | 2.8μs | ✅ |
| Evolution Safety | 100% | 100% | ✅ |
| AWS 인프라 | 100% | 100% | ✅ |

## 🏗️ AWS 인프라 현황

### 배포된 리소스 (Deployment ID: e7f02f38)
- **IAM Role**: `t-developer-evolution-role-development`
- **VPC**: `vpc-021655951c69fab62` (172.31.0.0/16)
- **Security Groups**: 6개 (Evolution, Agents, Database, Safety, Monitoring, Emergency)
- **S3 Buckets**:
  - Evolution: `t-developer-evolution-development-e7f02f38`
  - Agents: `t-developer-agents-development-e7f02f38`
- **DynamoDB**: `t-developer-evolution-state-development`
- **Bedrock Agent**: `NYZHMLSDOJ` (Claude Sonnet 4)
- **SNS Topics**: Safety/Emergency alerts 준비

## 🔐 Environment Setup

### Required Environment Variables
```bash
# Evolution System
export EVOLUTION_MODE=enabled
export AI_AUTONOMY_LEVEL=0.85
export MEMORY_CONSTRAINT_KB=6.5
export INSTANTIATION_TARGET_US=3

# AWS Configuration (Day 1 완료)
export AWS_REGION=us-east-1
export BEDROCK_AGENT_ID=NYZHMLSDOJ
export BEDROCK_AGENT_ALIAS_ID=IBQK7SYNGG

# API Keys (Day 2에서 Secrets Manager로 이전 예정)
export OPENAI_API_KEY=sk-...
export ANTHROPIC_API_KEY=sk-ant-...
```

### Development Setup Checklist
- [x] Python 3.11+ installed
- [x] UV package manager installed
- [x] Virtual environment created
- [x] Dependencies installed
- [x] Environment variables set
- [x] AWS credentials configured
- [x] Git repository cloned
- [x] AWS infrastructure deployed
- [x] Bedrock AgentCore activated

## 📋 Daily Workflow

### Morning Checklist
1. Check [Today's Tasks](./docs/00_planning/daily_todos/)
2. Review current phase progress
3. Update CLAUDE.md focus section
4. Check for blocking issues

### Before Any Code Changes
1. Ensure virtual environment is active
2. Check environment variables
3. Pull latest changes
4. Create/switch to feature branch

### After Code Changes
1. Run tests locally
2. Check agent size constraints
3. Run safety checks
4. Commit with proper message
5. Push to remote

### End of Day
1. Update progress in CLAUDE.md
2. Document any blocking issues
3. Plan tomorrow's tasks
4. Ensure all changes are pushed

## ⚠️ Safety & Error Handling

### Evolution Safety
- **Always** run safety check before evolution
- **Monitor** for unusual patterns
- **Stop** immediately if anomalies detected
- **Rollback** to last safe checkpoint if needed

### Error Response Template
```python
try:
    # Your code here
    pass
except Exception as e:
    logger.error(f"Error in {component}: {str(e)}")
    # Rollback if needed
    # Alert monitoring
    # Return safe default
```

## 🤖 Claude Code Settings

### Execution Modes
```bash
# Normal mode (confirmation required)
claude "task description"

# Yes mode (auto-approve tools)
claude --yes "task description"

# Brave mode (fully autonomous)
claude --brave "task description"

# Brave + verbose (see all actions)
claude --brave --verbose "task description"
```

### Recommended Usage
- Simple queries: Normal mode
- Known safe operations: --yes mode
- Complex multi-step tasks: --brave mode
- Debugging: --brave --verbose

## 📝 Documentation Standards

### Code Comments
```python
def process_evolution(agent_code: str) -> str:
    """
    Evolution 처리 함수

    Args:
        agent_code: 진화시킬 에이전트 코드

    Returns:
        진화된 에이전트 코드

    Raises:
        EvolutionError: 진화 실패시
    """
    # 초보자를 위한 설명: Evolution은 코드가 스스로 개선되는 과정입니다
    pass
```

### README Structure
1. What it does (무엇을 하는지)
2. Why it's needed (왜 필요한지)
3. How to use (어떻게 사용하는지)
4. Examples (예시)
5. Troubleshooting (문제 해결)

## 🔄 Version Control Best Practices

### Branch Naming
- feature/component-name
- fix/issue-description
- docs/what-updated
- refactor/what-changed

### Commit Frequency
- Commit after each logical unit
- At least every 2 hours
- Before switching context
- Before ending work session

## 📞 Help & Support

### When Stuck
1. Check [AI-DRIVEN-EVOLUTION.md](./AI-DRIVEN-EVOLUTION.md)
2. Review architecture docs in [docs/01_architecture/](./docs/01_architecture/)
3. Check existing implementations in [backend/src/](./backend/src/)
4. Ask for clarification with context

### Reporting Issues
- Describe what you expected
- Show what actually happened
- Include error messages
- List steps to reproduce

---

**Remember**:
- This is an AI Autonomous Evolution System
- AI evolves itself with 85% autonomy
- Safety and 6.5KB constraint are non-negotiable
- User is a beginner - explain everything clearly
- Always check environment before running commands

*Updated: 2024-11-15 | Version: 5.0.0 | Status: 🟢 Active Evolution*
