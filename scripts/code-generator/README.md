# T-Developer Code Generator

자동화된 코드 생성 도구로 반복적인 코드 작성을 효율화합니다.

## 🚀 사용법

### 에이전트 생성
```bash
npm run generate agent my-agent-name
```

대화형 프롬프트를 통해 다음을 선택할 수 있습니다:
- 에이전트 타입: processing, analysis, generation, integration
- 기능: database-access, file-operations, api-calls, llm-integration, caching
- 설명: 에이전트에 대한 설명

### 생성되는 파일
- `backend/src/agents/{name}-agent.ts` - 에이전트 구현
- `backend/tests/agents/{name}-agent.test.ts` - 단위 테스트
- `docs/agents/{name}-agent.md` - 문서

## 📁 템플릿 구조

```
scripts/code-generator/
├── generator.ts          # 메인 생성기
├── templates/            # Handlebars 템플릿
│   ├── agent.hbs        # 에이전트 템플릿
│   ├── agent-test.hbs   # 테스트 템플릿
│   └── agent-doc.hbs    # 문서 템플릿
└── README.md
```

## 🛠️ 템플릿 커스터마이징

Handlebars 템플릿을 수정하여 생성되는 코드를 커스터마이징할 수 있습니다.

### 사용 가능한 변수
- `{{name}}` - 에이전트 이름
- `{{className}}` - PascalCase 클래스명
- `{{type}}` - 에이전트 타입
- `{{capabilities}}` - 선택된 기능 배열
- `{{description}}` - 에이전트 설명

### 헬퍼 함수
- `{{camelCase str}}` - camelCase 변환
- `{{pascalCase str}}` - PascalCase 변환
- `{{includes array value}}` - 배열 포함 여부 확인
- `{{if_eq a b}}` - 값 비교

## 🧪 테스트

```bash
# 설정 테스트
node scripts/test-code-generator.js

# 데모 실행
node scripts/demo-code-generator.js
```

## 📦 의존성

- commander: CLI 인터페이스
- inquirer: 대화형 프롬프트
- handlebars: 템플릿 엔진
- chalk: 컬러 출력