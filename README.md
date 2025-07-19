# T-Developer

T-Developer는 AI 기반 자동화된 개발 시스템으로, 사용자의 요청을 받아 계획 수립부터 코드 구현, 테스트, 배포까지 자동으로 수행합니다.

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
- GitHub 계정 및 Personal Access Token
- Slack 워크스페이스 및 Bot Token

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

- `POST /api/tasks`: 새로운 작업 생성
- `GET /api/tasks/{task_id}`: 작업 조회
- `POST /api/slack/events`: Slack 이벤트 처리
- `GET /health`: 헬스 체크

## 사용 방법

### API를 통한 작업 요청

```bash
curl -X POST "http://localhost:8000/api/tasks" \
     -H "Content-Type: application/json" \
     -d '{"request": "사용자가 질문을 입력하면 관련된 정부 지원사업을 검색하여 추천하는 기능을 추가해줘.", "user_id": "web-user"}'
```

### Slack을 통한 작업 요청

Slack 채널에서 다음과 같이 메시지를 작성합니다:

```
@T-Developer: 사용자가 질문을 입력하면 관련된 정부 지원사업을 검색하여 추천하는 기능을 추가해줘.
```

또는

```
T-Developer: 사용자가 질문을 입력하면 관련된 정부 지원사업을 검색하여 추천하는 기능을 추가해줘.
```

## 라이선스

MIT