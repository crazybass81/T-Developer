# T-Developer 개발자 가이드

## 📚 목차

### 1. [시작하기](./getting-started.md)
- 시스템 요구사항
- 설치 및 설정
- 첫 프로젝트 생성

### 2. [아키텍처 개요](./architecture.md)
- 시스템 아키텍처
- 멀티 에이전트 시스템
- 기술 스택

### 3. [에이전트 개발](./agents/)
- [에이전트 프레임워크](./agents/framework.md)
- [에이전트 타입](./agents/types.md)
- [커스텀 에이전트 개발](./agents/custom.md)

### 4. [API 레퍼런스](./api/)
- [인증](./api/authentication.md)
- [프로젝트 관리](./api/projects.md)
- [에이전트 제어](./api/agents.md)
- [웹소켓 이벤트](./api/websocket.md)

### 5. [통합 가이드](./integrations/)
- [AWS 서비스](./integrations/aws.md)
- [GitHub 연동](./integrations/github.md)
- [CI/CD 파이프라인](./integrations/cicd.md)

### 6. [베스트 프랙티스](./best-practices/)
- [보안](./best-practices/security.md)
- [성능 최적화](./best-practices/performance.md)
- [에러 처리](./best-practices/error-handling.md)

### 7. [문제 해결](./troubleshooting/)
- [일반적인 문제](./troubleshooting/common-issues.md)
- [디버깅 가이드](./troubleshooting/debugging.md)
- [FAQ](./troubleshooting/faq.md)

## 🚀 빠른 시작

T-Developer는 AI 기반 멀티 에이전트 개발 플랫폼입니다.

### 전제 조건
- Node.js 18+
- Python 3.9+
- AWS 계정
- Docker

### 설치
```bash
git clone https://github.com/your-org/t-developer.git
cd t-developer
npm install
```

## 🤝 기여하기

문서 개선에 기여하고 싶으시다면:

1. 이슈 생성 또는 기존 이슈 확인
2. 브랜치 생성: `git checkout -b docs/improve-guide`
3. 변경사항 커밋: `git commit -m "docs: improve developer guide"`
4. Pull Request 생성