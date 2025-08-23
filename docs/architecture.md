좋아 T! **전체 아키텍처**를 한눈에 볼 수 있게 머메이드로 3개 뷰를 준비했어.
(그대로 복붙해서 미리보기 하면 돼.)

# 1) 시스템 전체 아키텍처(컴포넌트 뷰)

```mermaid
flowchart LR
  %% Clients / Signals
  subgraph Clients["클라이언트 & 신호"]
    U["사용자/외부 시스템"]
    SIG["관측 신호"]
  end

  %% Orchestration Layer
  subgraph ORCH["오케스트레이션 레이어"]
    TS["Top Supervisor Orchestrator"]
    subgraph SUB["하위 오케스트레이터"]
      COrch["Create-Orch"]
      UOrch["Upgrade-Orch"]
      AOrch["Auto-Evolve-Orch"]
      QAOrch["QA-Orch"]
      SecOrch["Sec-Orch"]
      BuildOrch["Build/IaC-Orch"]
    end
  end

  %% Agent Layer
  subgraph AGENTS["에이전트 레이어"]
    Agno["Agno"]
    Claude["Claude Code"]
    DeDup["DeDup-Checker"]
    RK["RuleKeeper"]
    PE["PolicyEngine"]
    MC["Memory Curator"]
    OC["Observer-Collector"]
  end

  %% Runtime & Ops
  subgraph RUNTIME["런타임·운영"]
    BAC["Bedrock AgentCore"]
    Flags["Feature Flags"]
    Canary["Canary"]
  end

  %% Knowledge & Stores
  subgraph KNOW["지식·레지스트리"]
    Reg["Agent Registry"]
    Cat["Template Catalog"]
    Snip["Snippet DB"]
    ADR["ADR/ChangeLog"]
  end

  %% Memory Hub
  subgraph MEM["Memory Hub"]
    O["O-CTX"]
    A["A-CTX"]
    S["S-CTX"]
    Ux["U-CTX"]
    OBS["OBS-CTX"]
  end

  %% Flows
  U --> TS
  SIG --> AOrch
  TS --> COrch
  TS --> UOrch
  TS --> AOrch

  COrch -->|필요 정의| Agno
  UOrch -->|필요 정의| Agno
  AOrch -->|필요 정의| Agno
  Agno -->|생성 요청| Claude

  COrch --> QAOrch
  UOrch --> QAOrch
  AOrch --> QAOrch
  COrch --> SecOrch
  UOrch --> SecOrch
  AOrch --> SecOrch

  QAOrch --> BuildOrch
  SecOrch --> BuildOrch
  BuildOrch --> BAC
  BAC --> Flags
  BAC --> Canary

  %% Memory / Knowledge edges
  ORCH <-->|읽기/쓰기| MEM
  AGENTS <-->|읽기/쓰기| MEM
  AGENTS <-->|조회/재사용| KNOW
  MC --> MEM
  OC --> OBS
  RK -.감시.-> ORCH
  RK -.감시.-> AGENTS
  PE -.하드가드레일.-> ORCH
  DeDup -.유사도검사.-> KNOW
```

# 2) 메모리 & 가드레일(AGCORE-001, AIFIRST/De-dup/MH-Gate)

```mermaid
flowchart TD
  T["태스크/산출물"] --> G0["AIFIRST 체크"]
  G0 --> DD["DD-Gate 중복개발 금지"]
  DD --> MH["MH-Gate 메모리 위생"]
  MH --> PUT["메모리 쓰기"]
  PUT --> HUB{{"Memory Hub"}}
  subgraph HUB["Memory Hub"]
    O1["O-CTX"]
    A1["A-CTX"]
    S1["S-CTX"]
    U1["U-CTX"]
    B1["OBS-CTX"]
  end
  HUB --> GET["mem.get / RAG"]
  RK["RuleKeeper"] -."규칙 준수/수정 제안".-> G0
  RK -."규칙 준수/수정 제안".-> DD
  RK -."규칙 준수/수정 제안".-> MH
  PE["PolicyEngine"] -."필수항목/보안/정책 차단".-> G0
  PE -."필수항목/보안/정책 차단".-> DD
  PE -."필수항목/보안/정책 차단".-> MH
  Cur["Memory Curator"] -->|"요약/라벨/중복제거"| HUB
```

# 3) QA-Orchestrator 내부 병렬(팬아웃/팬인)

```mermaid
flowchart TD
  QA["QA-Orchestrator"] --> Lint["Lint"]
  QA --> Type["Type Check"]
  QA --> Lic["License Scan"]
  QA --> UT["Unit Tests"]
  QA --> IT["Integration"]
  QA --> E2E["E2E"]
  QA --> CT["Contract"]
  QA --> Compat["Compatibility"]
  QA --> Smoke["Perf Smoke"]
  Lint --> Join["Aggregate"]
  Type --> Join
  Lic --> Join
  UT --> Join
  IT --> Join
  E2E --> Join
  CT --> Join
  Compat --> Join
  Smoke --> Join
  Join --> Res{"Pass?"}
  Res -->|Yes| Up["상위 플로우 복귀"]
  Res -->|No| Fix["Claude Refactor"]
  Fix --> QA
```

원하면 세 문서(생성/업그레이드/자동진화) **부록 섹션**에 그대로 붙여넣을 수 있게 제목만 달아서 넣어둘게.
