# {{PROJECT_NAME}}

![T-Developer](https://img.shields.io/badge/Generated%20by-T--Developer-blue)
![Version](https://img.shields.io/badge/version-{{VERSION}}-green)
![License](https://img.shields.io/badge/license-{{LICENSE}}-yellow)

## 📋 프로젝트 개요

{{PROJECT_DESCRIPTION}}

### 🎯 주요 기능
{{#FEATURES}}
- {{.}}
{{/FEATURES}}

## 🚀 빠른 시작

### 필수 요구사항
- Node.js {{NODE_VERSION}}+
- {{#REQUIREMENTS}}{{.}}, {{/REQUIREMENTS}}

### 설치
```bash
# 저장소 클론
git clone {{REPOSITORY_URL}}
cd {{PROJECT_NAME}}

# 의존성 설치
npm install

# 환경 변수 설정
cp .env.example .env
# .env 파일을 편집하여 필요한 값 설정
```

### 실행
```bash
# 개발 모드
npm run dev

# 프로덕션 빌드
npm run build

# 프로덕션 실행
npm start
```

## 📚 API 문서

- [API 문서](./docs/api.md)
- [Swagger UI](http://localhost:8000/api-docs)

## 🧪 테스트

```bash
# 모든 테스트 실행
npm test

# 테스트 커버리지
npm run test:coverage
```

## 📦 배포

```bash
# Docker 빌드
docker build -t {{PROJECT_NAME}} .

# Docker 실행
docker run -p 8000:8000 {{PROJECT_NAME}}
```

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 {{LICENSE}} 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 🙏 감사의 말

- [T-Developer](https://t-developer.com) - AI 기반 개발 플랫폼
- 모든 기여자들에게 감사드립니다