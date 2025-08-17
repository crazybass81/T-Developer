좋아. **불확실성/리스크/의존성**이 큰 핵심 구간만 골라서 **1–2시간 단위 마이크로플랜**으로 재쪼갰어. (각 항목의 Subtask 는 모두 1–2h 타임박스, 산출물 명시)

---

## 1) P0-T2 GitHub OIDC & 권한 정책 (보안 핵심)

* **M1**: OIDC 신뢰 관계 문서화(레포/엔브 별 권한표) → `docs/oidc-matrix.md`
* **M2**: IAM IdP/Role 생성 & Trust 정책 최소화 → `infra/iam-roles.json`
* **M3**: GitHub Environments 생성(Dev/Stage/Prod) & 시크릿 분리 → 설정 스크린샷/리스트
* **M4**: 브랜치 보호(필수 리뷰/PR 전용/푸시 금지) 적용 → 규칙 스냅샷
* **M5**: Actions 워크플로 OIDC 드라이런(권한 탐색) → `artifacts/oidc-dryrun.log`
* **M6**: 최소권한 검증(권한 상승 차단 시나리오) → `artifacts/oidc-perm-test.md`
* **Exit/Gate**: main 직접 푸시 차단, OIDC 토큰으로만 배포 가능, 권한 점검 체크리스트 통과

---

## 2) P1-T4 CodegenAgent (Claude Code + MCP) (핵심 통합)

* **M1**: `claude` 헤드리스 실행 확인(dry-run, no write) → `artifacts/claude-dryrun.log`
* **M2**: MCP 클라이언트 설정(파일/Git/GitHub) + **write-scope 화이트리스트** → `packages/mcp/clients/claude.mcp.json`
* **M3**: 목표 템플릿 작성(“docstring ≥80%/MI≥65”) → `configs/tasks/docstring_goal.yaml`
* **M4**: 샌드박스에서 린트/테스트 러너 호출(MCP runner) → `artifacts/runner-probe.log`
* **M5**: 대상 패키지에 변경 적용 → **로컬 diff 산출(미커밋)** → `artifacts/diff.patch`
* **M6**: 지표 측정 실패 시 재시도 파라미터 조정(온도/컨텍스트) → `artifacts/retry-matrix.md`
* **M7**: 브랜치 `tdev/auto/*` PR 생성 + 요약 코멘트 자동화 → PR 링크/코멘트 캡처
* **Exit/Gate**: PR 생성·테스트 통과·Docstring≥80·MI≥65·위험 커맨드 0

---

## 3) P2-T2 Observability(로그/트레이스/메트릭) (운영 가시성)

* **M1**: 텔레메트리 스키마 정의(IDs: goal/trace/plan/pr) → `docs/telemetry-schema.md`
* **M2**: 에이전트 호출 공통 로거/트레이서 래퍼 추가 → `packages/runtime/observability.py`
* **M3**: 단계별 이벤트 명세(Research/Plan/Code/Eval) → `configs/events.yaml`
* **M4**: 메트릭 수집(성공률/리드타임/재시도수) 계측 → 대시보드 초안 스냅샷
* **M5**: 실패 시퀀스 재현 & 트레이스 체인 확인 → `artifacts/trace-failure.log`
* **Exit/Gate**: 한 사이클의 **전 구간** 로그/스팬/메트릭이 AgentCore에서 조회 가능

---

## 4) P3-T1 보안 스캔(CodeQL/Semgrep/OSV) (게이트 품질)

* **M1**: 언어별 기본 쿼리/룰셋 선택 & 제외경로 합의 → `configs/security/baseline.md`
* **M2**: CodeQL 워크플로 분리/캐시 최적화 → `.github/workflows/codeql.yml`
* **M3**: Semgrep 액션 + 룰 튜닝(오탐 억제 주석/폴더 제외) → `packages/evaluation/semgrep/semgrep.yml`
* **M4**: OSV & 시크릿 스캐너 추가, 테스트용 시크릿 투입·탐지 → `artifacts/secret-detection.log`
* **M5**: “경고=차단” 정책/예외 승인 흐름 문서화 → `docs/security-gates.md`
* **Exit/Gate**: 샘플 PR 3건에서 **오탐률 목표 이하** & 차단 정책 정상 작동

---

## 5) P4-T3 TestGen A2A (테스트 자동 생성)

* **M1**: Pynguin/Hypothesis 호출 인터페이스(A2A 어댑터) → `packages/a2a/testgen/adapter.py`
* **M2**: Planner의 `plan.ready` 이벤트 구독 → `packages/orchestrator/subscriptions.yaml`
* **M3**: 생성 테스트 커밋/라벨 자동화(`test:generated`) → 액션 스크립트
* **M4**: 뮤테이션 스모크(Cosmic Ray) 최소 시나리오 → `packages/evaluation/mutation/cosmic-ray.toml`
* **M5**: 커버리지/변이점수 기준 설정·PR 코멘트 자동 리포트 → 샘플 코멘트 캡처
* **Exit/Gate**: 자동 생성 테스트가 **PR 1건 이상**에 추가되고 게이트 지표 상승

---

## 6) P5-T3 InfraAgent (IaC·환경·시크릿) (배포 토대)

* **M1**: CDK vs Terraform 결정 & 최소 스택 정의 → `docs/iac-choice.md`
* **M2**: Ephemeral 환경 네이밍/TTL/태그 규칙 → `configs/env/ephemeral.yaml`
* **M3**: VPC/SG/로깅 최소 스택 구현 → `infra/cdk/stacks.py`
* **M4**: 시크릿/파라미터 저장소(AgentCore Identity 연계) → `infra/secrets/plan.md`
* **M5**: `plan→apply→smoke` 파이프라인 잡 작성 → `.github/workflows/deploy.yml`
* **M6**: 빈 서비스 스캐폴드로 생성/삭제 드라이런 → `artifacts/deploy-dryrun.log`
* **Exit/Gate**: PR마다 Ephemeral 환경 자동 생성/삭제, 권한·비용 알람 OK

---

## 7) P5-T5 E2E “서비스 생성” 루프 (요구→배포)

* **M1**: 입력 Goal → SpecAgent 호출·SRS/OpenAPI 산출 → `artifacts/SRS.md`, `openapi.yaml`
* **M2**: Blueprint 선택/변수 주입 → 스캐폴드 코드/CI 생성 → `artifacts/scaffold.diff`
* **M3**: InfraAgent로 Ephemeral 배포 → 엔드포인트/헬스체크 URL 확보
* **M4**: ContractTestAgent로 계약 테스트 실행 → `artifacts/contract-report.md`
* **M5**: Codegen(Claude) 구현 → 테스트/보안/품질 게이트 **모두 통과** PR
* **M6**: Staging 자동 배포 & 릴리스 노트 초안 → `artifacts/release-draft.md`
* **Exit/Gate**: **새 서비스 1개** Staging까지 자동화 완료(계약/보안/품질 통과)

---

## 8) P6-T2 SLO 게이트(k6·Chaos)

* **M1**: 목표 SLO 정의(p95, 에러율, 가용성) → `configs/slo.yaml`
* **M2**: k6 시나리오/임계선(thresholds) 작성 → `tests/load/k6-script.js`
* **M3**: Chaos(지연/장애 주입) 최소 셋 구성 → `tests/chaos/plan.md`
* **M4**: CI에 부하·카오스 잡 추가 & 차단 로직 → `.github/workflows/perf-chaos.yml`
* **M5**: SLO 미달 시 자동 재시도/원인 리포트 → `artifacts/slo-fail-report.md`
* **Exit/Gate**: 부하+카오스 통합 파이프라인에서 SLO 기준 만족/차단 로직 작동

---

## 9) P7-T1 Memory-Curator (학습/피드백 루프)

* **M1**: 사례 스키마(컨텍스트/행동/결과/지표) 정의 → `schemas/pattern.json`
* **M2**: 성공/실패 사례 자동 적재 파이프라인 → `packages/memory/curator.py`
* **M3**: 패턴 쿼리 API & Planner 힌트 주입 → `packages/agents/planner_hints.py`
* **M4**: 월별 회귀 지표/라운드 수 변화 리포트 → `artifacts/learning-trend.md`
* **Exit/Gate**: 동일 유형 이슈의 평균 라운드 수 **하락 추세** 확인

---

### 사용 팁

* 각 마이크로 작업은 **산출물 1개**를 남기도록 했어(로그/문서/설정/PR/리포트).
* 위 9개만 먼저 더 쪼개면, 나머지는 4h Subtask 수준으로도 안정적으로 굴러간다.
* 필요하면 특정 항목을 **이슈/보드 업로드용 YAML**로 변환해 줄게.
