좋아요. 각 Phase의 **범위(Scope)** 항목을 **Task**로 승격하고, 각 Task 아래에 **4시간 단위 Subtask**를 쪼개서 정리했습니다.
형식: `P{phase}-T{n}` / `P{phase}-T{n}-S{m}` (모든 Subtask는 4h 기준)

---

# P0. 부트스트랩 & 골격

**P0-T1: 모노레포/초기 골격 구성**

* P0-T1-S1: 모노레포 디렉터리/패키지 스캐폴딩 생성(agents/orchestrator/runtime/mcp/a2a/evaluation)
* P0-T1-S2: 공통 툴링(pyproject/ruff/black/radon/interrogate/pytest) 설정
* P0-T1-S3: `.env.example`/스크립트(`bootstrap.sh`, `run_self_evolution.py`) 초안 작성
* P0-T1-S4: README(개발/실행 방법, 브랜치 전략) 1차 작성

**P0-T2: GitHub OIDC & 권한 정책**

* P0-T2-S1: GitHub OIDC 연동 및 AWS/IAM 역할 매핑
* P0-T2-S2: 브랜치 보호 규칙(main 보호, PR 필수, 리뷰 최소 인원)
* P0-T2-S3: PR 템플릿/라벨/체크리스트 자동화
* P0-T2-S4: 시크릿/권한 분리(Repo→Env/Environment Secrets)

**P0-T3: MCP 기본 3종 + Browser/Tracker 템플릿**

* P0-T3-S1: Filesystem MCP 서버 설정(화이트리스트 경로)
* P0-T3-S2: Git MCP 서버 설정(브랜치 화이트리스트)
* P0-T3-S3: GitHub MCP 서버 설정(PR 생성/코멘트 기능)
* P0-T3-S4: Browser/Tracker(Jira/Linear) 템플릿 추가(허용 도메인/프로젝트 키)

**P0-T4: 샌드박스 실행환경(Docker, 옵션: Firecracker)**

* P0-T4-S1: Dockerfile/런 스크립트 작성(비root, no-new-privileges)
* P0-T4-S2: 리소스 제한(CPU/Mem/PIDs) 및 마운트 정책
* P0-T4-S3: 샌드박스에서 테스트/빌드 실행 검증
* P0-T4-S4: (옵션) microVM(ignite) 스펙 초안 작성

**P0-T5: CI 베이스라인 파이프라인**

* P0-T5-S1: 린트/포맷(ruff/black) 잡 추가
* P0-T5-S2: 테스트(pytest) 잡 추가
* P0-T5-S3: 품질(interrogate/radon) 잡 추가
* P0-T5-S4: 배지/결과 요약 아티팩트 업로드

---

# P1. 자가진화 코어 루프

**P1-T1: ResearchAgent(Agno)**

* P1-T1-S1: 리포 스캔(누락 docstring/type hints/테스트) 로직
* P1-T1-S2: KB/문서/이슈 트리밍 및 인사이트 JSON 스키마
* P1-T1-S3: MCP(Browser/Tracker/GitHub) 호출 어댑터
* P1-T1-S4: 유닛 테스트/샘플 인사이트 생성

**P1-T2: PlannerAgent(Agno)**

* P1-T2-S1: 4h 단위 태스크 분해 규칙/히ュー리스틱
* P1-T2-S2: DAG 모델(의존성/리스크/우선순위) 스키마
* P1-T2-S3: 인사이트→DAG 변환 파이프라인
* P1-T2-S4: 예제 DAG/가짜 데이터 기반 테스트

**P1-T3: EvaluatorAgent(Agno)**

* P1-T3-S1: docstring coverage 수집(interrogate)
* P1-T3-S2: 복잡도/MI 수집(radon) + 품질 스코어 산식
* P1-T3-S3: 리포트 아티팩트(JSON/Markdown) 생성
* P1-T3-S4: 성공 판정 로직(임계치) 테스트

**P1-T4: CodegenAgent(Claude Code + MCP)**

* P1-T4-S1: 헤드리스/CLI 또는 SDK 실행 래퍼
* P1-T4-S2: MCP(fs/git/github) 바인딩 및 작업 스코프 제한
* P1-T4-S3: “docstring ≥80%” 목표 템플릿 태스크 작성
* P1-T4-S4: 변경→테스트→PR 자동 생성 E2E 검증

**P1-T5: Squad Supervisor-DAG 라우팅**

* P1-T5-S1: 라우팅 규칙(intent→agent) 정의
* P1-T5-S2: 엔트리포인트/파이프라인 연결
* P1-T5-S3: 인자/컨텍스트(Repo/Branch/Goal) 전파
* P1-T5-S4: 최초 자동 PR 1건 생성 리허설

---

# P2. AgentCore 통합 & 관측

**P2-T1: AgentCore SDK 래퍼(Runtime/Gateway/Identity)**

* P2-T1-S1: Gateway 툴(깃헙/KB/API) 호출 래퍼
* P2-T1-S2: Identity/IAM 컨텍스트 추출/전파
* P2-T1-S3: Runtime 세션/리소스 구성
* P2-T1-S4: 샘플 호출/권한검증 테스트

**P2-T2: Observability(로그/트레이스/메트릭)**

* P2-T2-S1: trace\_id/goal\_id/plan\_id/pr\_id 전 구간 삽입
* P2-T2-S2: 단계별 이벤트(Log/Span) 표준화
* P2-T2-S3: 메트릭(성공/실패/리드타임) 수집
* P2-T2-S4: 대시보드 뷰(Goal→PR→Gate) 구성

**P2-T3: 실패 처리/재시도/롤백 정책**

* P2-T3-S1: 재시도 전략(백오프/최대 시도)
* P2-T3-S2: 써킷브레이커/타임아웃 설정
* P2-T3-S3: 롤백(브랜치/PR/아티팩트) 시나리오
* P2-T3-S4: 카나리/드라이런 플래그 추가

**P2-T4: 장기 메모리/아티팩트 저장**

* P2-T4-S1: Artifact 스키마 및 스토리지 선택
* P2-T4-S2: 저장/조회 API 래퍼
* P2-T4-S3: 보존/정리(보관주기) 정책
* P2-T4-S4: 샘플 아티팩트 적재/조회 테스트

---

# P3. 보안·품질 게이트 고도화

**P3-T1: 보안 스캔(CodeQL/Semgrep/OSV)**

* P3-T1-S1: CodeQL 워크플로 구성/쿼리셋 선택
* P3-T1-S2: Semgrep 룰셋/액션 통합
* P3-T1-S3: OSV/시크릿 검출 추가
* P3-T1-S4: “경고=차단” 정책/가중치 설정

**P3-T2: 테스트 강화(Unit/Property/Mutation)**

* P3-T2-S1: Pytest 레이아웃/픽스처 표준화
* P3-T2-S2: Hypothesis 속성 테스트 예제 추가
* P3-T2-S3: Cosmic Ray(뮤테이션) 스모크
* P3-T2-S4: 커버리지/뮤테이션 지표 수집

**P3-T3: 품질 지표(Interrogate/Radon)**

* P3-T3-S1: Docstring 임계치 설정 및 리포트
* P3-T3-S2: MI/CC 기준 및 차단 로직
* P3-T3-S3: 통합 리포트(보안/테스트/품질) 생성
* P3-T3-S4: PR 코멘트/체크와 연동

**P3-T4: CI 게이트 정렬 & 위험 명령 차단**

* P3-T4-S1: 파이프 순서(보안→테스트→품질) 적용
* P3-T4-S2: 위험 커맨드 차단/허용 목록
* P3-T4-S3: PR-only 정책 확증(직접 push 차단)
* P3-T4-S4: 실패 패턴 알림/이슈 자동 생성

---

# P4. A2A 외부 에이전트 온보딩(보안/테스트)

**P4-T1: A2A 브로커/정책**

* P4-T1-S1: 브로커 배치/등록
* P4-T1-S2: capability allow-list/타임아웃
* P4-T1-S3: redaction(경로/토큰) 정책
* P4-T1-S4: 감사 로그/관측 연동

**P4-T2: SecurityScanner A2A 래핑**

* P4-T2-S1: 스캔 API 어댑터/결과 정규화
* P4-T2-S2: 머지 게이트와 결합(차단 사유 표준화)
* P4-T2-S3: 샌드박스/리포 권한 최소화
* P4-T2-S4: 실패/재시도/써킷 테스트

**P4-T3: TestGen A2A 래핑**

* P4-T3-S1: Pynguin/Hypothesis/뮤테이션 호출 포맷
* P4-T3-S2: Planner의 `plan.ready` 이벤트 구독
* P4-T3-S3: 생성 테스트 PR 커밋/라벨 자동화
* P4-T3-S4: 커버리지 상승/회귀 방지 검증

---

# P5. “서비스 생성” 모듈

**P5-T1: SpecAgent(요구→사양)**

* P5-T1-S1: 입력 포맷(자연어→SRS) 프롬프트/스키마
* P5-T1-S2: OpenAPI/도메인 모델 생성 로직
* P5-T1-S3: 수용기준 템플릿/검증 체크리스트
* P5-T1-S4: 샘플 3종에 대한 일관성 테스트

**P5-T2: BlueprintAgent(스캐폴딩)**

* P5-T2-S1: 블루프린트 카탈로그(예: CRUD/이벤트) 구조화
* P5-T2-S2: 템플릿 변수(언어/프레임워크/DB/버스/인증)
* P5-T2-S3: 코드/CI/문서/헬스체크 동시 생성
* P5-T2-S4: 샘플 생성→빌드/테스트 검증

**P5-T3: InfraAgent(IaC·환경·시크릿)**

* P5-T3-S1: CDK/Terraform 선택·스택 설계
* P5-T3-S2: Ephemeral/Staging/Prod 파이프라인 IaC
* P5-T3-S3: GitHub Environments/OIDC 연결
* P5-T3-S4: 배포 스모크 테스트

**P5-T4: ContractTestAgent(계약 테스트)**

* P5-T4-S1: OpenAPI 기반 스키마/계약 검증 러너
* P5-T4-S2: 목 서버/샘플 시나리오 구성
* P5-T4-S3: PR 게이트 연동(불일치 차단)
* P5-T4-S4: 리포트/요약 코멘트 자동화

**P5-T5: E2E 서비스 생성 루프**

* P5-T5-S1: Goal→Spec→Blueprint 연계
* P5-T5-S2: Infra 배포→Ephemeral 환경 가동
* P5-T5-S3: Codegen(Claude) 구현→PR
* P5-T5-S4: Gate 통과 후 Staging 배포

---

# P6. 성능·신뢰·비용 가드

**P6-T1: PerfTuner A2A**

* P6-T1-S1: 프로파일러/벤치 러너 통합
* P6-T1-S2: 핫스팟 리포트→패치 제안 포맷
* P6-T1-S3: 샌드박스에서의 안전 실행/검증
* P6-T1-S4: 자동 PR/라벨링/회귀 체크

**P6-T2: 부하/카오스 & SLO 게이트**

* P6-T2-S1: k6 시나리오/목표치(p95, 에러율) 정의
* P6-T2-S2: 장애 주입(chaos) 최소 셋 구성
* P6-T2-S3: SLO 미달 시 차단/재시도 플로우
* P6-T2-S4: 결과 리포트 PR 코멘트/대시보드

**P6-T3: Cost/Compliance Agent**

* P6-T3-S1: 비용 추정/실측 수집 파이프라인
* P6-T3-S2: 상한/정책 위반 차단 로직
* P6-T3-S3: 라이선스/PII 규정 체크
* P6-T3-S4: 승인 워크플로(A2A Change-Approver)

---

# P7. 학습·지식 축적

**P7-T1: Memory-Curator**

* P7-T1-S1: 성공/실패 패턴 스키마(사례/맥락/메트릭)
* P7-T1-S2: 저장/검색 API + 인덱싱
* P7-T1-S3: 프라이버시/보존 정책
* P7-T1-S4: 샘플 쿼리/리포트

**P7-T2: 패턴 카탈로그 & 힌트 주입**

* P7-T2-S1: 반복 이슈 유형 군집화
* P7-T2-S2: “플래너 힌트” 규칙/프롬프트 작성
* P7-T2-S3: 힌트 A/B 실험(라운드 수 비교)
* P7-T2-S4: 성공 패턴 확대 적용

**P7-T3: (옵션) 그래프 RAG**

* P7-T3-S1: 설계/코드/리포 문서 그래프 구축
* P7-T3-S2: 질의 파이프라인(플래너/리서치 연동)
* P7-T3-S3: 품질/속도 튜닝
* P7-T3-S4: 보안/접근 제어

---

# P8. 확장/거버넌스/제품화

**P8-T1: Event/Blackboard 모델 병행**

* P8-T1-S1: 이벤트 스키마/토픽 정의
* P8-T1-S2: 퍼블리시/서브스크립션 구현
* P8-T1-S3: 중복/순서 보장/리트라이 정책
* P8-T1-S4: DAG↔Event 하이브리드 플로우 검증

**P8-T2: 추가 A2A 온보딩**

* P8-T2-S1: 승인/리스크/데브옵스형 외부 에이전트 조사
* P8-T2-S2: Agent Card/정책/한도 설정
* P8-T2-S3: 샌드박스·권한 검증
* P8-T2-S4: 운영 지표/비용 모니터링

**P8-T3: 거버넌스/ADR/감사**

* P8-T3-S1: ADR 템플릿/결정 기록 프로세스
* P8-T3-S2: 규정 준수 체크리스트/자동화
* P8-T3-S3: 감사 로그/보관 주기
* P8-T3-S4: 보안/컴플라이언스 리뷰 주기화

**P8-T4: 카탈로그/비용·쿼터**

* P8-T4-S1: 내부/파트너 에이전트 카탈로그 페이지
* P8-T4-S2: 가격/쿼터/우선순위 정책
* P8-T4-S3: 소비/청구 대시보드
* P8-T4-S4: 온보딩 가이드/SLAs

---

필요하면 위 목록을 **이슈/보드 업로드용 YAML/CSV**로 변환해 드릴게요.
