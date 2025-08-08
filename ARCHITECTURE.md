# T-Developer System Architecture
> AWS Multi-Agent Architecture 기반 프로젝트 자동 생성 시스템

## 🎯 프로젝트 핵심 목표
**자연어 입력으로 모든 종류의 소프트웨어 프로젝트를 자동 생성하는 AI 시스템**
- 웹 애플리케이션
- 모바일 앱
- 백엔드 API
- 데스크톱 애플리케이션
- CLI 도구
- 기타 모든 소프트웨어 프로젝트

## 🏗️ 핵심 프레임워크 (3대 축)

### 1. **AWS Agent Squad** - 오케스트레이션 레이어
- Multi-Agent 조정 및 관리
- SupervisorAgent 패턴으로 작업 분배
- 병렬 워크플로우 코디네이션
- 10,000x 성능 최적화
- Python/TypeScript 지원
- 오픈소스 (API 키 불필요)

### 2. **Agno Framework** - 에이전트 생성 레이어
- 초고속 에이전트 인스턴스화 (~3μs)
- 메모리 사용량 최소화 (6.5KB per agent)
- 다중 모달 지원 (Text, Image, Audio, Video)
- 25+ LLM 모델 지원
- 템플릿 기반 동적 에이전트 생성
- Level 1-5 메모리 persistence

### 3. **AWS Bedrock AgentCore** - 엔터프라이즈 런타임
- 8시간 세션 지원
- 서버리스 실행 환경
- 세션 격리 및 보안
- 자동 스케일링
- 소비 기반 과금

## 🎨 전체 시스템 아키텍처 (ECS Integrated)

```
┌─────────────────────────────────────────────────────────────┐
│                  T-Developer Web Interface                    │
│         - Natural Language Project Description               │
│         - Real-time Agent Status Dashboard                   │
│         - Interactive Development Console                    │
│         - Live Code Preview & Testing                        │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│            AWS Agent Squad Orchestration Layer               │
│    - Master Supervisor Agent (Project Manager)               │
│    - Intelligent Task Routing & Delegation                   │
│    - Parallel Workflow Coordination                          │
│    - Real-time Progress Monitoring                           │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│              T-Developer Core Agent System                   │
├──────────────┬──────────────────┬───────────────────────────┤
│ Requirements │   Development    │    Quality & Delivery     │
│   Agents     │     Agents       │        Agents            │
├──────────────┼──────────────────┼───────────────────────────┤
│ 1. NL Input  │ 4. Component     │ 8. Service Assembly      │
│ 2. UI Select │    Decision      │ 9. Download/Package      │
│ 3. Parser    │ 5. Match Rate    │                          │
│              │ 6. Search/Call   │                          │
│              │ 7. Generation    │                          │
└──────────────┴──────────────────┴───────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                 Agent Generation Layer                       │
│         Agno Framework - Dynamic Agent Creation              │
│    - Template-based Agent Generation (~3μs)                  │
│    - Language-specific Agent Specialization                  │
│    - Tool Integration & Memory Management                    │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│          AWS Bedrock AgentCore Runtime Layer                │
│    - Enterprise Runtime Environment                          │
│    - Session Isolation & Security                            │
│    - Auto-scaling & Resource Management                      │
│    - 8-hour Session Support                                  │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│              AWS Infrastructure Services                     │
├─────────────┬─────────────┬─────────────┬──────────────────┤
│ ECS Fargate │   DynamoDB  │      S3     │   CloudWatch     │
│  (Primary   │  (Session   │  (Artifacts │   (Monitoring)   │
│   Compute)  │   Storage)  │   Storage)  │                  │
├─────────────┼─────────────┼─────────────┼──────────────────┤
│    Step     │   Bedrock   │  CloudFront │   EventBridge    │
│  Functions  │   Models    │    (CDN)    │   (Events)       │
│ (Workflows) │    (LLMs)   │             │                  │
├─────────────┼─────────────┼─────────────┼──────────────────┤
│   Lambda    │     ECR     │     ALB     │   Auto Scaling   │
│  (Utility   │   (Docker   │    (Load    │   (Dynamic       │
│   Only)     │   Images)   │  Balancer)  │    Scaling)      │
└─────────────┴─────────────┴─────────────────────────────────┘
```

## 🔄 9-Agent Pipeline 상세

### Phase 1: Requirements Analysis
1. **NL Input Agent** (자연어 입력 처리)
   - Agno Framework로 인스턴스화
   - GPT-4/Claude 활용한 의도 분석
   - 요구사항 구조화

2. **UI Selection Agent** (기술 스택 선택)
   - 프로젝트 타입별 최적 스택 결정
   - 프레임워크/라이브러리 선택

3. **Parser Agent** (프로젝트 구조 분석)
   - 파일/폴더 구조 설계
   - 아키텍처 패턴 적용

### Phase 2: Development
4. **Component Decision Agent** (컴포넌트 설계)
   - 상세 컴포넌트 명세
   - 인터페이스 정의

5. **Match Rate Agent** (매칭률 계산)
   - 기존 템플릿과 비교
   - 재사용 가능 코드 식별

6. **Search Agent** (코드 템플릿 검색)
   - S3/DynamoDB에서 템플릿 조회
   - 베스트 프랙티스 수집

7. **Generation Agent** (코드 생성)
   - Claude/GPT-4 활용 코드 생성
   - 의존성 관리

### Phase 3: Quality & Delivery
8. **Assembly Agent** (프로젝트 조립/검증)
   - 코드 통합
   - 품질 검증
   - 보안 체크

9. **Download Agent** (패키지 생성)
   - ZIP/Docker 이미지 생성
   - 설치 가이드 포함
   - S3 업로드 및 CDN 배포

## 📁 프로젝트 디렉토리 구조

```
T-DeveloperMVP/
├── .amazonq/
│   └── rules/                # 🔴 핵심 설계 문서
│       ├── 00-AI-multi-agent-system-integration-architecture.md
│       ├── 00-T-Developer-system-architecture-design.md
│       ├── MetaRules.md
│       └── phase*.md         # 구현 단계별 규칙
│
├── frontend/                 # React 프론트엔드
├── backend/
│   ├── src/
│   │   ├── agents/          # 에이전트 구현
│   │   │   ├── *.ts         # TypeScript 구현 (현재)
│   │   │   └── implementations/  # Python 구현 (고급)
│   │   ├── agno/            # Agno Framework 통합
│   │   └── aws-agent-squad/ # AWS Agent Squad 통합
│   └── downloads/
│
├── ARCHITECTURE.md          # 시스템 아키텍처
├── CLAUDE.md               # 운영 규칙
└── README.md
```

## 🎨 기술 스택 및 언어 매핑

### Core Frameworks with Language Requirements
```python
framework_language_mapping = {
    # 핵심 프레임워크
    "AWS Agent Squad": {
        "primary": "Python",
        "secondary": "TypeScript",
        "reason": "오케스트레이션 및 에이전트 관리"
    },
    "Agno Framework": {
        "primary": "Python",
        "secondary": None,
        "reason": "고성능 에이전트 생성 (3μs)"
    },
    "AWS Bedrock AgentCore": {
        "primary": "Python",
        "secondary": "JavaScript/TypeScript",
        "reason": "AWS SDK 및 런타임 관리"
    },
    
    # AI 모델 통합
    "OpenAI GPT-4": {
        "primary": "Python",
        "secondary": "TypeScript",
        "reason": "openai 라이브러리"
    },
    "Anthropic Claude": {
        "primary": "Python",
        "secondary": "TypeScript",
        "reason": "anthropic SDK"
    },
    "AWS Bedrock": {
        "primary": "Python (boto3)",
        "secondary": "TypeScript (AWS SDK)",
        "reason": "AWS 네이티브 통합"
    }
}
```

### Component-Specific Language Rules (ECS Deployment)
```yaml
components:
  # 9-Agent Pipeline (ECS Fargate)
  agents:
    current_implementation: "TypeScript"  # 현재 상태
    target_implementation: "Python"       # 목표 (production)
    deployment: "ECS Fargate"            # 모든 에이전트 ECS 통합
    location: 
      - "backend/src/agents/ecs-integrated/*.py" (통합 버전)
      - "backend/src/agents/final/*" (최종 구현)
    
  # Frontend
  web_interface:
    language: "TypeScript"
    framework: "React + Vite"
    reason: "모던 웹 개발 표준"
  
  # Backend API
  api_server:
    current: "TypeScript (Express)"
    target: "Python (FastAPI)"
    reason: "Agent 통합 및 성능"
  
  # AWS Infrastructure (ECS-First)
  infrastructure:
    language: "Python"
    primary_compute: "ECS Fargate"
    tools:
      - "AWS CDK (Python)"
      - "Docker & Docker Compose"
      - "ECS Task Definitions"
      - "CloudFormation (YAML/JSON)"
    
  # Testing
  testing:
    unit_tests: "각 컴포넌트와 동일 언어"
    integration_tests: "Python (pytest)"
    e2e_tests: "TypeScript (Playwright)"
  
  # DevOps
  ci_cd:
    github_actions: "YAML"
    scripts: "Python/Bash"
```

### Language Priority Rules
1. **Python First** (MetaRules.md 준수)
   - 모든 Agent 구현
   - AWS 서비스 통합
   - 데이터 처리 및 AI/ML
   
2. **TypeScript** 
   - Frontend (React)
   - 현재 Backend (마이그레이션 예정)
   - 타입 안전성이 필요한 부분
   
3. **Bash/Shell**
   - 시스템 스크립트
   - 배포 자동화
   
4. **YAML/JSON**
   - 설정 파일
   - CI/CD 파이프라인

## 🚀 ECS Fargate 배포 아키텍처

### ECS 클러스터 구성
```yaml
Cluster: t-developer-cluster
  Service Groups:
    1. Analysis Group (경량 에이전트):
       - Agents: NL Input, UI Selection, Parser
       - Resources: 1 vCPU, 2GB RAM
       - Scaling: 2-10 tasks
       
    2. Decision Group (중간 에이전트):
       - Agents: Component Decision, Match Rate, Search
       - Resources: 2 vCPU, 4GB RAM
       - Scaling: 2-8 tasks
       
    3. Generation Group (무거운 에이전트):
       - Agents: Generation, Assembly, Download
       - Resources: 4 vCPU, 8GB RAM
       - Scaling: 1-5 tasks

  Networking:
    - VPC: Private subnets with NAT
    - ALB: Application Load Balancer
    - Service Discovery: AWS Cloud Map
    
  Storage:
    - EFS: Shared file system for agents
    - S3: Generated project storage
```

### Container 구조
```dockerfile
# 통합 Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY agents/ ./agents/
COPY api/ ./api/
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0"]
```

## ⚙️ 핵심 설계 원칙

### 1. **ECS-First Architecture**
- 모든 에이전트는 ECS Fargate에서 실행
- 완벽한 기능 구현 (Lambda 제약 없음)
- 에이전트 간 직접 메모리 공유

### 2. **Multi-Agent Collaboration**
- 각 에이전트는 전문 영역 담당
- AWS Agent Squad로 조율
- 병렬 처리 최대화

### 3. **Performance & Scalability**
- Auto-scaling으로 부하 대응
- 콜드 스타트 없는 일관된 성능
- 무제한 실행 시간 지원

### 4. **Production Ready**
- Mock 구현 절대 금지
- 모든 코드는 production 수준
- 엔터프라이즈 보안
- Blue/Green 배포

## 📊 성능 목표

- **에이전트 생성**: < 3μs (Agno)
- **메모리 사용**: < 6.5KB per agent
- **전체 파이프라인**: < 30초
- **동시 처리**: 1000+ 요청
- **세션 지속**: 8시간
- **가용성**: 99.99%

## 🔒 보안 고려사항

### AWS Bedrock AgentCore 제공
- 세션 격리
- IAM 기반 인증
- VPC 격리
- 암호화된 통신

### Application Level
- Input validation
- SQL injection 방지
- XSS 방지
- Rate limiting

### 환경변수 관리 아키텍처
```
Local Development (.env file)
         ↓
[Development/Staging/Production]
         ↓
    ┌────────┴────────┐
    ↓                 ↓
Parameter Store    Secrets Manager
(일반 설정)        (민감한 정보)
    ↓                 ↓
    └────────┬────────┘
         ↓
   HybridConfigManager
   (backend/src/config/config-manager.ts)
         ↓
     Application
```

#### Parameter Store 구조
```
/t-developer/
├── development/
│   ├── api_url
│   ├── timeout
│   └── framework_config
├── staging/
│   └── ...
└── production/
    └── ...
```

#### Secrets Manager 구조
```
t-developer/development/openai-api-key
t-developer/development/anthropic-api-key
t-developer/development/aws-bedrock-config
t-developer/production/...
```

## 📝 구현 단계 (Phase)

### 현재 상태
- Phase 0-9 문서 존재 (.amazonq/rules/)
- TypeScript 기본 구현 완료 (Mock 수준)
- Python 고급 구현 준비 (Production 수준)

### 진행 계획
1. **Phase 0-3**: 기초 아키텍처
2. **Phase 4**: 핵심 에이전트 구현 (현재)
3. **Phase 5-6**: 고급 기능
4. **Phase 7-9**: 최적화 및 확장

## 🖥️ Compute 환경별 기능 분리

### Lambda Functions (서버리스)
**특징**: 15분 제한, 10GB 메모리, 빠른 시작, 비용 효율적

#### Lambda에서 실행할 기능
```python
lambda_functions = {
    # 1. 개별 Agent 실행 (단일 책임)
    "agents": [
        "nl-input-agent",      # < 30초 실행
        "ui-selection-agent",  # < 10초 실행
        "parser-agent",        # < 20초 실행
        "match-rate-agent",    # < 15초 실행
        "search-agent",        # < 10초 실행
    ],
    
    # 2. 유틸리티 함수
    "utilities": [
        "validate-input",      # 입력 검증
        "generate-presigned-url",  # S3 URL 생성
        "send-notification",   # 알림 전송
        "cleanup-old-files",   # 정기 정리
    ],
    
    # 3. API Gateway 백엔드
    "api_endpoints": [
        "GET /health",
        "GET /api/v1/frameworks",
        "POST /api/v1/validate",
        "GET /api/v1/status/{id}",
    ],
    
    # 4. 이벤트 핸들러
    "event_handlers": [
        "s3-upload-trigger",   # S3 업로드시
        "sqs-message-processor",  # 큐 메시지 처리
        "scheduled-cleanup",   # 정기 작업
    ]
}
```

### EC2/ECS/Fargate (인스턴스 기반)
**특징**: 장시간 실행, 고메모리, 상태 유지, WebSocket 지원

#### 인스턴스에서 실행할 기능
```python
instance_services = {
    # 1. 장시간 실행 Agent
    "heavy_agents": [
        "component-decision-agent",  # 복잡한 분석
        "generation-agent",     # 대량 코드 생성 (> 1분)
        "assembly-agent",       # 프로젝트 조립 (> 2분)
        "download-agent",       # 패키징 (> 30초)
    ],
    
    # 2. 오케스트레이션 서비스
    "orchestration": [
        "aws-agent-squad",      # Agent 조율
        "supervisor-agent",     # 전체 파이프라인 관리
        "workflow-engine",      # Step Functions 대체
    ],
    
    # 3. 상태 유지 서비스
    "stateful_services": [
        "websocket-server",     # 실시간 통신
        "session-manager",      # 세션 관리
        "cache-service",        # Redis/메모리 캐시
        "queue-processor",      # 큐 관리
    ],
    
    # 4. 메인 애플리케이션
    "main_application": [
        "frontend-server",      # React 앱 서빙
        "api-gateway",         # FastAPI/Express 서버
        "admin-dashboard",     # 관리자 패널
    ],
    
    # 5. AI/ML 워크로드
    "ai_workloads": [
        "model-inference",     # 큰 모델 실행
        "batch-processing",    # 대량 처리
        "training-jobs",       # 모델 학습
    ]
}
```

### 하이브리드 아키텍처
```
사용자 요청
    ↓
API Gateway (Lambda)
    ↓
[경량 작업]              [무거운 작업]
    ↓                        ↓
Lambda Functions        EC2/ECS/Fargate
(개별 Agent)           (파이프라인 전체)
    ↓                        ↓
    └──────────┬──────────┘
               ↓
         S3 (결과 저장)
               ↓
         CloudFront (배포)
```

### 선택 기준

#### Lambda 선택 기준
- ✅ 실행 시간 < 15분
- ✅ 메모리 < 10GB
- ✅ Stateless 작업
- ✅ 이벤트 기반 트리거
- ✅ 간헐적 실행
- ✅ 비용 최적화 필요

#### EC2/Instance 선택 기준
- ✅ 실행 시간 > 15분
- ✅ 메모리 > 10GB
- ✅ Stateful 작업
- ✅ WebSocket 필요
- ✅ 지속적 실행
- ✅ GPU 필요

### 비용 최적화 전략
```python
cost_optimization = {
    "lambda": {
        "strategy": "Request 기반 과금",
        "best_for": "간헐적 실행, 짧은 작업",
        "avoid": "상시 실행, WebSocket"
    },
    "ec2_spot": {
        "strategy": "Spot Instance 활용",
        "best_for": "배치 처리, 중단 가능 작업",
        "savings": "최대 90% 절감"
    },
    "ecs_fargate": {
        "strategy": "컨테이너 기반 실행",
        "best_for": "예측 가능한 워크로드",
        "scaling": "자동 스케일링"
    },
    "ec2_reserved": {
        "strategy": "Reserved Instance",
        "best_for": "24/7 실행 서비스",
        "savings": "최대 72% 절감"
    }
}
```

## 🔄 언어 마이그레이션 로드맵

### Step 1: Agent Migration (우선순위 1)
```python
# 현재: TypeScript (Mock)
backend/src/agents/*.ts

# 목표: Python (Production)
backend/src/agents/implementations/*.py
```
- [ ] NL Input Agent → Python
- [ ] UI Selection Agent → Python  
- [ ] Parser Agent → Python
- [ ] Component Decision Agent → Python
- [ ] Match Rate Agent → Python
- [ ] Search Agent → Python
- [ ] Generation Agent → Python
- [ ] Assembly Agent → Python
- [ ] Download Agent → Python

### Step 2: Backend API Migration (우선순위 2)
```python
# 현재: TypeScript/Express
backend/src/main.ts

# 목표: Python/FastAPI
backend/src/main.py
```
- [ ] FastAPI 서버 구성
- [ ] Agent 통합
- [ ] AWS 서비스 연결

### Step 3: Framework Integration (우선순위 3)
- [ ] Agno Framework 통합 (Python)
- [ ] AWS Agent Squad 통합 (Python)
- [ ] AWS Bedrock AgentCore 통합 (Python)

### Step 4: Infrastructure as Code
- [ ] AWS CDK (Python) 구성
- [ ] Lambda Functions (Python)
- [ ] Step Functions 워크플로우

## ⚠️ 중요 규칙 (MetaRules.md)

1. **규칙 변경 금지**
2. **기능 단순화/제거로 에러 해결 금지**
3. **규칙 유지가 최우선**
4. **pip → uv 명령어 사용**
5. **Python이 주 언어**
6. **규칙 문서의 코드 준수**

## 🚀 지원 프로젝트 타입

- ✅ Web Applications (React, Vue, Angular)
- ✅ Mobile Apps (React Native, Flutter)
- ✅ Backend APIs (Node.js, Python, Java)
- ✅ Desktop Applications (Electron)
- ✅ CLI Tools
- ✅ Microservices
- ✅ Machine Learning Projects
- ✅ Blockchain Applications
- ✅ IoT Applications
- ✅ Game Development

## 📌 절대 준수 사항

**이 아키텍처를 벗어나는 변경 금지:**
- AWS Agent Squad 오케스트레이션 유지
- Agno Framework 성능 기준 준수
- AWS Bedrock AgentCore 런타임 활용
- 9-Agent Pipeline 구조 유지
- .amazonq/rules/ 문서 준수

---
*이 문서는 .amazonq/rules/의 설계를 기반으로 작성되었으며, 모든 개발은 이 아키텍처를 따라야 합니다.*