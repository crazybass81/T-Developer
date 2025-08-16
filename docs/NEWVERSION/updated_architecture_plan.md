좋아, “구조가 아직 확실하지 않다”는 전제를 받아서 **결정이 미완인 부분을 안전하게 열어두면서도** 바로 구현을 시작할 수 있는 형태로 정리해 줄게. 아래는 **고정(Invariants)**, **대안 아키텍처 3종(트레이드오프 포함)**, **변경에 강한 최소 인터페이스(Contract)**, **기본 실행 플로우/관측/보안 가드레일**, **짧은 검증 로드맵** 순서야.
— 질문 없이도 진행 가능하도록 기본값까지 제시했어.

---

# 0) 고정값(이 프로젝트에서 반드시 유지할 축)

* **에이전트 구현:** Agno
* **오케스트레이션:** AWS Agent Squad
* **운영/런타임:** Amazon Bedrock AgentCore
* **코드 생성/수정:** Claude Code(+ MCP 툴 플레인)
* **외부 상호운용:** A2A (옵션 확장)

---

# 1) 아키텍처 옵션 3종 (서로 호환 가능)

## 옵션 A) **Supervisor‑DAG 파이프라인** (기본 추천, 바로 가동 가능)

* **개념:** Squad의 Supervisor가 “Research → Plan → Code → Evaluate”를 **직렬/부분 병렬** DAG로 실행.
* **장점:** 단순/디버깅 용이, SLA 예측, 초기 MTTR 낮음.
* **단점:** 에이전트 수가 많아지면 DAG 관리 복잡도↑, 동적 협력(외부 A2A) 유연성↓.
* **언제:** v1\~v2 자가진화(문서화/타입힌트/리팩토링) 단계.

## 옵션 B) **블랙보드(Event Bus) 모델** (중기 확장)

* **개념:** “Blackboard(상태 보드)”에 이벤트/상태를 게시하면, 구독 중인 에이전트가 조건 매칭 시 **스스로 작업 픽업**.
* **장점:** 느슨한 결합, **부분 실패 격리** 훌륭, 새 에이전트 추가 쉬움.
* **단점:** 전역 일관성/중복 작업 제어가 필요, 관측/디버깅 난도↑.
* **언제:** 다수 리포/팀/서비스 대상 **병렬 진화** 진입 시.

## 옵션 C) **연합/마켓형(A2A 중심) 오케스트레이션** (장기)

* **개념:** 내부 Supervisor는 최소 코어만 유지, 다수 기능은 **외부 에이전트(A2A)** 위임(보안/성능튜닝/비용승인 등).
* **장점:** 생태계 확장/전문화 활용, 비용 최적화.
* **단점:** 계약 합의/권한 위임/관측 경계 복잡.
* **언제:** 파트너 에이전트/사내 여러 팀과의 **광역 협업** 필요 시.

### 실무 권장 조합

* **시작:** 옵션 A (DAG)로 **핵심 루프** 고정
* **확장:** 일부 서브태스크(보안/테스트/문서화)를 옵션 B로 이벤트화
* **장기:** 옵션 C로 특정 고난도 태스크를 외부 에이전트에 위임

---

# 2) 변경 친화적 **최소 인터페이스(Contract) 세트**

> 이 5개만 고정하면, A↔B↔C 간 구조 변경 시에도 코드는 대부분 재사용 가능.

### 2.1 AgentSpec

```ts
type AgentInput = {
  intent: "research" | "plan" | "code" | "evaluate" | string;
  task_id: string;            // idempotency key
  payload: Record<string, any>;
  ctx?: { repo: string; branch: string; user?: string; };
};

type AgentOutput = {
  task_id: string;
  status: "ok" | "retry" | "fail";
  artifacts?: Artifact[];
  metrics?: Record<string, number>;
  events?: Event[];           // 옵션 B, C용
  next?: { intent: string; payload: any }[]; // DAG 확장용
};
```

### 2.2 Artifact (변경 결과의 최소 단위)

```ts
type Artifact = {
  kind: "diff" | "file" | "report" | "pr" | "metric";
  ref: string;               // path or PR URL
  meta?: Record<string, any>;
};
```

### 2.3 Event (옵션 B/C 확장)

```ts
type Event = {
  type: string;              // e.g., "code.patch.ready"
  key: string;               // de-dup 기준
  data: any;
  visibility: "internal" | "a2a";
};
```

### 2.4 ToolSpec (MCP/게이트웨이에 공통)

```ts
type ToolCall = {
  tool: "fs"|"git"|"github"|"tracker"|"kb"|"scanner"|"runner";
  action: string;            // e.g., "open_pr","scan","run_tests"
  args: Record<string, any>;
};
```

### 2.5 Policy (가드레일)

```ts
type Policy = {
  write_scope: string[];     // 편집 가능 디렉터리
  require_pr: boolean;       // main 직접 push 금지
  test_gate: { min_coverage: number; mutation_smoke: boolean; };
  security_gate: { codeql: boolean; semgrep: boolean; };
};
```

---

# 3) 기본 실행 플로우(옵션 A 기준, 옵션 B/C로 쉽게 이행 가능)

1. **User/Goal** → Squad Supervisor에 Goal 전달
2. **ResearchAgent**: 리포/이슈/KB 스캔 → 개선 후보/리스크/벤치마크 산출(Artifact: `report`)
3. **PlannerAgent**: 4h 단위 DAG 생성(Artifact: `plan.report`)
4. **CodegenAgent(Claude Code)**: MCP로 편집·테스트·PR 생성(Artifact: `diff`,`pr`)
5. **EvaluatorAgent**: docstring coverage, MI, 테스트, 정적/보안 스캔 집계(Artifact: `metrics.report`)
6. **Gate**: Policy 충족 시 **merge** or **retry/fix loop**
7. (옵션 B) 각 단계 결과를 Event로 게시 → 구독 에이전트가 후속 처리
8. (옵션 C) 특정 단계(Event)를 외부 A2A 에이전트에 위임(권한/가시성 정책 포함)

---

# 4) 관측·신뢰·보안(간단하지만 강한 기본값)

* **Idempotency & 재시도:** `task_id`를 모든 호출/저장에 포함, **at‑least‑once** 처리 가정 + **de‑dup**
* **트레이싱 키:** `trace_id`, `goal_id`, `plan_id`, `pr_id`를 로그 전 구간에 전파
* **게이트 순서:**

  1. 정적/보안(CodeQL/Semgrep/OSV)
  2. 테스트(단위+속성+뮤테이션‑스모크)
  3. 품질(docstring≥80, MI≥65)
  4. SWE‑bench 샘플(선택)
* **권한 최소화:** MCP `write_scope` 화이트리스트, `require_pr=true`, 위험 커맨드 차단
* **격리 실행:** 샌드박스 컨테이너(선택: Firecracker microVM)에서만 테스트/빌드 수행
* **비밀/신원:** AgentCore Identity(IAM/OIDC)로 솔브, 깃 액션은 OIDC만 허용

---

# 5) 선택지별 구성 스케치

## A안(DAG) 라우팅 의사코드

```yaml
routes:
  - when: intent == "research"  -> research
  - when: intent == "plan"      -> planner
  - when: intent in ["code","refactor"] -> codegen
  - when: intent == "evaluate"  -> evaluator
```

## B안(Blackboard) 이벤트 규칙 예시

```yaml
subscriptions:
  - agent: codegen
    on: ["plan.ready"]        # Planner 결과 이벤트
    filter: { repo: "^tdev/" }
  - agent: evaluator
    on: ["pr.opened","tests.done","scan.done"]
```

## C안(A2A) 위임 정책 예시

```yaml
a2a_policies:
  allow:
    - "PerfTuner.profile"   # 외부 성능튜너
    - "SecScanner.review"   # 외부 보안검사
  redaction:
    - paths: ["secrets/*","internal/*"]
```

---

# 6) **10일 검증 로드맵**(불확실성 줄이는 데 초점)

* **D1–D2**: 옵션 A 스켈레톤 가동 (Research→Plan→Code→Evaluate, PR 열고 게이트 통과)
* **D3–D4**: MCP 서버 3종(fs/git/github) + 샌드박스 실행, **정적/테스트 게이트** 온
* **D5–D6**: 이벤트 버스(내부) 도입, Planner 결과를 **plan.ready**로 게시 → Codegen 구독 (옵션 B 맛보기)
* **D7–D8**: 외부 A2A(PerfTuner or SecScanner) PoC 한 개 위임 (옵션 C 맛보기)
* **D9–D10**: 관측 대시보드(Goal→PR→Gate 지표) + 회귀 테스트 스위트 구성, 실패/재시도 전략 튜닝

**승인 기준(Exit):**

* 합성 목표 2종(예: docstring 80% & 타입힌트)에서 **PR 자동 생성** + **게이트 통과** + **머지 승인 준비**
* 1개의 이벤트 기반 흐름(plan.ready)과 1개의 A2A 위임을 성공

---

# 7) 지금 당장 쓸 **기본값**(의사결정 확정)

* **주 구조:** 옵션 **A (Supervisor‑DAG)** 로 시작
* **확장 포인트:** Planner 결과를 이벤트로도 발행(옵션 B 호환성 준비)
* **A2A:** 보안스캔만 1개 외부 위임(최소 권한)
* **게이트 기준:** docstring ≥ 80, MI ≥ 65, 테스트 통과, 보안 스캔 경고=차단
* **폴더 스코프:** `packages/agents/**`, `packages/runtime/**`만 초기 write 허용

---

원하면 이 결정을 **리포에 바로 커밋할 “architecture.md + rules.md” 초안**으로 만들어줄게.
또, 아까 만든 컴포넌트 트리와 이 옵션 A/B/C를 **하나의 와이어프레임 다이어그램(텍스트 & SVG)** 으로 같이 넣어줄 수도 있어.
