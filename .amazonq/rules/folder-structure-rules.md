# T-Developer MVP 폴더 구조 규칙

## 📁 루트 디렉토리 구조

```
T-DeveloperMVP/
├── .amazonq/                    # Amazon Q 설정 및 규칙
├── backend/                     # 백엔드 서비스 (Python)
├── frontend/                    # 프론트엔드 애플리케이션 (React)
├── docs/                        # 프로젝트 문서
├── scripts/                     # 유틸리티 스크립트
├── docker/                      # Docker 설정
├── infrastructure/              # AWS 인프라 코드
└── .env.example                 # 환경 변수 템플릿
```

## 🔧 Backend 구조 (/backend)

```
backend/
├── src/
│   ├── agents/                  # 9개 핵심 에이전트
│   │   ├── implementations/     # 에이전트 구현체
│   │   │   ├── nl_input/
│   │   │   │   ├── tests/       # 단위 테스트
│   │   │   │   └── nl_input_agent.py
│   │   │   ├── ui_selection/
│   │   │   ├── parser/
│   │   │   ├── component_decision/
│   │   │   ├── match_rate/
│   │   │   ├── search/
│   │   │   ├── generation/
│   │   │   ├── assembly/
│   │   │   └── download/
│   │   └── framework/           # 에이전트 프레임워크
│   ├── orchestration/           # Agent Squad 오케스트레이션
│   ├── data/                    # 데이터 레이어
│   ├── api/                     # API 엔드포인트
│   └── utils/                   # 유틸리티 함수
├── tests/                       # 통합/E2E 테스트
│   ├── integration/             # 통합 테스트
│   └── e2e/                     # E2E 테스트
├── main.py                      # FastAPI 엔트리포인트
├── requirements.txt             # Python 의존성
└── pytest.ini                  # 테스트 설정
```

## 🧪 테스트 구조

### 테스트 파일 위치
- **Unit Tests**: `/backend/src/agents/implementations/{agent}/tests/`
- **Integration Tests**: `/backend/tests/integration/`
- **E2E Tests**: `/backend/tests/e2e/`

### 테스트 파일명
- **Python**: `test_{module_name}.py`

---
**언어**: Python 통일  
**업데이트**: 2024년 12월