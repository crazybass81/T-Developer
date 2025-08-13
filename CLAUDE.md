# T-Developer Evolution System

## 📚 Key Documents
1. [Master Plan](./AI-DRIVEN-EVOLUTION.md) - **Primary Reference**
2. [Today's Tasks](./docs/00_planning/daily_todos/week03/day15.md)
3. [Evolution Engine](./docs/01_architecture/components/evolution_engine.md)
4. [Agent Registry](./docs/01_architecture/components/agent_registry.md)
5. [Workflow Engine](./docs/01_architecture/components/workflow_engine.md)

## 🔧 Active Development
- Branch: feature/T-Orchestrator
- Working Dir: /home/ec2-user/T-DeveloperMVP
- Language: Python 3.11+ **ONLY**
- Package Manager: UV (not pip)
- Related Issues: Evolution Engine MVP

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

## 📊 Current Status

| Component | Status | Progress | Next Action |
|-----------|--------|----------|-------------|
| Evolution Engine | 🔧 Working | 40% | Core logic implementation |
| Agent Registry | 🔧 Working | 30% | Schema definition |
| Workflow Engine | ⏸ Planned | 0% | Start after Registry |
| AgentCore Integration | ⏸ Planned | 0% | Waiting for agents |
| Agent Squad Setup | ⏸ Planned | 0% | Architecture review |

## 🔐 Environment Setup

### Required Environment Variables
```bash
# Evolution System
export EVOLUTION_MODE=enabled
export AI_AUTONOMY_LEVEL=0.85  
export MEMORY_CONSTRAINT_KB=6.5
export INSTANTIATION_TARGET_US=3

# AWS Configuration (필요시 요구)
export AWS_REGION=us-east-1
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret

# API Keys (필요시 요구)
export OPENAI_API_KEY=sk-...
export ANTHROPIC_API_KEY=sk-ant-...
```

### Development Setup Checklist
- [ ] Python 3.11+ installed
- [ ] UV package manager installed
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] Environment variables set
- [ ] AWS credentials configured
- [ ] Git repository cloned

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