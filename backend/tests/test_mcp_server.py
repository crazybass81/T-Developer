"""Tests for MCP Server implementation."""

import json
from unittest.mock import patch

import pytest
from packages.mcp.server.main import (
    MCPServer,
    SecurityValidator,
    ToolExecutor,
    ToolRequest,
    ToolType,
)


class TestSecurityValidator:
    """Test security validation."""

    def test_authentication_disabled(self):
        """Test authentication when disabled."""
        config = {"authentication": {"enabled": False}}
        validator = SecurityValidator(config)

        assert validator.validate_authentication(None) is True
        assert validator.validate_authentication("wrong") is True

    def test_authentication_enabled(self):
        """Test authentication when enabled."""
        config = {"authentication": {"enabled": True}}

        with patch.dict("os.environ", {"MCP_SECURITY_TOKEN": "secret"}):
            validator = SecurityValidator(config)

            assert validator.validate_authentication("secret") is True
            assert validator.validate_authentication("wrong") is False
            assert validator.validate_authentication(None) is False

    def test_validate_request_tool_disabled(self):
        """Test request validation with disabled tool."""
        config = {"tools": {"filesystem": {"enabled": False}}}
        validator = SecurityValidator(config)

        request = ToolRequest(id="1", tool=ToolType.FILESYSTEM, operation="read", parameters={})

        assert validator.validate_request(request) is False

    def test_validate_request_git_operations(self):
        """Test git operation validation."""
        config = {
            "tools": {
                "git": {
                    "enabled": True,
                    "permissions": {
                        "allowed_operations": ["status", "diff"],
                        "denied_operations": ["force-push"],
                    },
                }
            }
        }
        validator = SecurityValidator(config)

        # Allowed operation
        request = ToolRequest(id="1", tool=ToolType.GIT, operation="status", parameters={})
        assert validator.validate_request(request) is True

        # Denied operation
        request = ToolRequest(id="2", tool=ToolType.GIT, operation="force-push", parameters={})
        assert validator.validate_request(request) is False


class TestToolExecutor:
    """Test tool execution."""

    @pytest.mark.asyncio
    async def test_filesystem_read(self, tmp_path):
        """Test filesystem read operation."""
        # Create test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello World")

        config = {}
        executor = ToolExecutor(config)

        request = ToolRequest(
            id="1", tool=ToolType.FILESYSTEM, operation="read", parameters={"path": str(test_file)}
        )

        response = await executor.execute(request)

        assert response.success is True
        assert response.result == "Hello World"
        assert response.error is None

    @pytest.mark.asyncio
    async def test_filesystem_write(self, tmp_path):
        """Test filesystem write operation."""
        test_file = tmp_path / "output.txt"

        config = {}
        executor = ToolExecutor(config)

        request = ToolRequest(
            id="2",
            tool=ToolType.FILESYSTEM,
            operation="write",
            parameters={"path": str(test_file), "content": "Test content"},
        )

        response = await executor.execute(request)

        assert response.success is True
        assert test_file.exists()
        assert test_file.read_text() == "Test content"

    @pytest.mark.asyncio
    async def test_filesystem_list(self, tmp_path):
        """Test filesystem list operation."""
        # Create test files
        (tmp_path / "file1.txt").touch()
        (tmp_path / "file2.txt").touch()
        (tmp_path / "subdir").mkdir()

        config = {}
        executor = ToolExecutor(config)

        request = ToolRequest(
            id="3", tool=ToolType.FILESYSTEM, operation="list", parameters={"path": str(tmp_path)}
        )

        response = await executor.execute(request)

        assert response.success is True
        assert len(response.result) == 3
        assert any("file1.txt" in item for item in response.result)
        assert any("file2.txt" in item for item in response.result)
        assert any("subdir" in item for item in response.result)

    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling in executor."""
        config = {}
        executor = ToolExecutor(config)

        request = ToolRequest(
            id="4",
            tool=ToolType.FILESYSTEM,
            operation="read",
            parameters={"path": "/nonexistent/file.txt"},
        )

        response = await executor.execute(request)

        assert response.success is False
        assert response.error is not None
        assert "not found" in response.error.lower()


class TestMCPServer:
    """Test MCP Server."""

    @pytest.fixture
    def config_file(self, tmp_path):
        """Create temporary config file."""
        config = {
            "security": {"authentication": {"enabled": False}},
            "tools": {"filesystem": {"enabled": True}, "git": {"enabled": True}},
        }

        config_path = tmp_path / "config.json"
        config_path.write_text(json.dumps(config))

        return str(config_path)

    def test_load_config(self, config_file):
        """Test configuration loading."""
        server = MCPServer(config_file)

        assert server.config is not None
        assert "security" in server.config
        assert "tools" in server.config

    def test_expand_env_vars(self):
        """Test environment variable expansion."""
        with patch.dict("os.environ", {"TEST_VAR": "test_value"}):
            server = MCPServer()

            # Test string expansion
            result = server._expand_env_vars("${TEST_VAR}")
            assert result == "test_value"

            # Test dict expansion
            result = server._expand_env_vars({"key": "${TEST_VAR}"})
            assert result["key"] == "test_value"

            # Test list expansion
            result = server._expand_env_vars(["${TEST_VAR}", "static"])
            assert result[0] == "test_value"
            assert result[1] == "static"

    @pytest.mark.asyncio
    async def test_handle_request_success(self, config_file, tmp_path):
        """Test successful request handling."""
        server = MCPServer(config_file)

        # Create test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("Test content")

        request = {
            "id": "1",
            "tool": "filesystem",
            "operation": "read",
            "parameters": {"path": str(test_file)},
            "auth": {"token": ""},
        }

        response = await server.handle_request(json.dumps(request))
        response_data = json.loads(response)

        assert response_data["success"] is True
        assert response_data["result"] == "Test content"
        assert response_data["id"] == "1"

    @pytest.mark.asyncio
    async def test_handle_request_auth_failure(self):
        """Test request with authentication failure."""
        config = {"security": {"authentication": {"enabled": True}}}

        with patch.dict("os.environ", {"MCP_SECURITY_TOKEN": "secret"}):
            server = MCPServer()
            server.config = config
            server.validator = SecurityValidator(config["security"])

            request = {
                "id": "2",
                "tool": "filesystem",
                "operation": "read",
                "parameters": {"path": "/test.txt"},
                "auth": {"token": "wrong"},
            }

            response = await server.handle_request(json.dumps(request))
            response_data = json.loads(response)

            assert "error" in response_data
            assert "authentication" in response_data["error"].lower()

    @pytest.mark.asyncio
    async def test_handle_request_validation_failure(self, config_file):
        """Test request validation failure."""
        server = MCPServer(config_file)

        # Disable filesystem tool
        server.config["tools"]["filesystem"]["enabled"] = False
        server.validator = SecurityValidator(server.config)

        request = {
            "id": "3",
            "tool": "filesystem",
            "operation": "read",
            "parameters": {"path": "/test.txt"},
            "auth": {"token": ""},
        }

        response = await server.handle_request(json.dumps(request))
        response_data = json.loads(response)

        assert "error" in response_data
        assert "validation" in response_data["error"].lower()

    @pytest.mark.asyncio
    async def test_handle_malformed_request(self, config_file):
        """Test handling of malformed request."""
        server = MCPServer(config_file)

        response = await server.handle_request("invalid json")
        response_data = json.loads(response)

        assert "error" in response_data


class TestIntegration:
    """Integration tests for MCP Server."""

    @pytest.mark.asyncio
    async def test_full_workflow(self, tmp_path):
        """Test complete workflow."""
        # Create config
        config = {
            "security": {"authentication": {"enabled": True}},
            "tools": {
                "filesystem": {
                    "enabled": True,
                    "permissions": {
                        "read": {"allowed_paths": [str(tmp_path) + "/**"]},
                        "write": {"allowed_paths": [str(tmp_path) + "/**"]},
                    },
                }
            },
        }

        config_path = tmp_path / "config.json"
        config_path.write_text(json.dumps(config))

        with patch.dict("os.environ", {"MCP_SECURITY_TOKEN": "test_token"}):
            server = MCPServer(str(config_path))

            # Test write
            write_request = {
                "id": "1",
                "tool": "filesystem",
                "operation": "write",
                "parameters": {"path": str(tmp_path / "test.txt"), "content": "Hello MCP"},
                "auth": {"token": "test_token"},
            }

            response = await server.handle_request(json.dumps(write_request))
            response_data = json.loads(response)
            assert response_data["success"] is True

            # Test read
            read_request = {
                "id": "2",
                "tool": "filesystem",
                "operation": "read",
                "parameters": {"path": str(tmp_path / "test.txt")},
                "auth": {"token": "test_token"},
            }

            response = await server.handle_request(json.dumps(read_request))
            response_data = json.loads(response)
            assert response_data["success"] is True
            assert response_data["result"] == "Hello MCP"
