# 📚 T-Developer v2.0 사용 가이드

## 🎯 T-Developer란?

T-Developer는 **자연어 요구사항**을 받아서 **자동으로 코드를 생성/수정**하는 AI 기반 개발 도구입니다.

### 핵심 기능
- 🔄 **Evolution Loop**: 요구사항과 현재 상태의 갭이 0이 될 때까지 자동 반복
- 🤖 **15개 전문 AI 에이전트**: 각 분야별 전문가 AI가 협업
- 📊 **완전 자동화**: 분석부터 코드 생성, 테스트까지 자동 수행
- 🚀 **AWS Bedrock 기반**: 100% 실제 AI (Mock 없음)

---

## 🚀 빠른 시작

### 1️⃣ 백엔드 서버 실행
```bash
# T-Developer 디렉토리로 이동
cd /home/ec2-user/T-Developer

# FastAPI 백엔드 서버 시작
python3 -m uvicorn backend.api.upgrade_api:app --host 0.0.0.0 --port 8000 --reload
```

### 2️⃣ 프론트엔드 UI 실행
```bash
# 새 터미널에서
cd /home/ec2-user/T-Developer

# Streamlit UI 시작 (API 연동 버전)
streamlit run frontend/api_app.py --server.port 8503
```

### 3️⃣ 브라우저에서 접속
- UI: http://localhost:8503
- API 문서: http://localhost:8000/docs

---

## 📖 상세 사용법

### 🔧 기존 프로젝트 업그레이드 (UpgradeOrchestrator)

기존 프로젝트를 분석하고 요구사항에 맞게 개선합니다.

#### 사용 예시

1. **UI 접속**: http://localhost:8503

2. **프로젝트 경로 입력**
   ```
   /home/ec2-user/my-django-project
   ```

3. **요구사항 작성 예시**

   **예시 1: 성능 개선**
   ```
   이 Django 프로젝트의 성능을 개선하세요:
   1. 데이터베이스 쿼리 최적화 (N+1 문제 해결)
   2. 캐싱 전략 구현 (Redis 사용)
   3. 비동기 처리 도입 (Celery)
   4. API 응답 시간 50% 단축
   ```

   **예시 2: 보안 강화**
   ```
   보안 취약점을 수정하고 강화하세요:
   1. SQL 인젝션 방지
   2. XSS 공격 방어
   3. CSRF 토큰 구현
   4. API 인증/인가 강화 (JWT)
   5. 민감 데이터 암호화
   ```

   **예시 3: 코드 품질 개선**
   ```
   코드 품질과 유지보수성을 개선하세요:
   1. 타입 힌트 추가 (100% 커버리지)
   2. 테스트 커버리지 85% 이상
   3. 문서화 개선 (docstring 추가)
   4. SOLID 원칙 적용
   5. 중복 코드 제거
   ```

   **예시 4: 기능 추가**
   ```
   다음 기능들을 추가하세요:
   1. GraphQL API 엔드포인트 추가
   2. 실시간 알림 시스템 (WebSocket)
   3. 다국어 지원 (i18n)
   4. 소셜 로그인 (OAuth2)
   5. 파일 업로드 기능 (S3 연동)
   ```

4. **실행 및 모니터링**
   - "🚀 업그레이드 시작" 클릭
   - 실시간 진행 상황 확인
   - Evolution Loop 반복 횟수 모니터링
   - 갭 스코어가 0에 가까워질 때까지 대기

---

### 🆕 새 프로젝트 생성 (NewBuilderOrchestrator)

완전히 새로운 프로젝트를 생성합니다.

#### 사용 예시

1. **요구사항 작성 예시**

   **예시 1: REST API 서버**
   ```
   Python FastAPI로 블로그 REST API 서버를 만드세요:
   1. 사용자 인증 (JWT)
   2. 게시글 CRUD
   3. 댓글 시스템
   4. 태그 기능
   5. 검색 기능
   6. PostgreSQL 사용
   7. Docker 컨테이너화
   8. 테스트 코드 포함
   ```

   **예시 2: 실시간 대시보드**
   ```
   실시간 모니터링 대시보드를 만드세요:
   1. React + TypeScript 프론트엔드
   2. Node.js + Express 백엔드
   3. WebSocket 실시간 통신
   4. 차트 시각화 (Chart.js)
   5. 알림 시스템
   6. 사용자별 대시보드 커스터마이징
   7. MongoDB 데이터 저장
   ```

   **예시 3: CLI 도구**
   ```
   파일 관리 CLI 도구를 만드세요:
   1. 파일 검색 (정규식 지원)
   2. 일괄 이름 변경
   3. 중복 파일 찾기
   4. 파일 동기화
   5. 압축/압축해제
   6. 진행률 표시
   7. 설정 파일 지원
   ```

---

## 🔄 Evolution Loop 이해하기

### 작동 원리

```
요구사항 입력
    ↓
[반복 시작] ←─────────┐
    ↓                 │
1. 요구사항 분석      │
    ↓                 │
2. 현재 상태 분석     │
    ↓                 │
3. 갭 분석            │
    ↓                 │
갭 > 0? ──Yes─→ 4. 개선 작업
    ↓                 │
   No                 │
    ↓                 │
[완료]        ←───────┘
```

### 각 단계별 에이전트

| 단계 | 에이전트 | 역할 |
|------|---------|------|
| 요구사항 분석 | RequirementAnalyzer | 자연어 요구사항 해석 |
| 현재 상태 분석 | StaticAnalyzer, CodeAnalysisAgent 등 5개 | 코드 분석 |
| 외부 리서치 | ExternalResearcher | 최신 기술 조사 |
| 갭 분석 | GapAnalyzer | 요구사항과 현재 상태 차이 계산 |
| 아키텍처 설계 | SystemArchitect | 시스템 구조 설계 |
| 계획 수립 | PlannerAgent | 구현 계획 작성 |
| 코드 생성 | CodeGenerator | 실제 코드 작성 |
| 테스트 | TestAgent | 테스트 실행 및 검증 |

---

## 💡 효과적인 요구사항 작성법

### ✅ 좋은 예시

```
"사용자 인증 시스템을 구현하세요:
1. 이메일/비밀번호 로그인
2. 소셜 로그인 (Google, GitHub)
3. 2단계 인증 (TOTP)
4. 비밀번호 재설정
5. 세션 관리
6. API는 RESTful 규칙 준수
7. PostgreSQL 사용
8. 테스트 커버리지 80% 이상"
```

**좋은 이유:**
- 구체적인 기능 명시
- 기술 스택 명확
- 측정 가능한 목표

### ❌ 나쁜 예시

```
"좋은 웹사이트 만들어줘"
```

**나쁜 이유:**
- 너무 모호함
- 구체적 요구사항 없음
- 성공 기준 불명확

---

## 📊 결과물

### 생성되는 문서들

1. **requirements_analysis.md**: 요구사항 분석 결과
2. **gap_analysis.md**: 현재 상태와 목표 차이
3. **architecture_design.md**: 시스템 설계 문서
4. **implementation_plan.md**: 구현 계획
5. **test_report.md**: 테스트 결과
6. **evolution_history.json**: Evolution Loop 히스토리

### 코드 결과물

- 완성된 소스 코드
- 테스트 코드
- 설정 파일
- Docker 파일 (요청 시)
- CI/CD 파이프라인 (요청 시)

---

## 🔧 고급 설정

### API 직접 호출

```python
import requests

# 업그레이드 요청
response = requests.post(
    "http://localhost:8000/upgrade",
    json={
        "requirements": "성능을 50% 개선하세요",
        "project_path": "/path/to/project",
        "enable_dynamic_analysis": True,
        "include_behavior_analysis": True,
        "generate_impact_matrix": True
    }
)

task_id = response.json()["task_id"]

# 상태 확인
status = requests.get(f"http://localhost:8000/status/{task_id}")
print(status.json())
```

### 프로그래매틱 사용

```python
from backend.packages.orchestrator.upgrade_orchestrator import (
    UpgradeOrchestrator, 
    UpgradeConfig
)

# 설정
config = UpgradeConfig(
    project_path="/path/to/project",
    enable_evolution_loop=True,
    max_iterations=10,
    convergence_threshold=0.95
)

# 실행
orchestrator = UpgradeOrchestrator(config)
await orchestrator.initialize()
result = await orchestrator.execute_evolution_loop(
    "GraphQL API로 마이그레이션하세요"
)
```

---

## ❓ FAQ

### Q: Evolution Loop가 끝나지 않아요
A: 최대 반복 횟수(기본 10회)에 도달하면 자동 종료됩니다. 요구사항이 너무 복잡하면 단계적으로 나누세요.

### Q: 갭 스코어란?
A: 요구사항과 현재 상태의 차이를 0~1로 표현. 0에 가까울수록 요구사항 달성.

### Q: Mock 에러가 발생해요
A: T-Developer는 100% 실제 AI를 사용합니다. AWS Bedrock 설정을 확인하세요.

### Q: 어떤 언어를 지원하나요?
A: Python, JavaScript, TypeScript, Java, Go, Rust 등 대부분의 언어 지원.

### Q: 기존 코드가 삭제될까요?
A: 아니요. 모든 변경사항은 git으로 관리되며, 롤백 가능합니다.

---

## 🚨 주의사항

1. **비용**: AWS Bedrock API 호출 비용 발생
2. **시간**: 복잡한 요구사항은 처리 시간이 길 수 있음
3. **리소스**: Evolution Loop 동안 CPU/메모리 사용량 높음
4. **백업**: 중요한 프로젝트는 반드시 백업 후 실행

---

## 📞 지원

- GitHub Issues: https://github.com/your-org/t-developer/issues
- 문서: 이 파일 (docs/USER_GUIDE.md)
- API 문서: http://localhost:8000/docs

---

**버전**: 2.0.0
**업데이트**: 2025-08-23