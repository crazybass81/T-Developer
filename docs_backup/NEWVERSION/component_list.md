좋아, “바로 붙여 넣고 시작”할 수 있게 **구체적 컴포넌트 목록**을 패키지/파일 단위로 정리했어. (Agno=에이전트 구현, AWS Agent Squad=오케스트레이션, Bedrock AgentCore=운영, Claude Code=코드생성, MCP=Agnostic 툴 허브, A2A=외부 에이전트 연동)

---

# 0) 리포 구조(모노레포)

```
t-developer/
├─ README.md
├─ .env.example
├─ pyproject.toml                # 공통 툴(black/ruff/radon/interrogate/pytest)
├─ requirements.txt              # 러너 전용
├─ packages/
│  ├─ agents/                    # Agno 기반 에이전트
│  │  ├─ __init__.py
│  │  ├─ base.py
│  │  ├─ research_agent.py
│  │  ├─ planner_agent.py
│  │  ├─ evaluator_agent.py
│  │  └─ codegen_agent_claude/   # Claude Code 어댑터
│  │     ├─ __init__.py
│  │     └─ runner.py
│  ├─ orchestrator/              # AWS Agent Squad 연동
│  │  ├─ __init__.py
│  │  ├─ squad_config.yaml
│  │  ├─ router_rules.yaml
│  │  └─ entrypoint.py
│  ├─ runtime/                   # Bedrock AgentCore 연동 래퍼
│  │  ├─ __init__.py
│  │  ├─ agentcore_gateway.py
│  │  ├─ agentcore_identity.py
│  │  ├─ agentcore_observability.py
│  │  └─ deploy/
│  │     ├─ cdk/                 # 또는 terraform/choice
│  │     │  ├─ app.py
│  │     │  └─ stacks.py
│  │     └─ config/
│  │        └─ env.prod.yaml
│  ├─ mcp/                       # MCP 서버/클라이언트 설정
│  │  ├─ servers/
│  │  │  ├─ filesystem.server.json
│  │  │  ├─ git.server.json
│  │  │  ├─ github.server.json
│  │  │  ├─ browser.server.json
│  │  │  └─ tracker.server.json  # Jira/Linear 등
│  │  └─ clients/
│  │     ├─ claude.mcp.json
│  │     └─ vscode.mcp.json
│  ├─ a2a/                       # A2A 에이전트 카드/브로커
│  │  ├─ agent_cards/
│  │  │  ├─ perf-tuner.card.json
│  │  │  └─ sec-review.card.json
│  │  └─ broker_config.yaml
│  ├─ sandbox/                   # 안전 실행 러너
│  │  ├─ Dockerfile
│  │  ├─ run_in_sandbox.sh
│  │  └─ ignite/                 # (옵션) Firecracker(ignite) 사용 시
│  │     └─ vm.yaml
│  └─ evaluation/                # 품질/보안/테스트 파이프라인
│     ├─ codeql/
│     │  └─ codeql-config.yml
│     ├─ semgrep/
│     │  └─ semgrep.yml
│     ├─ pytest.ini
│     ├─ interrogate.toml
│     ├─ radon.toml
│     ├─ mutation/
│     │  └─ cosmic-ray.toml
│     └─ swe-bench/
│        └─ suite.yaml
├─ .github/
│  └─ workflows/
│     ├─ ci.yml                 # 린트/테스트/커버리지/게이트
│     ├─ codeql.yml
│     └─ semgrep.yml
└─ scripts/
   ├─ bootstrap.sh               # 로컬 초기화
   ├─ run_self_evolution.py      # E2E 오케스트레이션 트리거
   └─ make_pr_summary.py
```

---

# 1) 에이전트(Agno) 스켈레톤

`packages/agents/base.py`

```python
from typing import Any, Dict, Optional, List, TypedDict

class TaskSpec(TypedDict, total=False):
    goal: str
    success_criteria: Dict[str, Any]
    max_cycles: int
    repo_ref: str
    branch: str
    constraints: Dict[str, Any]

class Artifact(TypedDict, total=False):
    path: str
    diff: str
    metrics: Dict[str, Any]
    report: str

class AgnoAgent:
    name: str = "AgnoAgent"
    def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError
```

`packages/agents/research_agent.py`

```python
from .base import AgnoAgent, TaskSpec
from typing import Dict, Any

class ResearchAgent(AgnoAgent):
    name="ResearchAgent"
    def run(self, task: TaskSpec) -> Dict[str, Any]:
        # (예) MCP Gateway 통해 repo/issue/kb 스캔 → 개선 후보/리스크/벤치마크 수집
        return {"insights": {"docstring_missing": 37, "typehints_missing": 21}}
```

`packages/agents/planner_agent.py`

```python
from .base import AgnoAgent
from typing import Dict, Any, List

class PlannerAgent(AgnoAgent):
    name="PlannerAgent"
    def run(self, insights: Dict[str, Any]) -> Dict[str, Any]:
        # 4시간 단위 태스크 DAG 생성
        dag = [
          {"id":"T1","title":"Add docstrings in pkg A","est_hours":4,"deps":[]},
          {"id":"T2","title":"Add type hints in pkg A","est_hours":4,"deps":["T1"]},
        ]
        return {"plan_dag": dag}
```

`packages/agents/evaluator_agent.py`

```python
from .base import AgnoAgent
from typing import Dict, Any

class EvaluatorAgent(AgnoAgent):
    name="EvaluatorAgent"
    def run(self, artifact: Dict[str, Any]) -> Dict[str, Any]:
        # radon/interrogate 결과 수집해 성공여부 판단
        metrics = artifact.get("metrics", {})
        success = metrics.get("docstring_coverage",0) >= 80 and metrics.get("mi_score",60) >= 65
        return {"success": success, "metrics": metrics}
```

---

# 2) Claude Code “코드생성/수정 에이전트” 어댑터

`packages/agents/codegen_agent_claude/runner.py`

```python
import subprocess, json, os
from typing import Dict, Any
from ..base import AgnoAgent, TaskSpec, Artifact

CLAUDE_BIN = os.getenv("CLAUDE_BIN","claude")  # CLI 또는 SDK 래퍼

class CodegenClaudeAgent(AgnoAgent):
    name="CodegenClaudeAgent"

    def run(self, task: TaskSpec) -> Artifact:
        """
        task['goal']: 예) "docstring coverage >= 85% in package X"
        MCP는 claude 설정 파일(../mcp/clients/claude.mcp.json)로 등록되어 있다고 가정.
        """
        cmd = [
            CLAUDE_BIN,
            "--workspace", task.get("repo_ref","/workspace"),
            "--task", task.get("goal","Improve code"),
            "--branch", task.get("branch","tdev/auto"),
            "--mcp-config", "packages/mcp/clients/claude.mcp.json",
            "--create-pr"
        ]
        out = subprocess.run(cmd, capture_output=True, text=True, check=False)
        # 표준화된 결과 파싱(디프/메트릭은 후속 스텝에서 수집)
        return {"report": out.stdout}
```

> **참고**: 실제 환경에서는 CLI 대신 SDK 호출 + 세분화된 MCP 툴 호출(파일 편집/테스트/린트)을 권장.

---

# 3) AWS Agent Squad 오케스트레이션 설정

`packages/orchestrator/squad_config.yaml`

```yaml
supervisor:
  name: evolution-supervisor
  memory_backend: agentcore   # AgentCore Memory/Store 사용 가정
agents:
  - id: research
    impl: packages.agents.research_agent.ResearchAgent
  - id: planner
    impl: packages.agents.planner_agent.PlannerAgent
  - id: codegen
    impl: packages.agents.codegen_agent_claude.runner.CodegenClaudeAgent
  - id: evaluator
    impl: packages.agents.evaluator_agent.EvaluatorAgent
context:
  tools:
    - type: mcp
      client_config: packages/mcp/clients/claude.mcp.json
    - type: gateway
      name: agentcore
      resources:
        - github
        - kb
        - secrets
routing:
  strategy: rules
  rules_file: packages/orchestrator/router_rules.yaml
```

`packages/orchestrator/router_rules.yaml`

```yaml
- when: "input.intent == 'research'"
  to: "research"
- when: "input.intent == 'plan'"
  to: "planner"
- when: "input.intent in ['code','refactor']"
  to: "codegen"
- when: "input.intent == 'evaluate'"
  to: "evaluator"
- default: "research"
```

`packages/orchestrator/entrypoint.py`

```python
import os, json
# 가정: squad SDK 제공. 없으면 내부 라우터로 대체.
from squad import Supervisor

def handle(goal: str):
    spv = Supervisor.from_yaml("packages/orchestrator/squad_config.yaml")
    insights = spv.dispatch({"intent":"research","goal":goal})
    plan     = spv.dispatch({"intent":"plan","insights":insights})
    patch    = spv.dispatch({"intent":"code","plan":plan,"goal":goal})
    report   = spv.dispatch({"intent":"evaluate","artifact":patch})
    return report

if __name__ == "__main__":
    goal = os.getenv("GOAL","Increase docstring coverage to 85% for package tdev.core")
    result = handle(goal)
    print(json.dumps(result, indent=2, ensure_ascii=False))
```

---

# 4) Bedrock AgentCore 연동 래퍼

`packages/runtime/agentcore_gateway.py`

```python
from typing import Dict, Any

class AgentCoreGateway:
    def __init__(self, profile: str = "default"):
        # AgentCore SDK 클라이언트 초기화(아이덴티티/권한/리소스)
        ...

    def tool(self, name: str):
        # "github", "kb", "secrets" 등의 리소스 핸들 획득
        ...

    def call(self, tool: str, action: str, **kwargs) -> Dict[str,Any]:
        # 예: call("github","create_pr", base="main", head="tdev/auto", title="...")
        ...
```

`packages/runtime/agentcore_identity.py`

```python
class AgentCoreIdentity:
    def whoami(self) -> str:
        # IAM Role/Session/Policy 컨텍스트 조회
        ...
```

`packages/runtime/agentcore_observability.py`

```python
class AgentCoreObservability:
    def log_event(self, name: str, payload: dict):
        # Agent/Task/Plan/PR/Metric 로그/트레이스 전송
        ...
```

> **배포**는 CDK/TF 중 택1. 아래는 CDK 예시 골격.

`packages/runtime/deploy/cdk/app.py`

```python
from aws_cdk import App
from stacks import TDevStack

app = App()
TDevStack(app, "TDeveloperAgentCoreStack", env={'region':'ap-northeast-2'})
app.synth()
```

`packages/runtime/deploy/cdk/stacks.py`

```python
from aws_cdk import Stack
from constructs import Construct

class TDevStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)
        # AgentCore Runtime/Gateway/Memory/Obs 관련 리소스 바인딩
        # GitHub OIDC/Secrets, VPC, Logs 등
        ...
```

---

# 5) MCP 서버/클라이언트 설정

`packages/mcp/servers/filesystem.server.json`

```json
{
  "name": "fs",
  "type": "filesystem",
  "root": "/workspace",
  "allow": ["packages/*", "scripts/*"],
  "deny": ["**/.git/**", "**/node_modules/**"]
}
```

`packages/mcp/servers/git.server.json`

```json
{
  "name": "git",
  "type": "git",
  "repo_path": "/workspace",
  "allow_commands": ["status","diff","checkout","switch","apply","commit","push","pull"],
  "branch_whitelist": ["tdev/*","feature/*"]
}
```

`packages/mcp/servers/github.server.json`

```json
{
  "name": "github",
  "type": "github",
  "org": "your-org",
  "repo": "t-developer",
  "features": ["create_pr","comment_pr","label_pr","get_checks"]
}
```

`packages/mcp/servers/browser.server.json`

```json
{
  "name": "browser",
  "type": "browser",
  "allowed_hosts": ["docs.yourcorp.com","pypi.org","python.org"]
}
```

`packages/mcp/servers/tracker.server.json`

```json
{
  "name": "tracker",
  "type": "jira",
  "project_key": "TDEV",
  "actions": ["create_issue","transition","comment","link_pr"]
}
```

`packages/mcp/clients/claude.mcp.json`

```json
{
  "client": "claude",
  "servers": [
    {"$ref":"../servers/filesystem.server.json"},
    {"$ref":"../servers/git.server.json"},
    {"$ref":"../servers/github.server.json"},
    {"$ref":"../servers/browser.server.json"},
    {"$ref":"../servers/tracker.server.json"}
  ],
  "policy": {
    "confirm_on_write": true,
    "max_write_paths": 50
  }
}
```

---

# 6) A2A 연동(에이전트 카드 & 브로커)

`packages/a2a/agent_cards/perf-tuner.card.json`

```json
{
  "name": "PerfTuner",
  "capabilities": ["profile","optimize"],
  "inputs": {"repo":"string","commit":"string","targets":"string[]"},
  "auth": {"type":"oauth2","scopes":["repo:read"]},
  "callback": {"type":"webhook","url":"https://perf.example.com/a2a/callback"}
}
```

`packages/a2a/broker_config.yaml`

```yaml
broker:
  discovery:
    catalogs:
      - https://agents.example.com/catalog.json
  auth:
    mode: "federated"
  policies:
    allow:
      - "PerfTuner.profile"
      - "SecurityScanner.review"
```

---

# 7) 샌드박스 실행 환경

`packages/sandbox/Dockerfile`

```dockerfile
FROM python:3.11-slim
RUN apt-get update && apt-get install -y git curl build-essential
WORKDIR /workspace
COPY . /workspace
RUN pip install -r requirements.txt
# 보안 경량화
RUN useradd -m agent && chown -R agent:agent /workspace
USER agent
```

`packages/sandbox/run_in_sandbox.sh`

```bash
#!/usr/bin/env bash
set -euo pipefail
docker build -t tdev-sandbox:latest packages/sandbox
docker run --rm \
  --security-opt no-new-privileges \
  --pids-limit=512 --memory=3g --cpus=2 \
  -v "$(pwd)":/workspace \
  tdev-sandbox:latest bash -lc "$*"
```

(옵션) Firecracker(ignite) VM 스펙
`packages/sandbox/ignite/vm.yaml`

```yaml
name: tdev-vm
cpus: 2
memory: 4096MB
kernel: default
image: weaveworks/ignite-ubuntu:latest
ssh: true
mounts:
  - hostPath: .
    vmPath: /workspace
```

---

# 8) 평가/보안/테스트 파이프라인

`packages/evaluation/interrogate.toml`

```toml
ignore-init-method = true
ignore-private = true
fail-under = 80
```

`packages/evaluation/radon.toml`

```toml
[mi]
threshold = 65
cc_threshold = "B"   # CC 등급 기준
```

`packages/evaluation/mutation/cosmic-ray.toml`

```toml
[cosmic-ray]
modules = ["packages/"]
test-command = "pytest -q"
timeout = 30
```

`packages/evaluation/codeql/codeql-config.yml`

```yaml
name: "T-Developer CodeQL"
queries: ["security-and-quality"]
paths: ["packages/"]
```

`packages/evaluation/semgrep/semgrep.yml`

```yaml
rules:
  - id: no-secrets
    patterns:
      - pattern: $X=$SECRET
    message: "Possible secret"
    severity: ERROR
    languages: [python]
```

---

# 9) GitHub Actions (CI) — **게이트 통합**

`.github/workflows/ci.yml`

```yaml
name: ci
on:
  pull_request:
  push:
    branches: [ main, "tdev/**" ]
jobs:
  build-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - run: pip install -r requirements.txt
      - name: Lint
        run: |
          ruff check .
          black --check .
      - name: Unit & Property Tests
        run: |
          pytest -q --maxfail=1
      - name: Docstring Coverage
        run: |
          interrogate -c packages/evaluation/interrogate.toml packages/ --fail-under 80
      - name: Complexity (radon)
        run: |
          radon cc -s -n B packages/ && radon mi -s packages/ | awk '{ if ($3+0 < 65) { print "MI under 65"; exit 1 } }'
      - name: Mutation (smoke)
        run: |
          echo "skip-long-run or run nightly with matrix"
```

`.github/workflows/codeql.yml`

```yaml
name: codeql
on:
  pull_request:
  schedule: [ { cron: "0 2 * * 1" } ]
jobs:
  analyze:
    uses: github/codeql-action/.github/workflows/codeql.yml@v3
    with:
      config-file: packages/evaluation/codeql/codeql-config.yml
```

`.github/workflows/semgrep.yml`

```yaml
name: semgrep
on:
  pull_request:
  schedule: [ { cron: "0 3 * * 1" } ]
jobs:
  semgrep:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: returntocorp/semgrep-action@v1
        with:
          config: packages/evaluation/semgrep/semgrep.yml
```

---

# 10) “자가 진화” 워크플로 트리거

`scripts/run_self_evolution.py`

```python
import json, subprocess, os, sys
from packages.orchestrator.entrypoint import handle

goal = os.environ.get("GOAL", "Raise docstring coverage to 85% for packages/agents")
result = handle(goal)

print("=== Evolution Result ===")
print(json.dumps(result, ensure_ascii=False, indent=2))

# 실패 시 PR 막기(옵션)
if not result.get("success", False):
    print("Gate failed.", file=sys.stderr)
    sys.exit(1)
```

---

# 11) 로컬 부트스트랩

`scripts/bootstrap.sh`

```bash
#!/usr/bin/env bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
pre-commit install || true
echo "Ready. Try: python scripts/run_self_evolution.py"
```

---

# 12) 요구사항 연결 요약

* **에이전트 생성**: Agno 베이스(패키지/agents/\*)
* **오케스트레이터**: AWS **Agent Squad** 구성 파일(squad\_config.yaml + router\_rules.yaml)
* **운영**: Bedrock **AgentCore** 래퍼 및 배포 골격(packages/runtime/\* + CDK)
* **Claude Code**: 전담 CodegenAgent(패키지/agents/codegen\_agent\_claude) + MCP 클라이언트 설정
* **MCP**: 파일/깃/깃허브/브라우저/트래커 서버 JSON
* **A2A**: agent\_cards + broker\_config
* **평가/보안**: interrogate/radon/pytest/CodeQL/Semgrep/뮤테이션 + CI 게이트
* **샌드박스**: Docker 샌드박스(옵션: Firecracker)

---

필요하면 위 구조에서 **빈칸(…)** 부분을 당신 환경(AWS 계정, GitHub OIDC, Jira 프로젝트 등)에 맞춘 실코드로 바로 채워줄게.
