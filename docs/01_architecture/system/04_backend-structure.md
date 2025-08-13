# 📋 Backend 프로젝트 구조 규칙

## 🎯 목적
정리된 프로젝트 구조 및 유지보수성을 위한 가이드

## 📁 현재 프로젝트 구조

### 1. 📚 문서 (Documentation)
**위치**: `/backend/docs/`
```
docs/
├── deployment/       # 배포 가이드 (IAM, AWS 설정)
├── frontend/         # 프론트엔드 설계 문서
├── roadmap/          # DynamoDB 로드맵
└── PROJECT_STRUCTURE_RULES.md
```

### 2. 🔧 소스 코드 (Source Code)
**위치**: `/backend/src/`
```
src/
├── api/              # API 엔드포인트
│   └── v1/           # API v1 (agent registration)
├── core/             # 핵심 컴포넌트
│   ├── models/       # 데이터베이스 모델
│   ├── registry/     # 에이전트 레지스트리
│   ├── validation/   # 코드 검증
│   └── workflow/     # DAG 워크플로우 엔진
├── agents/           # 에이전트 구현체
└── [기타 모듈들]
```

### 3. 🧪 테스트 (Tests)
**위치**: `/backend/tests/`
```
tests/
├── agents/           # 에이전트별 테스트
├── e2e/             # E2E 테스트
├── integration/     # 통합 테스트
├── unit/            # 단위 테스트
└── [핵심 테스트들]
```

### 4. 🚀 스크립트 (Scripts)
**위치**: `/backend/scripts/`
```
scripts/
├── deploy/          # 배포 스크립트
├── setup/           # 환경 설정
├── utils/           # 유틸리티
└── validation/      # 검증 스크립트
```
- README.md는 예외 (루트에 유지)
- 카테고리별 하위 폴더 구성
- 파일명은 kebab-case 사용 (예: dynamodb-roadmap.md)

### 2. 🧪 테스트 (Tests)
**위치**: `/backend/tests/`
```
tests/
├── unit/             # 단위 테스트
├── integration/      # 통합 테스트
├── e2e/             # End-to-End 테스트
├── fixtures/        # 테스트 데이터
├── mocks/          # Mock 객체
└── conftest.py     # pytest 설정
```

**규칙**:
- 모든 테스트 파일은 `test_*.py` 또는 `*_test.py` 형식
- 테스트 타입별 폴더 분리
- 루트의 단독 테스트 파일은 `tests/`로 이동
- pytest.ini는 루트에 유지 (pytest 요구사항)

### 3. 🔧 설정 파일 (Configuration)
**위치**: 루트 레벨
```
backend/
├── .env.example        # 환경변수 템플릿
├── Dockerfile         # Docker 설정
├── requirements.txt   # Python 의존성
├── pytest.ini        # 테스트 설정
└── agno.config.yaml  # Agno 프레임워크 설정
```

**규칙**:
- 도구별 설정 파일은 루트에 유지
- 환경별 설정은 별도 관리 (.env는 gitignore)

### 4. 🚀 소스 코드 (Source)
**위치**: `/backend/src/`
```
src/
├── agents/           # 9-Agent 구현
├── orchestration/    # 파이프라인 오케스트레이션
├── integrations/     # 외부 서비스 통합
├── config/          # 런타임 설정
├── llm/            # LLM 프로바이더
├── security/       # 보안 모듈
└── main_api.py     # 메인 API
```

**규칙**:
- 비즈니스 로직은 모두 `src/`에 위치
- 기능별 폴더 구성
- Python 파일 우선 (CLAUDE.md 규칙)

### 5. 🔨 스크립트 (Scripts)
**위치**: `/backend/scripts/`
```
scripts/
├── setup/          # 설정 스크립트
├── deploy/         # 배포 스크립트
├── utils/          # 유틸리티
└── validation/     # 검증 스크립트
```

**규칙**:
- 실행 가능한 스크립트만 포함
- 용도별 하위 폴더 구성
- 실행 권한 부여 (chmod +x)

### 6. 🚢 배포 (Deployment)
**위치**: `/backend/deployment/`
```
deployment/
├── ecs/           # ECS 배포 설정
├── local/         # 로컬 배포
└── docker/        # Docker 관련
```

**규칙**:
- 인프라 및 배포 관련 파일
- 환경별 폴더 구성
- IaC (Infrastructure as Code) 파일 포함

## 🚫 금지 사항

1. **루트에 테스트 파일 배치 금지**
   - `test_*.py` 파일은 반드시 `tests/` 폴더에

2. **루트에 문서 파일 난립 금지**
   - README.md 제외하고 모두 `docs/`로

3. **임시 파일 커밋 금지**
   - logs/, cache/, temp/, coverage/ 등

4. **중복 설정 파일 금지**
   - requirements.txt 하나만 유지

## ✅ 정리 체크리스트

- [ ] 모든 `.md` 파일이 적절한 위치에 있는가?
- [ ] 테스트 파일이 `tests/` 폴더에 정리되었는가?
- [ ] 불필요한 임시 파일이 제거되었는가?
- [ ] 설정 파일이 중복되지 않는가?
- [ ] 폴더 구조가 명확한가?

## 🔄 마이그레이션 우선순위

1. **즉시**: 문서 파일 → `docs/`
2. **즉시**: 테스트 파일 → `tests/`
3. **점진적**: TypeScript → Python (CLAUDE.md 규칙)
4. **유지**: 현재 동작하는 구조는 보존

---
*이 규칙은 프로젝트의 성장에 따라 업데이트될 수 있습니다.*