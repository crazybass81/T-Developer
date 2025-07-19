# T-Developer

T-Developer는 AI 기반 자동화된 개발 시스템으로, 사용자의 요청을 받아 계획 수립부터 코드 구현, 테스트, 배포까지 자동으로 수행합니다.

## 주요 기능

- **자연어 기반 기능 요청**: 사용자가 자연어로 기능을 요청하면 AI가 이해하고 처리합니다.
- **자동 계획 수립**: Agno 에이전트가 요청을 분석하고 구현 계획을 수립합니다.
- **코드 자동 생성**: Q Developer 에이전트가 계획에 따라 코드를 자동으로 작성합니다.
- **테스트 자동화**: 생성된 코드에 대한 테스트를 자동으로 실행하고, 실패 시 자동 수정을 시도합니다.
- **GitHub 연동**: 자동으로 브랜치 생성, 커밋, PR 생성 및 병합을 수행합니다.
- **Slack 알림**: 작업 진행 상황을 Slack 채널에 실시간으로 알립니다.
- **멀티 프로젝트 지원**: 여러 프로젝트를 관리하고 프로젝트별 GitHub 저장소와 Slack 채널을 설정할 수 있습니다.

## 아키텍처

T-Developer는 다음과 같은 구성 요소로 이루어져 있습니다:

- **MAO (Multi-Agent Orchestrator)**: 중앙 오케스트레이터로, 사용자 요청을 받아 에이전트들을 조율합니다.
- **Agno Agent**: 계획 수립 및 지식 검색을 담당하는 에이전트입니다.
- **Q Developer Agent**: 코드 구현, 테스트, 배포를 담당하는 에이전트입니다.
- **Context Storage**: DynamoDB와 S3를 사용하여 작업 정보와 아티팩트를 저장합니다.
- **GitHub Integration**: 코드 저장소와 연동하여 브랜치 생성, 커밋, PR 생성 등을 수행합니다.
- **Slack Integration**: 작업 상태 변화를 Slack 채널에 알립니다.

## 설치 및 설정

### 요구 사항

- Python 3.8 이상
- AWS 계정 (DynamoDB, S3 사용)
- GitHub 계정 및 Personal Access Token (repo 권한 필요)
- Slack 워크스페이스 및 Bot Token (chat:write 권한 필요)
- OpenAI API 키 (선택사항 - 계획 수립에 사용)

### 설치

1. 저장소 클론:

```bash
git clone https://github.com/your-username/t-developer.git
cd t-developer
```

2. 가상 환경 생성 및 활성화:

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. 의존성 설치:

```bash
pip install -r requirements.txt
```

4. 환경 변수 설정:

`.env.example` 파일을 복사하여 `.env` 파일을 생성하고 필요한 환경 변수를 설정합니다:

```bash
cp .env.example .env
# .env 파일을 편집하여 필요한 값 설정
```

5. 인프라 설정:

```bash
python scripts/setup_infrastructure.py
```

### 실행

```bash
uvicorn main:app --reload
```

## API 엔드포인트

### 작업 관리
- `POST /api/tasks`: 새로운 작업 생성
- `GET /api/tasks/{task_id}`: 작업 조회
- `GET /api/tasks/{task_id}/plan`: 작업 계획 조회
- `GET /api/tasks/{task_id}/diff/{file_path}`: 파일 diff 조회
- `GET /api/tasks/{task_id}/test-log`: 테스트 로그 조회

### 프로젝트 관리
- `POST /api/projects`: 새로운 프로젝트 생성
- `GET /api/projects`: 프로젝트 목록 조회
- `GET /api/projects/{project_id}`: 프로젝트 조회

### 외부 연동
- `POST /api/slack/events`: Slack 이벤트 처리

### 시스템
- `GET /health`: 기본 헬스 체크
- `GET /health/detailed`: 상세 헬스 체크

## 사용 방법

### 프로젝트 생성

```bash
curl -X POST "http://localhost:8000/api/projects" \
     -H "Content-Type: application/json" \
     -d '{"name": "GovChat", "description": "정부 지원사업 매칭 챗봇", "github_repo": "username/repo", "slack_channel": "#channel-name"}'
```

### API를 통한 작업 요청

```bash
curl -X POST "http://localhost:8000/api/tasks" \
     -H "Content-Type: application/json" \
     -d '{"request": "사용자가 질문을 입력하면 관련된 정부 지원사업을 검색하여 추천하는 기능을 추가해줘.", "user_id": "web-user", "project_id": "PROJ-XXXXXXXX-XXXXXXXX"}'
```

### Slack을 통한 작업 요청

Slack 채널에서 다음과 같이 메시지를 작성합니다:

```
@T-Developer: 사용자가 질문을 입력하면 관련된 정부 지원사업을 검색하여 추천하는 기능을 추가해줘.
```

특정 프로젝트를 지정하려면:

```
@T-Developer: project:GovChat 사용자가 질문을 입력하면 관련된 정부 지원사업을 검색하여 추천하는 기능을 추가해줘.
```

### 작업 상태 확인

```bash
curl "http://localhost:8000/api/tasks/TASK-XXXXXXXX-XXXXXXXX"
```

### 계획 상세 보기

```bash
curl "http://localhost:8000/api/tasks/TASK-XXXXXXXX-XXXXXXXX/plan"
```

### 파일 diff 보기

```bash
curl "http://localhost:8000/api/tasks/TASK-XXXXXXXX-XXXXXXXX/diff/path/to/file.py"
```

## 라이선스

MIT

## 제한사항 및 고려사항

- **단일 저장소 지원**: 현재 버전에서는 프로젝트별로 다른 GitHub 저장소를 사용할 수 있지만, 동시에 여러 저장소를 처리하는 기능은 제한적입니다. 프로젝트에 지정된 GitHub 저장소를 사용하려면 프로젝트 생성 시 GitHub 저장소 URL을 지정해야 합니다.
- **PR 자동 병합**: 기본적으로 PR이 생성되면 자동으로 병합됩니다. 수동 코드 리뷰가 필요한 경우 글로벌 컨텍스트에서 `auto_merge` 설정을 `false`로 변경하거나 환경 변수 `AUTO_MERGE`를 `false`로 설정하세요.
- **코드 생성 제한**: 현재 버전에서는 실제 Amazon Q Developer CLI가 없는 경우 모의 구현을 사용합니다. 실제 프로덕션 환경에서는 Amazon Q Developer CLI를 설치하여 사용하는 것이 좋습니다.
- **배포 제한**: 현재 버전에서는 GitHub PR 병합까지만 지원하며, AWS Lambda 등으로의 자동 배포는 구현되지 않았습니다. 자동 배포가 필요한 경우 CI/CD 파이프라인을 별도로 구성해야 합니다.
- **Slack 멘션 패턴**: Slack에서 봇을 멘션하는 경우 `@T-Developer` 형태로 멘션하거나 실제 봇 ID를 사용하여 멘션할 수 있습니다. 멘션은 문장 시작 부분이나 중간에 위치해도 작동합니다.