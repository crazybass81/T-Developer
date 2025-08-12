# T-Developer Project Guidelines

## 👤 USER CONTEXT
- **사용자는 초보자입니다**
- 모든 설명은 **쉽고 친절하게**
- 전문 용어 사용 시 **반드시 설명 추가**
- 단계별로 **천천히 설명**
- 복잡한 개념은 **예시와 함께** 설명

## 🏛️ ARCHITECTURE ADHERENCE
- **PRIMARY SOURCE**: `.amazonq/rules/` 폴더가 최우선 설계 문서
- **MUST READ**: `/ARCHITECTURE.md` 및 `.amazonq/rules/` 필독
- **3 CORE FRAMEWORKS**: 
  - AWS Agent Squad (오케스트레이션)
  - Agno Framework (에이전트 생성)
  - AWS Bedrock AgentCore (런타임)
- **NEVER DEVIATE**: 정의된 아키텍처 절대 준수
- **9-Agent Pipeline**: 순서와 역할 엄격히 유지
- **NOT WEB-ONLY**: 모든 종류의 소프트웨어 프로젝트 지원
- **Python First**: MetaRules.md에 따라 Python 우선
- 변경 필요시 반드시 .amazonq/rules/ 문서 참조

## 💻 LANGUAGE RULES - Framework/Tool별 언어 규칙

### Framework별 필수 언어
```
AWS Agent Squad      → Python (필수), TypeScript (선택)
Agno Framework      → Python (필수)
AWS Bedrock AgentCore → Python (필수)
Agent Implementations → Python (목표), TypeScript (현재)
Frontend (React)     → TypeScript (필수)
Backend API         → Python/FastAPI (목표), TypeScript/Express (현재)
AWS Infrastructure  → Python (CDK), YAML (CloudFormation)
Testing            → Python (pytest), TypeScript (Jest/Playwright)
```

### 언어 선택 우선순위
1. **Python** - Agent, AWS 통합, AI/ML, 데이터 처리
2. **TypeScript** - Frontend, 타입 안전성 필요 부분
3. **Bash** - 스크립트, 자동화
4. **YAML/JSON** - 설정, CI/CD

### 절대 규칙
- pip 명령어 → uv로 변경
- Python이 주 언어 (MetaRules.md)
- Agent는 반드시 Python으로 마이그레이션

## 🚨 CRITICAL RULES - MUST FOLLOW

### 1. 🔄 GIT COMMIT & PUSH RULES - 필수 준수
**모든 단위 작업 완료 시 즉시 커밋 & 푸시**
- **단위 작업 정의**: 
  - 하나의 기능 구현 완료
  - 하나의 버그 수정 완료
  - 하나의 파일/모듈 리팩토링 완료
  - 하나의 테스트 작성 완료
  - 문서 업데이트 완료
- **커밋 규칙**:
  - 작업 완료 즉시 커밋 (최대 2시간 이내)
  - Conventional Commits 형식 사용
  - 의미 있는 단위로 분리
  - 커밋 메시지에 작업 내용 명확히 기술
- **푸시 규칙**:
  - 커밋 후 즉시 푸시 (리뷰 용이성)
  - feature 브랜치 사용 권장
  - main 브랜치는 안정된 코드만
- **목적**:
  - 다른 개발자/AI 서비스의 즉각적인 리뷰 가능
  - 작업 히스토리 명확한 추적
  - 충돌 최소화 및 빠른 통합
  - 백업 및 협업 효율성 증대

### 커밋 메시지 템플릿
```bash
<type>(<scope>): <subject>

<body>

<footer>
```

### 타입 종류
- **feat**: 새로운 기능 추가
- **fix**: 버그 수정
- **docs**: 문서 수정
- **style**: 코드 포맷팅, 세미콜론 누락 등
- **refactor**: 코드 리팩토링
- **test**: 테스트 추가
- **chore**: 빌드 업무, 패키지 매니저 수정 등

### 예시
```bash
# 단위 작업 완료 후 즉시 실행
git add .
git commit -m "feat(agent): Implement NL Input Agent with production logic"
git push origin feature/nl-input-agent

# 또는 main 브랜치 직접 푸시 (소규모 수정)
git add .
git commit -m "fix(api): Resolve download path issue in simple_api.py"
git push origin main
```

### 2. 🔧 ERROR HANDLING RULES - 오류 처리 규칙
- **NEVER** simplify or skip implementations when errors repeat
- **NEVER** create workarounds without user permission
- **ALWAYS** ask for user approval before simplifying complex solutions
- **ALWAYS** fix the root cause, not symptoms
- **MUST** report all errors transparently to the user
- When stuck on repeated errors:
  - Stop and explain the issue clearly
  - Provide multiple solution options
  - Wait for user decision
  - Do NOT proceed with shortcuts

### 3. ❌ NO MOCK IMPLEMENTATIONS
- **NEVER** create mock, dummy, or placeholder implementations
- **NEVER** use hardcoded responses or fake data
- **NEVER** implement "temporary" solutions
- All code must be **production-ready** from the start

### 4. ✅ PRODUCTION-READY REQUIREMENTS
Every implementation MUST include:
- **Error Handling**: Comprehensive try-catch blocks, proper error messages
- **Validation**: Input validation, type checking, boundary conditions
- **Logging**: Detailed logging for debugging and monitoring
- **Performance**: Optimized algorithms, caching where appropriate
- **Scalability**: Code that can handle growth in data/users
- **Security**: Input sanitization, SQL injection prevention, XSS protection
- **Testing**: Unit tests, integration tests where applicable
- **Documentation**: Clear comments and docstrings

### 5. 🎯 AGENT IMPLEMENTATION STANDARDS
For the 9-agent pipeline, each agent MUST:
- Implement **real logic**, not placeholder returns
- Include **data processing algorithms**
- Have **configurable parameters**
- Support **edge cases**
- Provide **meaningful outputs** based on actual analysis
- Include **performance metrics**
- Support **async operations** where needed

### 6. 🔧 TECHNICAL REQUIREMENTS
- Use the **Python implementations** in `/backend/src/agents/implementations/` as reference
- These are production-ready with advanced features
- TypeScript implementations should match Python quality level
- Include all supporting modules (validators, optimizers, cache, etc.)

### 7. 📊 QUALITY METRICS
Each component must achieve:
- Code coverage: > 80%
- Cyclomatic complexity: < 10
- Response time: < 1s for most operations
- Error rate: < 0.1%
- Memory efficiency: No memory leaks

### 8. 🚫 FORBIDDEN PRACTICES
- `return mockData` ❌
- `// TODO: implement later` ❌
- `console.log("Not implemented")` ❌
- Hardcoded test data in production code ❌
- Empty catch blocks ❌
- Ignoring error states ❌

### 9. 📝 CHECKLIST FOR NEW FEATURES
Before marking any feature as complete:
- [ ] Real implementation with actual logic
- [ ] Error handling for all edge cases
- [ ] Input validation
- [ ] Performance optimization
- [ ] Security considerations
- [ ] Logging and monitoring
- [ ] Tests written and passing
- [ ] Documentation updated

## PROJECT SPECIFIC NOTES

### Current Issues to Fix:
1. **TypeScript agents are mock-level** - Need complete rewrite to production level
2. **Download endpoint issue** - Express static middleware interfering with API routes
3. **Duplicate implementations** - Python (good) vs TypeScript (mock) - need to integrate Python or upgrade TypeScript

### Architecture:
- 9 Agent Pipeline: NL Input → UI Selection → Parser → Component Decision → Match Rate → Search → Generation → Assembly → Download
- Each agent must perform real processing, not just pass data through

### Testing Commands:
```bash
# Test the API
curl -X POST http://localhost:8000/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{"query": "Create a todo app"}'

# Check download
curl -O http://localhost:8000/api/v1/download/[filename].zip
```

### Key Paths:
- Backend: `/home/ec2-user/T-DeveloperMVP/backend/`
- Python Agents: `/home/ec2-user/T-DeveloperMVP/backend/src/agents/implementations/`
- TypeScript Agents: `/home/ec2-user/T-DeveloperMVP/backend/src/agents/*.ts`
- Frontend: `/home/ec2-user/T-DeveloperMVP/frontend/`

## 📚 EXPLANATION GUIDELINES
When explaining to the user:
1. **Use simple Korean** - 쉬운 한국어로 설명
2. **Avoid jargon** - 전문용어 최소화
3. **Provide examples** - 구체적인 예시 제공
4. **Step-by-step** - 단계별 설명
5. **Visual aids** - 이모지, 도표 활용
6. **Check understanding** - 이해 확인 질문

### Example of Good Explanation:
```
❌ Bad: "The API endpoint uses REST architecture with JWT authentication"
✅ Good: "API는 웹 주소같은 거예요. 마치 식당 주문 창구처럼 요청을 받아서 처리해줍니다. 
         보안을 위해 비밀번호 같은 열쇠(JWT)를 사용합니다."
```

## 🔐 SECURITY & CREDENTIALS

### AWS 환경변수 관리 (2개 서비스 사용)
1. **AWS Systems Manager Parameter Store** 
   - 일반 설정값 (Framework 설정, URL, 타임아웃 등)
   - 경로: `/t-developer/{environment}/`
   - 예: `/t-developer/production/api_url`

2. **AWS Secrets Manager**
   - 민감한 정보 (API 키, 비밀번호, 토큰 등)
   - 네이밍: `t-developer/{environment}/{service}`
   - 예: `t-developer/production/openai-api-key`

### 환경변수 규칙
- **NEVER** commit API keys or credentials
- Local development: `.env` 파일 사용 (git ignore 필수)
- Staging/Production: AWS 서비스만 사용
- 모든 secrets는 암호화 저장
- IAM 역할 기반 접근 제어

## 📊 PERFORMANCE REQUIREMENTS
- Each Agent execution: < 3 seconds
- Total pipeline: < 30 seconds  
- Memory per agent: < 6.5KB (Agno target)
- API response time: < 1 second
- CloudWatch metrics for all operations

## 🧪 TESTING STANDARDS
- Python code coverage: ≥ 80% (pytest)
- TypeScript coverage: ≥ 70% (Jest)
- Each Agent must have unit tests
- Integration tests for pipeline
- E2E test scenarios: minimum 5

## 📝 DOCUMENTATION REQUIREMENTS
- Each Agent needs README.md
- API documentation: OpenAPI/Swagger
- Complex logic: Korean comments for clarity
- CHANGELOG.md for all updates
- Architecture decisions in ADR format

## 🔄 VERSION CONTROL
- Semantic Versioning (MAJOR.MINOR.PATCH)
- Git commit format: type(scope): message
  - Types: feat, fix, docs, refactor, test, chore
- Each Agent has independent versioning
- Tag releases with v prefix (v1.0.0)

## 💾 DATA MANAGEMENT
- Auto-delete generated projects after 24 hours
- Encrypt all user data
- No PII in logs
- S3 versioning enabled
- Database backups daily

## 🚦 ERROR HANDLING
```python
# Standard error format
{
    "error": {
        "code": "AGENT_TIMEOUT",
        "message": "작업 시간이 초과되었습니다",  # User-friendly Korean
        "details": {...},  # Technical details for debugging
        "timestamp": "2024-01-01T00:00:00Z"
    }
}
```
- Retry logic: 3 attempts with exponential backoff
- Circuit breaker for external services
- Graceful degradation

## 🎨 CODE STYLE
### Python
- Formatter: Black (line length 88)
- Import sorter: isort
- Linter: flake8 + pylint
- Type hints required
- Docstrings: Google style

### TypeScript
- Formatter: Prettier
- Linter: ESLint
- Strict mode enabled
- No any types
- JSDoc for public APIs

## 🔌 INTEGRATION RULES
- External API timeout: 5 seconds
- Health check endpoint required
- Circuit breaker after 5 failures
- Rate limiting per client
- Request/Response validation

## 🖥️ COMPUTE ENVIRONMENT RULES

### ECS Fargate 통합 아키텍처 (프로덕션 표준)
**완벽한 기능 구현을 위한 ECS 통합 전략**

```yaml
ECS Fargate 클러스터:
  이름: t-developer-cluster
  
  서비스 구성:
    분석 그룹 (Service 1):
      - Agents: NL Input, UI Selection, Parser
      - CPU: 1 vCPU
      - Memory: 2GB
      - Auto-scaling: 2-10 tasks
      - 특징: 빠른 텍스트 처리, 경량 작업
    
    결정 그룹 (Service 2):
      - Agents: Component Decision, Match Rate, Search
      - CPU: 2 vCPU
      - Memory: 4GB
      - Auto-scaling: 2-8 tasks
      - 특징: 중간 복잡도, 계산 집약적
    
    생성 그룹 (Service 3):
      - Agents: Generation, Assembly, Download
      - CPU: 4 vCPU
      - Memory: 8GB
      - Auto-scaling: 1-5 tasks
      - 특징: 무거운 작업, 파일 I/O 집약적

통합 장점:
  - ✅ 무제한 실행 시간 (Generation 30분+ 가능)
  - ✅ 에이전트 간 직접 메모리 공유
  - ✅ 일관된 성능 (콜드 스타트 없음)
  - ✅ 완벽한 기능 구현
  - ✅ 통합 모니터링 및 로깅
  - ✅ 롤백 및 배포 단순화
```

### Lambda Functions (보조 유틸리티만)
**용도**: ECS를 지원하는 경량 유틸리티
```yaml
Lambda 사용 케이스:
  - 헬스체크 엔드포인트
  - S3 이벤트 트리거
  - CloudWatch 알람 핸들러
  - 정기 정리 작업 (Cron)
  
주의: 메인 에이전트는 모두 ECS에서 실행
```

### 아키텍처 선택 기준
```python
def choose_compute(component):
    """모든 핵심 에이전트는 ECS에서 실행"""
    if component.type == "agent":
        return "ECS_FARGATE"  # 9개 에이전트 모두
    elif component.type == "utility":
        return "Lambda"  # 보조 기능만
    elif component.type == "database":
        return "RDS/DynamoDB"
    else:
        return "ECS_FARGATE"  # 기본값
```

### 비용 최적화 전략
```yaml
ECS Fargate Spot:
  - 70% 비용 절감
  - 개발/테스트 환경 적합
  - 중단 허용 작업

ECS Fargate (On-Demand):
  - 프로덕션 환경
  - 예측 가능한 성능
  - Auto-scaling으로 효율화

Savings Plans:
  - 1년/3년 약정
  - 최대 50% 절감
  - 안정적인 워크로드
```

### 배포 파이프라인
```yaml
CI/CD with ECS:
  1. GitHub Push
  2. CodeBuild: Docker 이미지 빌드
  3. ECR: 이미지 저장
  4. CodeDeploy: Blue/Green 배포
  5. ECS Service 업데이트
  6. Health Check & Rollback
```

## 📦 DEPLOYMENT CHECKLIST
- [ ] All tests passing
- [ ] Security scan completed
- [ ] Performance benchmarks met
- [ ] Documentation updated
- [ ] Rollback plan ready
- [ ] Staging environment tested
- [ ] Monitoring alerts configured

## 🤖 CLAUDE CODE SETTINGS

### 설정 파일 구조 (3단계 우선순위)
```
1. Global 설정 (~/.claude/settings.json) - 모든 프로젝트
2. Project 설정 (.claude/settings.json) - 팀과 공유, Git 커밋
3. Local 설정 (.claude/settings.local.json) - 개인용, Git 제외
```

### 우선순위
Local > Project > Global (Local이 최우선)

### 실행 모드
```bash
# 일반 모드 (확인 필요)
claude "작업 내용"

# Yes Mode (도구 사용 자동 승인)
claude --yes "작업 내용"

# Brave Mode (모든 작업 자동 승인, 적극적 실행)
claude --brave "작업 내용"

# Brave Mode + 상세 로그
claude --brave --verbose "작업 내용"

# Brave Mode + 비용 제한
claude --brave --max-cost 5 "작업 내용"
```

### Brave Mode 특징
- ✅ 모든 도구 자동 승인
- ✅ 더 큰 범위의 변경 허용
- ✅ 복잡한 다단계 작업 연속 실행
- ✅ 더 적극적인 문제 해결
- ✅ 긴 작업도 중단 없이 진행

### 현재 프로젝트 설정 (.claude/settings.json)
```json
{
  "brave": true,              // Brave Mode 기본 활성화 설정
  "auto_approval": {
    "enabled": true,
    "patterns": ["*"]         // 모든 도구 허용
  },
  "permissions": {
    "allow": ["*"],           // 모든 명령 허용
    "deny": []
  }
}
```

**주의**: 설정 파일의 `"brave": true`는 기본값일 뿐, 실제 Brave Mode 실행은 `--brave` 플래그 필요

### 권장 사용법
- 일반 작업: `claude "작업"`
- 간단한 자동화: `claude --yes "작업"`  
- 복잡한 작업: `claude --brave "작업"`
- 대규모 리팩토링: `claude --brave --verbose "작업"`

## REMEMBER:
**Every line of code should be production-ready. No exceptions.**
**Every explanation should be beginner-friendly. No assumptions.**
**Follow .amazonq/rules/ as the source of truth.**
**Use --brave flag for autonomous execution mode.**