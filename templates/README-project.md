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
{{#REQUIREMENTS}}
- {{.}}
{{/REQUIREMENTS}}

### 설치
```bash
# 저장소 클론
git clone {{REPOSITORY_URL}}
cd {{PROJECT_NAME}}

# 의존성 설치
npm install

# 환경 변수 설정
cp .env.example .env
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

## 🏗️ 프로젝트 구조

```
{{PROJECT_NAME}}/
├── src/
│   ├── controllers/    # API 컨트롤러
│   ├── services/       # 비즈니스 로직
│   ├── models/         # 데이터 모델
│   ├── routes/         # API 라우트
│   └── utils/          # 유틸리티 함수
├── tests/              # 테스트 파일
├── docs/               # 문서
└── scripts/            # 스크립트
```

## 📚 API 문서

- 개발: http://localhost:{{PORT}}/api-docs
- 프로덕션: {{PRODUCTION_URL}}/api-docs

## 🧪 테스트

```bash
# 단위 테스트
npm run test:unit

# 통합 테스트
npm run test:integration

# 전체 테스트
npm test
```

## 🔧 환경 변수

| 변수명 | 설명 | 기본값 |
|--------|------|--------|
{{#ENV_VARS}}
| {{NAME}} | {{DESCRIPTION}} | {{DEFAULT}} |
{{/ENV_VARS}}

## 🤝 기여하기

기여를 환영합니다! [CONTRIBUTING.md](./CONTRIBUTING.md)를 참고해주세요.

## 📄 라이선스

이 프로젝트는 {{LICENSE}} 라이선스 하에 배포됩니다.

---

Generated with ❤️ by [T-Developer](https://github.com/t-developer)