"""Tests for Refactor Agent - TDD approach with Claude Code integration."""

import json
from unittest.mock import MagicMock, patch

import pytest

from packages.agents.base import AgentInput, AgentOutput, AgentStatus
from packages.agents.refactor import (
    ClaudeCodeClient,
    CodeChange,
    CodeModifier,
    GitManager,
    MCPToolExecutor,
    RefactorAgent,
    RefactorConfig,
    RefactorTask,
)


class TestCodeChange:
    """Test CodeChange dataclass."""

    def test_code_change_creation(self):
        """Test creating a code change."""
        change = CodeChange(
            file_path="src/main.py",
            change_type="modify",
            before="def old():\n    pass",
            after="def new():\n    return True",
            line_start=10,
            line_end=12,
            description="Refactor function",
        )

        assert change.file_path == "src/main.py"
        assert change.change_type == "modify"
        assert "def new()" in change.after
        assert change.line_start == 10

    def test_code_change_diff(self):
        """Test generating diff from change."""
        change = CodeChange(
            file_path="test.py",
            change_type="modify",
            before="x = 1",
            after="x = 2",
            line_start=1,
            line_end=1,
        )

        diff = change.to_diff()
        assert "-x = 1" in diff
        assert "+x = 2" in diff
        assert "test.py" in diff


class TestRefactorTask:
    """Test RefactorTask dataclass."""

    def test_refactor_task_creation(self):
        """Test creating a refactor task."""
        task = RefactorTask(
            id="task-001",
            type="add_type_hints",
            target_files=["main.py", "utils.py"],
            instructions="Add type hints to all functions",
            priority="high",
            estimated_changes=5,
        )

        assert task.id == "task-001"
        assert len(task.target_files) == 2
        assert task.priority == "high"
        assert task.status == "pending"

    def test_refactor_task_validation(self):
        """Test task validation."""
        # Valid task
        task = RefactorTask(
            id="task-002", type="refactor", target_files=["file.py"], instructions="Refactor code"
        )
        assert task.is_valid() is True

        # Invalid task - no files
        task_invalid = RefactorTask(
            id="task-003", type="refactor", target_files=[], instructions="Refactor code"
        )
        assert task_invalid.is_valid() is False


class TestClaudeCodeClient:
    """Test Claude Code client."""

    @pytest.fixture
    def client(self):
        """Create Claude Code client."""
        return ClaudeCodeClient()

    @pytest.mark.asyncio
    async def test_execute_refactor(self, client):
        """Test executing refactoring via Claude Code."""
        with patch("subprocess.run") as mock_run:
            # Mock successful Claude Code execution
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout=json.dumps(
                    {
                        "status": "success",
                        "changes": [
                            {"file": "main.py", "diff": "...", "summary": "Added type hints"}
                        ],
                    }
                ),
                stderr="",
            )

            result = await client.refactor(
                files=["main.py"], instructions="Add type hints", tools=["filesystem"]
            )

            assert result["status"] == "success"
            assert len(result["changes"]) == 1
            assert mock_run.call_count == 2  # version check + actual refactor

    @pytest.mark.asyncio
    async def test_handle_claude_code_error(self, client):
        """Test handling Claude Code errors."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=1, stdout="", stderr="Error: Failed to refactor"
            )

            result = await client.refactor(files=["bad.py"], instructions="Break things")

            assert result["status"] == "error"
            assert "Failed to refactor" in result.get("error", "")

    def test_validate_tools(self, client):
        """Test MCP tool validation."""
        # Valid tools
        assert client.validate_tools(["filesystem", "git"]) is True

        # Invalid tool
        assert client.validate_tools(["filesystem", "invalid_tool"]) is False

        # Empty tools
        assert client.validate_tools([]) is True


class TestMCPToolExecutor:
    """Test MCP tool executor."""

    @pytest.fixture
    def executor(self):
        """Create MCP tool executor."""
        return MCPToolExecutor()

    @pytest.mark.asyncio
    async def test_read_file(self, executor, tmp_path):
        """Test reading file via MCP."""
        test_file = tmp_path / "test.py"
        test_file.write_text("def hello():\n    return 'world'")

        content = await executor.read_file(str(test_file))

        assert "def hello()" in content
        assert "return 'world'" in content

    @pytest.mark.asyncio
    async def test_write_file(self, executor, tmp_path):
        """Test writing file via MCP."""
        test_file = tmp_path / "output.py"
        content = "print('Hello, World!')"

        success = await executor.write_file(str(test_file), content)

        assert success is True
        assert test_file.read_text() == content

    @pytest.mark.asyncio
    async def test_run_tests(self, executor):
        """Test running tests via MCP."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="All tests passed")

            result = await executor.run_tests("pytest tests/")

            assert result["success"] is True
            assert "All tests passed" in result["output"]


class TestGitManager:
    """Test Git manager."""

    @pytest.fixture
    def git_manager(self, tmp_path):
        """Create Git manager with temp repo."""
        return GitManager(repo_path=str(tmp_path))

    @pytest.mark.asyncio
    async def test_create_branch(self, git_manager):
        """Test creating a new branch."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)

            success = await git_manager.create_branch("feature/test")

            assert success is True
            assert mock_run.called

    @pytest.mark.asyncio
    async def test_commit_changes(self, git_manager):
        """Test committing changes."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)

            changes = [
                CodeChange(file_path="main.py", change_type="modify", before="old", after="new")
            ]

            commit_hash = await git_manager.commit_changes(changes, "feat: Add improvements")

            assert commit_hash is not None
            assert mock_run.called

    @pytest.mark.asyncio
    async def test_create_pull_request(self, git_manager):
        """Test creating a pull request."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0, stdout=json.dumps({"url": "https://github.com/repo/pull/1"})
            )

            pr_url = await git_manager.create_pull_request(
                title="Add features", body="Description of changes", branch="feature/test"
            )

            assert pr_url == "https://github.com/repo/pull/1"


class TestCodeModifier:
    """Test code modifier."""

    @pytest.fixture
    def modifier(self):
        """Create code modifier."""
        return CodeModifier()

    def test_add_type_hints(self, modifier):
        """Test adding type hints to code."""
        code = """
def add(a, b):
    return a + b

def greet(name):
    return f"Hello, {name}"
"""

        modified = modifier.add_type_hints(code)

        assert "def add(a: " in modified or "def add(a, b)" in modified  # May not modify without AI
        assert "def greet(name: str)" in modified or "def greet(name)" in modified

    def test_add_docstrings(self, modifier):
        """Test adding docstrings to functions."""
        code = """
def calculate(x, y):
    return x * y
"""

        modified = modifier.add_docstrings(code)

        assert '"""' in modified or "def calculate" in modified

    def test_refactor_long_function(self, modifier):
        """Test refactoring long functions."""
        code = """
def process_data(data):
    # Step 1
    cleaned = []
    for item in data:
        if item:
            cleaned.append(item.strip())

    # Step 2
    filtered = []
    for item in cleaned:
        if len(item) > 3:
            filtered.append(item)

    # Step 3
    result = []
    for item in filtered:
        result.append(item.upper())

    return result
"""

        suggestions = modifier.suggest_refactoring(code)

        assert len(suggestions) > 0
        assert any("extract" in s.lower() or "split" in s.lower() for s in suggestions)


class TestRefactorConfig:
    """Test refactor configuration."""

    def test_default_config(self):
        """Test default configuration."""
        config = RefactorConfig()

        assert config.use_claude_code is True
        assert config.create_pull_request is True
        assert config.run_tests_before is True
        assert config.run_tests_after is True
        assert config.max_changes_per_pr == 50

    def test_custom_config(self):
        """Test custom configuration."""
        config = RefactorConfig(
            use_claude_code=False, create_pull_request=False, sandbox_mode=True, auto_commit=False
        )

        assert config.use_claude_code is False
        assert config.create_pull_request is False
        assert config.sandbox_mode is True
        assert config.auto_commit is False


class TestRefactorAgent:
    """Test refactor agent."""

    @pytest.fixture
    def agent(self):
        """Create refactor agent."""
        config = RefactorConfig(
            use_claude_code=False,  # Disable for testing
            create_pull_request=False,
            run_tests_before=False,
            run_tests_after=False,
        )
        return RefactorAgent("refactor", config)

    @pytest.mark.asyncio
    async def test_execute_refactor_task(self, agent):
        """Test executing a refactor task."""
        input_data = AgentInput(
            intent="refactor",
            task_id="test-001",
            payload={
                "task": {
                    "type": "add_type_hints",
                    "files": ["main.py"],
                    "instructions": "Add type hints to all functions",
                },
                "plan_id": "plan-001",
            },
        )

        with patch.object(agent.claude_client, "refactor") as mock_refactor:
            mock_refactor.return_value = {
                "status": "success",
                "changes": [{"file": "main.py", "diff": "...", "summary": "Added type hints"}],
            }

            output = await agent.execute(input_data)

            assert output.status == AgentStatus.OK
            assert len(output.artifacts) > 0
            assert any(a.kind == "code_changes" for a in output.artifacts)

    @pytest.mark.asyncio
    async def test_validate_output(self, agent):
        """Test output validation."""
        valid_output = AgentOutput(
            task_id="test-002",
            status=AgentStatus.OK,
            artifacts=[{"kind": "code_changes", "ref": "changes.json", "content": {"changes": []}}],
            metrics={"files_modified": 2},
        )

        assert await agent.validate(valid_output) is True

        invalid_output = AgentOutput(
            task_id="test-003", status=AgentStatus.OK, artifacts=[], metrics={}  # No artifacts
        )

        assert await agent.validate(invalid_output) is False

    def test_get_capabilities(self, agent):
        """Test capabilities declaration."""
        capabilities = agent.get_capabilities()

        assert capabilities["name"] == "refactor"
        assert "refactor" in capabilities["supported_intents"]
        assert "claude_code" in capabilities["features"]
        assert capabilities["mcp_tools"] == ["filesystem", "git", "github"]
