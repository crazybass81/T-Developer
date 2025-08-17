# 🤖 Claude Code Integration Strategy

## 📌 개요

T-Developer v2는 코드 수정 작업을 위해 **Claude Code**를 핵심 엔진으로 사용합니다. Claude Code는 Anthropic의 코드 생성 및 수정 전용 모델로, MCP(Model Context Protocol)를 통해 파일시스템, Git, GitHub 등과 직접 상호작용할 수 있습니다.

## 🏗️ 아키텍처

### Claude Code의 위치

```
Evolution Engine
    ↓
RefactorAgent
    ↓
Claude Code Client (SDK/CLI)
    ↓
MCP Tools (filesystem, git, github)
    ↓
실제 코드 수정 & PR 생성
```

### SaaS 환경에서의 구성

```yaml
saas_configuration:
  execution:
    mode: "sandbox"  # 컨테이너/microVM에서 격리 실행
    runtime: "docker"
    resource_limits:
      cpu: "2 cores"
      memory: "4GB"
      timeout: "10 minutes"

  security:
    pr_only: true  # main 브랜치 직접 push 차단
    write_scope:  # 수정 가능 경로 제한
      - "src/"
      - "tests/"
      - "docs/"
    forbidden_patterns:  # 수정 금지 패턴
      - ".github/workflows/*"
      - "*.env"
      - "secrets/*"

  integration:
    github:
      method: "OIDC"  # GitHub OIDC로 권한 최소화
      permissions:
        - "pull_requests: write"
        - "contents: read"

  billing:
    model: "usage_based"
    tracking: "per_customer"
    limits:
      daily_quota: 1000  # API 호출 수
      max_file_size: "100KB"
```

## 🔧 구현 상세

### 1. Claude Code Client 래퍼

```python
# backend/packages/agents/claude_code_refactor.py
from typing import List, Dict, Any, Optional
from claude_code import ClaudeCodeClient
from mcp import MCPConfig
import asyncio
import logging

logger = logging.getLogger(__name__)

class ClaudeCodeRefactorAgent:
    """Claude Code를 사용한 코드 수정 Agent."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Claude Code 클라이언트 초기화.

        Args:
            config: MCP 및 보안 설정
        """
        self.config = config or self._default_config()
        self.client = ClaudeCodeClient(
            api_key=os.environ.get("ANTHROPIC_API_KEY"),
            mcp_config=MCPConfig(**self.config["mcp"]),
            sandbox=self.config.get("sandbox", True)
        )
        self.context_store = get_context_store()

    def _default_config(self) -> Dict[str, Any]:
        """기본 설정."""
        return {
            "mcp": {
                "tools": ["filesystem", "git", "github"],
                "write_scope": ["backend/", "frontend/src/", "tests/"],
                "pr_only": True,
                "sandbox": True
            },
            "safety": {
                "max_files_per_run": 50,
                "max_changes_per_file": 500,
                "require_tests": True,
                "auto_rollback": True
            },
            "github": {
                "create_pr": True,
                "pr_template": "claude_code_pr_template.md",
                "require_review": True,
                "auto_merge": False
            }
        }

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """코드 수정 작업 실행.

        Args:
            task: {
                "instructions": List[str],  # 수정 지시사항
                "target_path": str,          # 대상 경로
                "context": Dict[str, Any],   # 추가 컨텍스트
                "evolution_id": str          # Evolution ID
            }

        Returns:
            실행 결과
        """
        try:
            # 1. 작업 전 백업
            backup_id = await self._create_backup(task["target_path"])

            # 2. Claude Code 실행
            result = await self.client.refactor(
                instructions=self._format_instructions(task["instructions"]),
                path=task["target_path"],
                context=task.get("context", {}),
                create_pr=self.config["github"]["create_pr"],
                pr_title=self._generate_pr_title(task),
                pr_body=self._generate_pr_body(task)
            )

            # 3. 결과 검증
            if not await self._validate_changes(result):
                await self._rollback(backup_id)
                raise ValueError("변경사항 검증 실패")

            # 4. Context Store에 저장
            await self.context_store.store_implementation_log(
                modified_files=result.get("modified_files", []),
                changes=result.get("changes", []),
                pr_url=result.get("pr_url"),
                evolution_id=task["evolution_id"]
            )

            return {
                "success": True,
                "pr_url": result.get("pr_url"),
                "modified_files": result.get("modified_files", []),
                "changes": result.get("changes", []),
                "metrics": self._calculate_metrics(result)
            }

        except Exception as e:
            logger.error(f"Claude Code 실행 실패: {e}")
            await self._rollback(backup_id)
            return {
                "success": False,
                "error": str(e)
            }

    def _format_instructions(self, instructions: List[str]) -> str:
        """Claude Code용 지시사항 포맷팅."""
        formatted = "다음 작업을 수행해주세요:\n\n"
        for i, instruction in enumerate(instructions, 1):
            formatted += f"{i}. {instruction}\n"
        formatted += "\n요구사항:\n"
        formatted += "- 모든 변경사항에 대해 테스트 작성\n"
        formatted += "- 타입 힌트 추가\n"
        formatted += "- Docstring 작성\n"
        formatted += "- SOLID 원칙 준수\n"
        return formatted

    def _generate_pr_title(self, task: Dict[str, Any]) -> str:
        """PR 제목 생성."""
        return f"refactor: {task.get('description', 'Code improvements via Claude Code')}"

    def _generate_pr_body(self, task: Dict[str, Any]) -> str:
        """PR 본문 생성."""
        return f"""## 📝 Summary

Claude Code를 통한 자동 코드 개선

## 🔄 Changes

{self._format_changes_list(task.get('instructions', []))}

## 🧪 Test Plan

- [ ] 단위 테스트 통과
- [ ] 통합 테스트 통과
- [ ] 코드 품질 메트릭 개선

## 📊 Metrics Impact

- Docstring Coverage: TBD
- Type Coverage: TBD
- Code Complexity: TBD

---

🤖 Generated by T-Developer with Claude Code
Evolution ID: {task.get('evolution_id', 'N/A')}
"""

    async def _validate_changes(self, result: Dict[str, Any]) -> bool:
        """변경사항 검증."""
        # 1. 테스트 실행
        test_passed = await self._run_tests(result.get("modified_files", []))

        # 2. 보안 스캔
        security_ok = await self._security_scan(result.get("changes", []))

        # 3. 품질 체크
        quality_ok = await self._quality_check(result.get("modified_files", []))

        return test_passed and security_ok and quality_ok
```

### 2. MCP 설정 파일

```json
// mcp_config.json
{
  "version": "1.0",
  "tools": {
    "filesystem": {
      "enabled": true,
      "permissions": {
        "read": ["**/*"],
        "write": ["backend/**", "frontend/src/**", "tests/**"],
        "create": ["tests/**"],
        "delete": false
      }
    },
    "git": {
      "enabled": true,
      "permissions": {
        "commit": true,
        "branch": true,
        "push": false,  // PR only mode
        "merge": false
      }
    },
    "github": {
      "enabled": true,
      "permissions": {
        "create_pr": true,
        "update_pr": true,
        "close_pr": false,
        "merge_pr": false,
        "create_issue": true
      }
    },
    "shell": {
      "enabled": false  // 보안상 비활성화
    }
  },
  "security": {
    "sandbox": true,
    "timeout": 600,  // 10 minutes
    "max_memory": "4GB",
    "forbidden_patterns": [
      "**/.env",
      "**/*.key",
      "**/*.pem",
      "**/secrets/**"
    ]
  }
}
```

### 3. Docker 샌드박스 설정

```dockerfile
# Dockerfile.claude-code-sandbox
FROM python:3.11-slim

# 보안 그룹 및 사용자 생성
RUN groupadd -r claude && useradd -r -g claude claude

# 필수 패키지 설치
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Claude Code SDK 설치
RUN pip install --no-cache-dir \
    claude-code-sdk \
    anthropic \
    mcp-filesystem \
    mcp-git

# 작업 디렉토리 설정
WORKDIR /workspace

# 권한 설정
RUN chown -R claude:claude /workspace

# 보안 설정
USER claude

# 환경 변수
ENV CLAUDE_CODE_SANDBOX=true
ENV MCP_CONFIG_PATH=/workspace/mcp_config.json

# 엔트리포인트
ENTRYPOINT ["python", "-m", "claude_code"]
```

## 🔐 보안 고려사항

### 1. 권한 최소화

```yaml
github_permissions:
  - pull_requests: write  # PR 생성만 가능
  - contents: read        # 코드 읽기만 가능
  - issues: write        # 이슈 생성 가능

forbidden_actions:
  - direct_push_to_main
  - delete_branch
  - modify_github_actions
  - access_secrets
```

### 2. 격리 실행

```python
# 샌드박스 실행 래퍼
class SandboxedClaudeCode:
    def __init__(self):
        self.container_runtime = "docker"
        self.image = "claude-code-sandbox:latest"

    async def run_in_sandbox(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """컨테이너 내에서 Claude Code 실행."""
        container = await self.create_container(
            image=self.image,
            volumes={
                "/tmp/workspace": "/workspace:rw"
            },
            environment={
                "ANTHROPIC_API_KEY": self._get_api_key(),
                "GITHUB_TOKEN": self._get_github_token()
            },
            resource_limits={
                "cpu": "2",
                "memory": "4g",
                "pids": 100
            }
        )

        result = await container.run(task)
        await container.cleanup()

        return result
```

### 3. 감사 로깅

```python
# 모든 Claude Code 작업 로깅
class AuditLogger:
    def log_claude_code_action(self, action: Dict[str, Any]):
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "action_type": "claude_code_refactor",
            "evolution_id": action.get("evolution_id"),
            "modified_files": action.get("modified_files"),
            "pr_url": action.get("pr_url"),
            "user": action.get("user", "system"),
            "success": action.get("success"),
            "error": action.get("error")
        }

        # DynamoDB에 저장
        self.save_to_audit_log(audit_entry)
```

## 📊 비용 관리

### Usage Tracking

```python
class ClaudeCodeUsageTracker:
    """Claude Code API 사용량 추적."""

    async def track_usage(self, customer_id: str, usage: Dict[str, Any]):
        """고객별 사용량 기록."""
        await self.dynamodb.put_item(
            TableName="claude_code_usage",
            Item={
                "customer_id": customer_id,
                "timestamp": datetime.now().isoformat(),
                "tokens_used": usage.get("tokens"),
                "api_calls": usage.get("calls"),
                "cost_estimate": self.calculate_cost(usage)
            }
        )

    def calculate_cost(self, usage: Dict[str, Any]) -> float:
        """비용 계산."""
        # Claude Code API 가격 정책에 따른 계산
        tokens = usage.get("tokens", 0)
        cost_per_1k_tokens = 0.01  # 예시 가격
        return (tokens / 1000) * cost_per_1k_tokens
```

## 🚀 배포 체크리스트

- [ ] Anthropic API Key 설정
- [ ] GitHub OIDC 설정
- [ ] MCP 설정 파일 생성
- [ ] Docker 샌드박스 이미지 빌드
- [ ] 보안 정책 설정
- [ ] 사용량 추적 테이블 생성
- [ ] PR 템플릿 준비
- [ ] CI/CD 파이프라인 업데이트

## 📈 예상 효과

1. **코드 품질 향상**
   - 일관된 코딩 스타일
   - 자동 테스트 생성
   - SOLID 원칙 준수

2. **개발 속도 향상**
   - 반복적인 리팩토링 자동화
   - PR 자동 생성
   - 코드 리뷰 부담 감소

3. **안전성 보장**
   - PR-only 모드로 직접 수정 차단
   - 샌드박스 실행으로 격리
   - 자동 롤백 메커니즘

---

**작성일**: 2025-08-17
**버전**: 1.0.0
**상태**: 🟢 Ready for Implementation
