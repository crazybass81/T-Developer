# T-Developer

T-Developer는 사용자 요청을 받아 자동으로 소프트웨어 개발 작업을 수행하는 AI 기반 개발 오케스트레이션 시스템입니다.

## 시스템 개요

T-Developer는 다음과 같은 주요 구성 요소로 이루어져 있습니다:

- **MAO (Multi-Agent Orchestrator)**: 중앙 오케스트레이터로, 작업 흐름을 조정하고 에이전트 간 데이터 흐름을 관리합니다.
- **Agno (계획/지식 에이전트)**: 작업 계획 수립, 지식 검색, 컨텍스트 분석 등을 담당합니다.
- **Amazon Q Developer (코드 구현 에이전트)**: 코드 작성, 수정, 테스트, 배포 등을 담당합니다.
- **컨텍스트 저장소**: DynamoDB와 S3를 사용하여 작업 정보와 아티팩트를 저장합니다.
- **GitHub 연동**: 코드 저장소와 상호작용하여 브랜치 생성, 커밋, PR 생성 등을 수행합니다.
- **Slack 알림**: 작업 상태 및 결과를 Slack 채널에 알립니다.
- **웹 프론트엔드**: 프로젝트 생성, 작업 요청, 모니터링, 결과 확인을 위한 사용자 인터페이스를 제공합니다.

## 설치 및 설정

### 요구 사항

- Python 3.9 이상
- Node.js 14.x 이상 (프론트엔드용)
- AWS 계정 (DynamoDB, S3 사용)
- GitHub 계정 및 토큰
- Slack 봇 토큰 (알림 기능 사용 시)

### 백엔드 설치

1. 저장소 클론:
   ```bash
   git clone https://github.com/crazybass81/T-Developer.git
   cd t-developer
   ```

2. 가상 환경 생성 및 활성화:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # 또는
   venv\\Scripts\\activate  # Windows
   ```

3. 의존성 설치:
   ```bash
   pip install -r requirements.txt
   ```

### 프론트엔드 설치

1. 프론트엔드 디렉토리로 이동:
   ```bash
   cd frontend
   ```

2. 의존성 설치:
   ```bash
   npm install
   ```

### 환경 설정

`.env` 파일을 생성하고 다음 변수를 설정합니다:

```
# 실행 환경 설정
TDEVELOPER_ENV=development  # development, production

# AWS 설정
AWS_REGION=us-east-1
DYNAMODB_TABLE_PREFIX=TDeveloper-
S3_BUCKET_NAME=t-developer-context

# GitHub 설정
GITHUB_TOKEN=your_github_token
GITHUB_REPO=your_repo_name
GITHUB_OWNER=your_github_username
GITHUB_BRANCH_PREFIX=feature/

# Slack 설정
SLACK_BOT_TOKEN=your_slack_bot_token
SLACK_CHANNEL=#your_slack_channel
SLACK_SIGNING_SECRET=your_slack_signing_secret

# AI 모델 설정
AGNO_API_KEY=your_agno_api_key
OPENAI_API_KEY=your_openai_api_key

# JWT 설정
JWT_SECRET=your_jwt_secret_key

# Q Developer 설정
Q_DEVELOPER_WORKSPACE=/tmp/q-workspace

# 기타 설정
NOTIFICATION_LEVEL=normal  # minimal, normal, verbose
HOST=0.0.0.0
PORT=8000
```

## 실행

### 백엔드 서버 실행

```bash
python main.py
```

기본적으로 서버는 `http://0.0.0.0:8000`에서 실행됩니다.

### 프론트엔드 개발 서버 실행

```bash
cd frontend
npm start
```

프론트엔드는 `http://localhost:3000`에서 실행됩니다.

### API 엔드포인트

- `POST /api/tasks`: 새 작업 생성
- `GET /api/tasks/{task_id}`: 작업 상태 조회
- `POST /api/slack/events`: Slack 이벤트 처리
- `GET /health`: 상태 확인

## 사용 방법

### 웹 인터페이스를 통한 사용

1. 브라우저에서 `http://localhost:3000`으로 접속합니다.
2. 프로젝트 생성 화면에서 프로젝트 정보를 입력합니다.
3. 기능 요청 화면에서 자연어로 기능을 요청합니다.
4. 작업 모니터링 화면에서 진행 상황을 확인합니다.
5. 작업 완료 후 결과 확인 화면에서 코드 변경사항과 테스트 결과를 검토합니다.

### API를 통한 작업 요청

```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"request": "Add JWT authentication to the API", "user_id": "user123"}'
```

### Slack을 통한 작업 요청

Slack 채널에서 다음과 같이 메시지를 작성합니다:

```
@T-Developer: Add JWT authentication to the API
```

## 시스템 아키텍처

```
[ 사용자 (웹 UI/Slack/API) ]
         │
         ▼
[ MAO – Multi-Agent Orchestrator ]
         │
         ├──> [ Agno Agent ] (계획/지식)
         │         └──> (컨텍스트 조회)
         │         <-── (계획/분석 반환)
         │
         └──> [ Q Developer Agent ] (코딩/테스트)
                   └──> (코드 변경 및 결과)
         │
         ├──> (컨텍스트 저장 - DynamoDB/S3)
         ├──> (코드 커밋 - GitHub)
         ├──> (배포 트리거)
         └──> (Slack 알림)
```

## 프로젝트 구조

```
t-developer/
├── agents/                # AI 에이전트 구현
│   ├── agno/              # Agno 에이전트
│   └── q_developer/       # Q Developer 에이전트
├── config/                # 설정 모듈
├── context/               # 컨텍스트 저장소
│   ├── dynamo/            # DynamoDB 연동
│   └── s3/                # S3 연동
├── core/                  # 핵심 모듈
│   ├── mao.py             # Multi-Agent Orchestrator
│   └── task.py            # 작업 모델
├── frontend/              # 웹 프론트엔드
│   ├── public/            # 정적 파일
│   └── src/               # 소스 코드
│       ├── components/    # 재사용 컴포넌트
│       ├── pages/         # 페이지 컴포넌트
│       └── styles/        # CSS 스타일
├── slack/                 # Slack 연동
├── tools/                 # 도구 모듈
│   └── git/               # Git/GitHub 도구
├── .env                   # 환경 변수 (생성 필요)
├── .env.example           # 환경 변수 예시
├── main.py                # 애플리케이션 진입점
└── requirements.txt       # Python 의존성
```

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.