좋아—지금까지 이 대화에서 합의된 방향(Agno 에이전트, AWS Agent Squad 오케스트레이션, Bedrock AgentCore 운영, Claude Code+MCP, A2A 연동)을 바탕으로 \*\*“스스로 진화하는 서비스 생성 서비스”\*\*를 만들기 위한 **Phase별 실행계획**을 바로 쓸 수 있게 정리했어.
각 Phase는 **목표 → 범위 → 핵심 태스크 → 산출물/아티팩트 → 게이트/지표(Exit 기준)** 순서로 구성했어.

---

# 0. 프로젝트 고정 축(변경 불가 가정)

* **에이전트 구현:** Agno
* **오케스트레이션:** AWS Agent Squad (Supervisor-DAG → 필요 시 Event/Blackboard 확장)
* **운영/런타임:** Amazon Bedrock AgentCore (Runtime/Gateway/Memory/Observability/Identity)
* **코드 생성/수정:** Claude Code (+ MCP: fs/git/github/browser/tracker/runner)
* **외부 상호운용:** A2A(보안/테스트/성능/승인 등 특화 에이전트)

---

# 1. 로드맵 한눈 요약

| Phase | 목표              | 핵심 성과(Exit)                                  |
| ----- | --------------- | -------------------------------------------- |
| P0    | 부트스트랩 & 골격      | repo/CI/MCP/Claude 세팅, OIDC·권한, 샌드박스 실행 OK   |
| P1    | 자가진화 코어 루프      | Research→Plan→Code→Evaluate로 **자동 PR 1건** 성공 |
| P2    | AgentCore 통합/관측 | 로그/트레이스/메트릭 일원화, 실패 재시도/롤백 전략 확정             |
| P3    | 보안/품질 게이트       | Semgrep/CodeQL/테스트/복잡도/Docstring **게이트 통과**  |
| P4    | A2A(보안·테스트)     | SecurityScanner/TestGen 외부 에이전트 연계 **안정화**   |
| P5    | 서비스 “생성” 모듈     | Spec/Blueprint/Infra 에이전트로 **새 스캐폴드 배포**     |
| P6    | 성능·신뢰·비용        | Perf/SLO/Cost 게이트 도입, 회귀율↓·리드타임↓             |
| P7    | 학습/지식 축적        | Memory-Curator, 패턴·사례 축적→계획 정확도↑             |
| P8    | 확장/거버넌스         | Event/Blackboard, 추가 A2A, 정책·컴플라이언스 고도화      |

---

# 2. Phase별 상세 계획

## P0. 부트스트랩 & 골격 (D1–D3)

**목표**: 바로 실행 가능한 리포/CI/권한/MCP/샌드박스 기반 마련
**범위**

* 모노레포 골격 생성(agents/orchestrator/runtime/mcp/a2a/evaluation)
* GitHub OIDC·권한(읽기/PR만, main 직접 push 금지)
* MCP 3종(fs/git/github) + Browser/Tracker 템플릿
* Docker 샌드박스(옵션: Firecracker microVM)
  **핵심 태스크**
* `.github/workflows/ci.yml`(ruff/black/pytest/interrogate/radon) 추가
* `packages/mcp/clients/claude.mcp.json` 작성(화이트리스트 경로)
* `scripts/run_self_evolution.py` 시드
  **산출물**
* 리포 구조/CI 배지, `.env.example`, MCP 설정 JSON, 샌드박스 Dockerfile
  **게이트/지표**
* 로컬/CI에서 **샌드박스 빌드 & 테스트 성공**
* Claude Code가 MCP를 통해 파일 읽기/브랜치 생성까지 확인

---

## P1. 자가진화 코어 루프 (D4–D7)

**목표**: 최소 목표(docstring/type hints)로 **자동 PR**까지
**범위**

* Agno: Research/Planner/Evaluator 스켈레톤 완성
* Codegen: Claude Code(헤드리스/CLI) 연동
* Squad: Supervisor-DAG 라우팅(Research→Plan→Code→Evaluate)
  **핵심 태스크**
* Research: 리포 스캔 결과(insights) 구조화
* Planner: 4시간 단위 DAG 산출
* Codegen: “목표 달성” 태스크→편집→테스트→PR
* Evaluate: docstring coverage/복잡도/품질 점수 집계
  **산출물**
* 최초 **자동 PR 1건**(예: docstring≥80% 달성)
  **게이트/지표**
* `Success=True`, Files Modified ≥ N, Coverage ≥ 80, MI ≥ 65

---

## P2. AgentCore 통합 & 관측 (D8–D10)

**목표**: 실행/권한/관측/메모리 일원화
**범위**

* AgentCore Runtime(세션/스케일), Gateway(깃허브/KB/API), Memory, Observability, Identity 연동
  **핵심 태스크**
* 로그/트레이스/메트릭: goal\_id/trace\_id/plan\_id/pr\_id 전파
* 실패 재시도/써킷브레이커/롤백 정책 정의
* 장기 메모리(Artifacts/Reports) 저장 스키마 정의
  **산출물**
* `agentcore_gateway.py`/`identity.py`/`observability.py` 래퍼
* 대시보드(Goal→PR→Gate 파이프)
  **게이트/지표**
* 모든 단계 로그/메트릭이 AgentCore에서 관측됨
* 실패 케이스 재시도 정책이 실제 동작

---

## P3. 보안·품질 게이트 고도화 (W2)

**목표**: “머지 안전장치” 완성
**범위**

* Semgrep/CodeQL/OSV + Unit/Property/Mutation 테스트
* 복잡도(radon), Docstring(interrogate) 기준
  **핵심 태스크**
* CI 게이트 순서: **보안→테스트→품질→(옵션)SWE-bench 샘플**
* 위험 커맨드 차단, PR-only 정책 확인
  **산출물**
* `.github/workflows/codeql.yml`, `packages/evaluation/*` 설정 파일
  **게이트/지표**
* **경고=차단** 정책 적용, “false positive 허용률” 임계 설정
* PR 자동 통과율(>X%), 회귀율(\<Y%) 기준 수립

---

## P4. A2A(보안·테스트) 외부 에이전트 온보딩 (W3)

**목표**: 외부 전문 에이전트로 효율↑
**범위**

* **SecurityScanner**(Semgrep/CodeQL) A2A 래핑
* **TestGen**(Pynguin/Hypothesis/뮤테이션 스모크) A2A 래핑
  **핵심 태스크**
* A2A 브로커 정책(allow list, 타임아웃, redaction)
* Planner 결과 이벤트 → TestGen 구독(테스트 보강 PR)
* 보안 스캔 리포트 → 머지 게이트 연동
  **산출물**
* `packages/a2a/agent_cards/*.json`, `broker_config.yaml`
  **게이트/지표**
* 보안/테스트 A2A 호출 성공률 ≥ 99%
* 테스트 자동 생성 후 커버리지/변이점수 상승

---

## P5. “서비스 생성” 모듈(핵심) (W4–W6)

**목표**: 요구→스캐폴드→배포까지 **폐루프**
**범위**

* **SpecAgent**: SRS/수용기준/OpenAPI/도메인 모델 산출
* **BlueprintAgent**: 서비스 템플릿(예: CRUD API, 이벤트 처리)
* **InfraAgent**: CDK/IaC로 Ephemeral/Staging/Prod 파이프라인
  **핵심 태스크**
* ContractTestAgent: OpenAPI 기반 계약 테스트 자동화
* GitHub Environments & OIDC, 시크릿/권한 분리
* “스캐폴드 PR → Ephemeral 배포 → 합격기준 검증” 루프
  **산출물**
* 신규 서비스 **초안 배포 1회**(Staging), PR 설명/아키텍처 다이어그램 자동 생성
  **게이트/지표**
* “요구→Staging까지 리드타임” 기준선 확보
* 계약/보안/테스트 게이트 100% 통과

---

## P6. 성능·신뢰·비용 가드 (W6–W8)

**목표**: 운영 수준 지표(SLO/Cost)까지 자동 보증
**범위**

* **PerfTuner A2A**(프로파일링→개선 PR), k6 부하/CHAOS 실험
* **Cost/Compliance Agent**: 비용 상한·라이선스/PII 정책
  **핵심 태스크**
* p95 latency, 오류율, 가용성 SLO 기준/게이트화
* 비용 추정 vs 실제 편차 모니터링, 초과 시 자동 보류/승인 루프
  **산출물**
* 성능·안정 리포트 자동 첨부 PR, 비용/정책 가드
  **게이트/지표**
* SLO 달성률 ≥ 목표, 비용 상한 초과 0건 유지

---

## P7. 학습·지식 축적 (W8–W9)

**목표**: “진화가 진짜 빨라지는” 루프 데이터화
**범위**

* **Memory-Curator**: 성공 패턴/실패 원인/성공 전략 축적
* (옵션) 그래프형 RAG로 설계/코드/변경 히스토리 질의 고도화
  **핵심 태스크**
* 다음 Planner 입력에 **사례 기반 힌트** 주입
* 평가 지표 개선 경향 분석(라운드 수 감소)
  **산출물**
* 패턴 카탈로그, 힌트 룰/프롬프트
  **게이트/지표**
* 동일 유형 이슈 평균 라운드 수 **지속 하락**

---

## P8. 확장/거버넌스/제품화 (W9+)

**목표**: 다팀/대조직/마켓 연동 준비
**범위**

* Event/Blackboard 모델 병행(옵션 B 통합)
* 추가 A2A(승인/리스크/데브옵스) 확대, 정책·감사 추적 강화
  **핵심 태스크**
* ADR(Architecture Decision Record) 운영, 버전/호환성 정책
* 사내/파트너 에이전트 카탈로그 및 비용/권한 모델
  **산출물**
* 운영 가이드, 보안/감사 레포트 템플릿, SLA 문서
  **게이트/지표**
* 조직 표준 준수 평가 통과, 외부 에이전트 카탈로그 ≥ N

---

# 3. 공통 운영 규칙(전 Phase 적용)

* **Idempotency/재시도**: `task_id`·`trace_id` 전 구간 전파, at-least-once + de-dup
* **권한 최소화**: MCP write-scope 화이트리스트, 위험 커맨드 차단, **PR-only**
* **샌드박스 격리**: 빌드/테스트/스캔은 컨테이너(옵션: microVM)에서만
* **게이트 순서**: 보안→테스트(유닛+속성+뮤테이션 스모크)→품질(docstring/MI)→(옵션)SWE-bench
* **로그/감사**: AgentCore Observability로 모든 A2A/MCP/툴 호출 기록

---

# 4. KPI(측정 가능한 성공 기준)

* **리드타임**(Goal→Staging 배포): P5 종료 시 기준선 ≤ X시간
* **PR 자동 통과율**: P3 이후 ≥ X% 유지
* **회귀율**(7일 이내): ≤ Y%
* **테스트 커버리지/뮤테이션 점수**: N% / Killed Ratio↑
* **성능/SLO**: p95 latency, 오류율, 가용성 목표 달성
* **비용 편차**: 추정 vs 실제 편차 ≤ T%
* **학습 효과**: 유사 이슈 라운드 수 월별 하락 추세

---

# 5. 바로 다음 액션(48시간)

1. **P0 착수**: 리포 골격/CI/MCP/샌드박스/OIDC 세팅 커밋
2. **P1 스켈레톤**: Research/Planner/Evaluator/Codegen(Claude) 연결 + Supervisor-DAG
3. **목표 1개 실행**: “docstring 80%” 자동 PR 1건 성공 → 로그/지표 캡처

---

원하면 각 Phase의 \*\*템플릿 파일 세트(예: Squad 라우팅 YAML, MCP/CI 설정, Spec/Blueprint/Infra 스켈레톤)\*\*를 바로 풀어서 드릴게.
