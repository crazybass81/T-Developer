짧게: **네.** 우리가 잡은 설계는 “핵심 에이전트가 기본적으로 AI-first로 동작”하도록 짜여 있어요. 다만 **Evaluator(평가) 축**은 지금도 지표 기반으로 충분하지만, 원하시면 LLM 보조 판단을 더 켜서 “스스로 고치기 위한 피드백 품질”을 한 단계 올릴 수 있습니다.

아래에 **필수 에이전트별로 AI가 어디서, 어떻게, 무엇을** 하는지와, **더 적극적으로 켜면 좋은 옵션**을 표시했어요.

---

## 필수 에이전트별 AI 활용도

| 에이전트                           | AI가 하는 일(핵심)                               | 쓰는 도구/패턴                                           | 산출물                |
| ------------------------------ | ------------------------------------------ | -------------------------------------------------- | ------------------ |
| **ResearchAgent**              | 요구/리포/이슈/문서 스캔 → 개선 후보 군집화·우선순위화           | LLM+RAG, MCP(browser/issue/github), 기준 프롬프트+스키마 출력 | `insights.json`    |
| **PlannerAgent**               | HTN 스타일 태스크 분해(4h 단위), DAG/리스크/의존성 계산, 재계획 | LLM 계획·자기비판(Self-critique), 플래너 룰린트                | `plan_dag.json`    |
| **CodegenAgent (Claude Code)** | 코드 생성/리팩토링, 테스트 실행, 실패 시 자체 수정 루프, PR 생성   | LLM 코드 모델, MCP(fs/git/github/runner), Test-fix 루프  | `diff.patch`, PR   |
| **EvaluatorAgent**             | 지표 수집·판정(문턱 통과/차단), 회귀 원인 요약(옵션)           | (기본) 도구 계산, (옵션) LLM로 원인 분류·수정 힌트                  | `eval_report.json` |

### “서비스 생성” 단계 필수(확장) 에이전트

* **SpecAgent**: 자연어 요구 → SRS/OpenAPI/수용기준 (LLM 초안 + 규칙 검증)
* **BlueprintAgent**: 청사진 선택/템플릿 변수 치환(언어/DB/버스/인증) (LLM 선택·설명)
* **InfraAgent**: IaC(CDK/Terraform) 스캐폴드 제안/생성(LLM 초안 → 도구 검증)
* **ContractTestAgent**: OpenAPI → 계약 테스트/목 서버 생성(LLM 테스트 초안 + 러너)

> 위 8개가 \*\*AI가 ‘직접 판단/생성/수정’\*\*에 관여하는 필수 축입니다. CI·보안 게이트/권한은 **비-AI(결정론)** 으로 안전망을 형성합니다.

---

## 더 “공격적으로” 켤 수 있는 AI 옵션 (권장 스위치)

1. **Evaluator LLM-Assist ON**

   * 역할: 실패 원인 분류(테스트 설계/타입힌트/복잡도/보안), “다음 라운드 수정 브리프” 자동 작성
   * 안전: **최종 합/불합격은 지표 게이트**(테스트·보안·품질)가 결정

2. **Planner Self-Critique Loop**

   * 1차 계획→자체 리뷰→수정안 반영(최대 N라운드), 데드라인·예산 룰 자동 점검

3. **Codegen Test-Fix Loop 강화**

   * 테스트 실패 로그 요약→패치 제안→재실행(라운드 제한 2\~3)
   * 위험 커맨드/쓰기 스코프는 MCP 정책으로 계속 차단

4. **Memory-Curator 힌트 주입**

   * 과거 성공 패턴을 Planner/Codegen 프롬프트에 자동 삽입(유사 이슈 라운드 수↓)

---

## 설정 예(요지) — “AI 적극 사용” 토글

```yaml
agents:
  research:
    llm: bedrock.anthropic.claude-3-7
    tools: [mcp.browser, mcp.github, agentcore.kb]
    output_schema: insights_v1
  planner:
    llm: bedrock.anthropic.claude-3-7
    strategy: htn
    self_critique: {enabled: true, max_rounds: 2}
    guards: [no_cycle, time_budget, risk_annotation]
  codegen:
    llm: claude-code
    tools: [mcp.fs, mcp.git, mcp.github, mcp.runner]
    test_fix_loop: {enabled: true, max_rounds: 3}
    write_scope: ["packages/**","scripts/**"]
  evaluator:
    gates: [tests, semgrep, codeql, docstring>=80, mi>=65]
    llm_assist: {enabled: true, role: "root-cause+fix-brief"}
```

---

## 결론 (현 상태 진단)

* **Yes** — 현재 설계는 필수 에이전트를 **AI-first**로 두고, MCP/AgentCore/게이트로 **안전하게 실행**하도록 잡혀 있습니다.
* 실전에서 **AI 활용도를 더 끌어올리고 싶은 부분**은 주로 **Evaluator/Planner/Codegen 루프 강화**이며, 위 스위치를 켜면 **“스스로 고치기” 속도와 품질**이 올라갑니다.
* 원하시면 지금 리포 구조에 맞춘 **프롬프트·스키마·정책 파일(위 YAML)** 을 바로 채워서 드릴게요.
