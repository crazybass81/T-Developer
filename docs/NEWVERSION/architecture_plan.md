좋은 질문! 멀티 에이전트로 “스스로 진화하는 개발 시스템”을 더 단단히 만드는 최신 스택/패턴을 아래처럼 제안해요. (당신이 선호한 스택: **Agno(에이전트 생성)** + **AWS Agent Squad(오케스트레이션)** + \*\*Bedrock AgentCore(운영 런타임)\*\*는 그대로 살리고, Claude Code, MCP, A2A까지 얹습니다.)

# 제안 아키텍처(요약)

* **에이전트 레이어(Agno)**: Research / Planner / Coder(Claude Code) / Reviewer / Security / Test-Gen / Evaluator / Memory-Curator
* **오케스트레이션(AWS Agent Squad)**: SupervisorAgent가 멤버 에이전트를 “툴”처럼 호출·병렬화·핸드오프(=agent-as-tools 패턴). ([AWS Labs][1], [GitHub][2])
* **런타임(Bedrock AgentCore)**: 서버리스·보안형 에이전트 런타임 + 메모리 리소스 관리(버전/에일리어스 배포 연계). ([Amazon Web Services, Inc.][3], [Boto3][4], [AWS Documentation][5])
* **툴/데이터 플레인(MCP)**: 코드베이스·이슈트래커·리포지토리·보안스캐너 등을 MCP 서버로 표준화 연결(Claude Code와 바로 연동). ([Anthropic][6], [모델 컨텍스트 프로토콜][7])
* **에이전트 연합(A2A)**: 팀/조직 경계를 넘는 외부 에이전트와 상호작용(검색/구매/보안/빌드 등) — 표준 **A2A**로 상호 운용. ([linuxfoundation.org][8], [Google Developers Blog][9], [Microsoft][10])
* **평가/가드레일**: SWE-bench(Verified/Lite/Live) + 정적분석(CodeQL/Semgrep) + 테스트(단위/속성/뮤테이션)로 “개선 게이트” 구성. ([OpenAI][11], [swebench.com][12], [swe-bench-live.github.io][13], [codeql.github.com][14], [semgrep.dev][15], [cosmic-ray.readthedocs.io][16])
* **샌드박스 실행환경**: 코드 수정/빌드/테스트는 ACI(Agent-Computer Interface) 스타일 + Firecracker microVM으로 안전 실행. ([arXiv][17], [firecracker-microvm.github.io][18])

---

## 왜 이 구성이 “더 좋은가”

1. **오케스트레이션의 안정성** – Squad의 SupervisorAgent가 팀원 에이전트를 “툴”로 노출 → 병렬 작업·컨텍스트 공유가 깔끔, 스케일도 쉬움. ([AWS Labs][1])
2. **운영 단순화** – Bedrock AgentCore로 배포/버저닝/메모리 리소스 관리/오토스케일이 표준화. ([Amazon Web Services, Inc.][3], [Boto3][4])
3. **도구 연결 표준화** – MCP로 깔끔하게 GitHub/Issue/VectorDB/사내 API를 붙이고, Claude Code가 MCP를 그대로 사용. ([Anthropic][6])
4. **조직 간 협업 확장성** – A2A로 외부 에이전트(예: 보안 분석, 데이터 카탈로그, 배포 승인 에이전트)와 안전한 상호작용. ([linuxfoundation.org][8], [Google Developers Blog][19])
5. **신뢰 가능한 평가** – SWE-bench(Verified/Live) + 정적분석(CodeQL/Semgrep) + 테스트 생성(Pynguin) + 뮤테이션(Cosmic Ray)로 “정량 게이트”를 통과한 변경만 채택. ([OpenAI][11], [swe-bench-live.github.io][13], [GitHub Docs][20], [pynguin.readthedocs.io][21], [cosmic-ray.readthedocs.io][16])
6. **안전 실행** – ACI 연구와 실전형 OpenHands 아이디어를 가져오고, Firecracker로 빠르고 격리된 CI 런을 확보. ([arXiv][17], [GitHub][22], [firecracker-microvm.github.io][18])

---

## 에이전트 역할(추천)

* **ResearchAgent (Agno)**: 레포/이슈/릴리즈 노트/벤치마크 수집(MCP 툴).
* **PlannerAgent (Agno)**: HTN 스타일로 태스크 그래프 작성 → Squad Supervisor에 작업 큐 전달.
* **CoderAgent = Claude Code**: 코드 생성/수정/리팩토링(MCP로 로컬 툴·리포 접근, CLI/SDK 지원). ([Anthropic][23])
* **ReviewerAgent**: 스타일/품질/리스크 리뷰(Ruff/Black/타 언어 린터).
* **SecurityAgent**: CodeQL/Semgrep/OSV 스캔·리포팅. ([GitHub Docs][20], [semgrep.dev][15], [osv.dev][24])
* **TestGenAgent**: Pynguin(파이썬)·Diffblue(Java)로 테스트 자동 생성 + Hypothesis(속성 기반) 템플릿. ([pynguin.readthedocs.io][21], [diffblue.com][25], [hypothesis.readthedocs.io][26])
* **EvaluatorAgent**: Radon(복잡도/MI), docstring coverage(interrogate), SWE-bench 게이트. ([radon.readthedocs.io][27], [interrogate.readthedocs.io][28], [swebench.com][29])
* **Memory-Curator**: 변경 요약·패턴·회고를 Bedrock AgentCore 메모리에 축적. ([Boto3][4])

---

## 핵심 설계 패턴 6가지

1. **Agent-as-Tools + 그래프형 핸드오프**: Squad Supervisor + (필요 시) LangGraph로 세밀한 단계 제어(루프/중단/오류 분기). ([AWS Labs][1], [LangChain AI][30])
2. **MCP “도구 허브”**: 리포/이슈/빌드/테스트/스캔/배포를 MCP 서버로 노출 → Claude Code가 즉시 사용. ([모델 컨텍스트 프로토콜][7], [Anthropic][31])
3. **A2A “에이전트 허브”**: 내부 팀 외에 외부 에이전트와 안전 통신(Agent Card로 발견/권한 협상). ([linuxfoundation.org][8], [Stride][32])
4. **ACI + 마이크로VM 샌드박스**: 코드 수정/실행/테스트는 격리 환경에서만. ([arXiv][17], [firecracker-microvm.github.io][18])
5. **다중 게이트**: (a) 정적분석 통과 → (b) 단위+속성+뮤테이션 테스트 통과 → (c) SWE-bench/Lite 샘플 통과 시 머지. ([semgrep.dev][15], [hypothesis.readthedocs.io][26], [cosmic-ray.readthedocs.io][16], [swebench.com][12])
6. **그래프형 RAG(옵션)**: 대규모 내부 문서/설계 지식엔 GraphRAG로 질의 품질 향상. ([microsoft.github.io][33], [Microsoft][34])

---

## 실행 로드맵(간단)

* **Phase A – 골격 세팅**: Agno 에이전트 정의 → Squad Supervisor 파이프라인 구성 → AgentCore에 배포/버전-에일리어스. ([GitHub][2], [AWS Labs][1], [AWS Documentation][5])
* **Phase B – 툴/샌드박스**: MCP 서버(Repo/CI/테스트/스캐너) + Firecracker 샌드박스 런너. ([모델 컨텍스트 프로토콜][7], [firecracker-microvm.github.io][18])
* **Phase C – 평가 게이트**: CodeQL/Semgrep/OSV + Pynguin/Hypothesis/Cosmic Ray + Radon/interrogate + SWE-bench 샘플. ([GitHub Docs][20], [semgrep.dev][15], [osv.dev][24], [pynguin.readthedocs.io][21], [hypothesis.readthedocs.io][26], [cosmic-ray.readthedocs.io][16], [radon.readthedocs.io][27], [interrogate.readthedocs.io][28], [swebench.com][29])
* **Phase D – 연합/확장**: 필요한 외부 에이전트(A2A)와 연동(예: 비용 승인/보안 예외 심사 에이전트). ([linuxfoundation.org][8])

---

## Claude Code를 “코드 작성 에이전트”로 쓰는 베스트 프랙티스

* **비대화식 모드/SDK**로 워크플로우에 내장(태스크 입력→패치 산출), MCP로 리포/테스트 러너/코드검색 도구 접근. ([Anthropic][35])
* **리뷰 루프**: ReviewerAgent가 패치·테스트 결과를 요약 피드백 → Claude Code가 수정 라운드.
* **안전장치**: 파일/디렉터리 스코프 제한, 위험 커맨드 차단, 샌드박스 외부 쓰기 불가.

---

## 선택적 보너스

* **OpenHands 스타일 자동화**(터미널/브라우저/편집기 툴체인)로 더 넓은 작업 범위 지원. ([GitHub][22])
* **SWE-bench Live로 회귀 테스트**(실시간 이슈로 오버피팅 방지). ([swe-bench-live.github.io][13])
* **LangGraph 세부 오케스트레이션**(서브플로우에만 적용해 복잡도 최소화). ([LangChain AI][30])

---

원하시면, 이 설계를 바로 적용한 \*\*구체적 컴포넌트 목록(리포 구조, Agno/Squad 설정 템플릿, MCP 서버 스키마, AgentCore 배포 스크립트, 평가 파이프라인 YAML)\*\*까지 바로 드릴게요.

[1]: https://awslabs.github.io/agent-squad/agents/built-in/supervisor-agent/?utm_source=chatgpt.com "Supervisor Agent | Agent Squad"
[2]: https://github.com/awslabs/agent-squad?utm_source=chatgpt.com "awslabs/agent-squad: Flexible and powerful framework for ..."
[3]: https://aws.amazon.com/bedrock/agentcore/?utm_source=chatgpt.com "Amazon Bedrock AgentCore (Preview) - AWS"
[4]: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agentcore-control.html?utm_source=chatgpt.com "BedrockAgentCoreControlPlane..."
[5]: https://docs.aws.amazon.com/bedrock/latest/userguide/deploy-agent.html?utm_source=chatgpt.com "Deploy an agent - Amazon Bedrock"
[6]: https://docs.anthropic.com/en/docs/mcp?utm_source=chatgpt.com "Model Context Protocol (MCP)"
[7]: https://modelcontextprotocol.io/docs/concepts/tools?utm_source=chatgpt.com "Tools"
[8]: https://www.linuxfoundation.org/press/linux-foundation-launches-the-agent2agent-protocol-project-to-enable-secure-intelligent-communication-between-ai-agents?utm_source=chatgpt.com "Linux Foundation Launches the Agent2Agent Protocol ..."
[9]: https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/?utm_source=chatgpt.com "Announcing the Agent2Agent Protocol (A2A)"
[10]: https://www.microsoft.com/en-us/microsoft-cloud/blog/2025/05/07/empowering-multi-agent-apps-with-the-open-agent2agent-a2a-protocol/?utm_source=chatgpt.com "Empowering multi-agent apps with the open Agent2Agent ..."
[11]: https://openai.com/index/introducing-swe-bench-verified/?utm_source=chatgpt.com "Introducing SWE-bench Verified - OpenAI"
[12]: https://www.swebench.com/lite.html?utm_source=chatgpt.com "SWE-bench Lite"
[13]: https://swe-bench-live.github.io/?utm_source=chatgpt.com "SWE-bench-Live Leaderboard"
[14]: https://codeql.github.com/docs/?utm_source=chatgpt.com "CodeQL documentation - GitHub"
[15]: https://semgrep.dev/products/semgrep-code?utm_source=chatgpt.com "Semgrep Code | Scan Source-code with Static Application ..."
[16]: https://cosmic-ray.readthedocs.io/?utm_source=chatgpt.com "Cosmic Ray: mutation testing for Python - Read the Docs"
[17]: https://arxiv.org/abs/2405.15793?utm_source=chatgpt.com "SWE-agent - Computer Science > Software Engineering"
[18]: https://firecracker-microvm.github.io/?utm_source=chatgpt.com "Firecracker"
[19]: https://developers.googleblog.com/en/google-cloud-donates-a2a-to-linux-foundation/?utm_source=chatgpt.com "Google Cloud donates A2A to Linux Foundation"
[20]: https://docs.github.com/code-security/code-scanning/introduction-to-code-scanning/about-code-scanning-with-codeql?utm_source=chatgpt.com "About code scanning with CodeQL"
[21]: https://pynguin.readthedocs.io/?utm_source=chatgpt.com "Pynguin—PYthoN General UnIt test geNerator — pynguin 0.41.0.dev documentation"
[22]: https://github.com/All-Hands-AI/OpenHands?utm_source=chatgpt.com "All-Hands-AI/OpenHands: OpenHands: Code Less, Make More"
[23]: https://docs.anthropic.com/en/docs/claude-code/cli-reference?utm_source=chatgpt.com "CLI reference"
[24]: https://osv.dev/?utm_source=chatgpt.com "OSV - Open Source Vulnerabilities"
[25]: https://www.diffblue.com/diffblue-cover/?utm_source=chatgpt.com "Diffblue Cover"
[26]: https://hypothesis.readthedocs.io/?utm_source=chatgpt.com "Hypothesis 6.137.3 documentation"
[27]: https://radon.readthedocs.io/en/latest/?utm_source=chatgpt.com "Welcome to Radon's documentation! — Radon 4.1.0 ..."
[28]: https://interrogate.readthedocs.io/?utm_source=chatgpt.com "interrogate: explain yourself — Python docstring coverage (v1 ..."
[29]: https://www.swebench.com/?utm_source=chatgpt.com "SWE-bench Leaderboards"
[30]: https://langchain-ai.github.io/langgraph/concepts/multi_agent/?utm_source=chatgpt.com "LangGraph Multi-Agent Systems - Overview"
[31]: https://docs.anthropic.com/en/docs/claude-code/mcp?utm_source=chatgpt.com "Connect Claude Code to tools via MCP"
[32]: https://www.stride.build/blog/agent-to-agent-a2a-vs-model-context-protocol-mcp-when-to-use-which?utm_source=chatgpt.com "Agent-to-Agent (A2A) vs. Model Context Protocol (MCP)"
[33]: https://microsoft.github.io/graphrag/?utm_source=chatgpt.com "Welcome - GraphRAG"
[34]: https://www.microsoft.com/en-us/research/project/graphrag/?utm_source=chatgpt.com "Project GraphRAG - Microsoft Research"
[35]: https://docs.anthropic.com/en/docs/claude-code/sdk?utm_source=chatgpt.com "Claude Code SDK"
