# T-Developer 시작하기

이 문서는 T-Developer 시스템을 설정하고 실행하는 방법을 안내합니다.

## 1. 환경 설정

### 1.1 의존성 설치

```bash
pip install -r requirements.txt
```

### 1.2 환경 변수 설정

`.env` 파일을 편집하여 다음 필수 환경 변수를 설정합니다:

- **AWS 자격 증명**: AWS CLI를 통해 설정하거나 환경 변수로 설정합니다.
  ```bash
  export AWS_ACCESS_KEY_ID=your_access_key
  export AWS_SECRET_ACCESS_KEY=your_secret_key
  ```

- **GitHub 연동**: GitHub Personal Access Token과 저장소 정보를 설정합니다.
  ```
  GITHUB_TOKEN=your_github_token
  GITHUB_OWNER=your_github_username
  GITHUB_REPO=your_repository_name
  ```

- **Slack 연동**: Slack Bot Token과 서명 시크릿을 설정합니다.
  ```
  SLACK_BOT_TOKEN=xoxb-your-slack-bot-token
  SLACK_SIGNING_SECRET=your_slack_signing_secret
  ```

- **AI 설정**: OpenAI API 키를 설정합니다.
  ```
  OPENAI_API_KEY=your_openai_api_key
  ```

## 2. 인프라 설정

AWS 리소스(DynamoDB 테이블, S3 버킷)를 생성합니다:

```bash
python scripts/setup_infrastructure.py
```

## 3. 서버 실행

```bash
uvicorn main:app --reload
```

서버가 시작되면 `http://localhost:8000`에서 접근할 수 있습니다.

## 4. API 테스트

### 4.1 작업 생성

```bash
curl -X POST "http://localhost:8000/api/tasks" \
     -H "Content-Type: application/json" \
     -d '{"request": "사용자 인증 기능을 추가해줘.", "user_id": "test-user"}'
```

### 4.2 작업 조회

```bash
curl "http://localhost:8000/api/tasks/TASK-XXXXXXXX-XXXXXXXX"
```

### 4.3 헬스 체크

```bash
curl "http://localhost:8000/health"
```

## 5. Slack 연동 설정

1. [Slack API 웹사이트](https://api.slack.com/apps)에서 새 앱을 생성합니다.
2. 다음 권한을 추가합니다:
   - `chat:write`
   - `chat:write.public`
3. 앱을 워크스페이스에 설치합니다.
4. Bot User OAuth Token을 `.env` 파일의 `SLACK_BOT_TOKEN`에 설정합니다.
5. 이벤트 구독을 활성화하고 요청 URL을 `http://your-server/api/slack/events`로 설정합니다.
6. 다음 이벤트를 구독합니다:
   - `message.channels`
7. 서명 시크릿을 `.env` 파일의 `SLACK_SIGNING_SECRET`에 설정합니다.

## 6. 문제 해결

### 6.1 AWS 자격 증명 오류

AWS 자격 증명이 올바르게 설정되었는지 확인합니다:

```bash
aws sts get-caller-identity
```

### 6.2 Slack 연동 오류

Slack 이벤트 요청 URL이 올바르게 설정되었는지 확인합니다. 로컬 개발 환경에서는 [ngrok](https://ngrok.com/)을 사용하여 공개 URL을 생성할 수 있습니다:

```bash
ngrok http 8000
```

### 6.3 GitHub 연동 오류

GitHub Personal Access Token에 다음 권한이 있는지 확인합니다:
- `repo` (전체 저장소 접근)
- `workflow` (워크플로우 접근, 필요한 경우)

## 7. 로그 확인

로그 파일을 확인하여 문제를 진단합니다:

```bash
tail -f t-developer.log
```