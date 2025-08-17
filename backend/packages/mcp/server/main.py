"""MCP Server implementation for T-Developer v2."""

import asyncio
import json
import logging
import os
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Optional

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("mcp.server")


class ToolType(Enum):
    """Available tool types."""

    FILESYSTEM = "filesystem"
    GIT = "git"
    WEB = "web"
    DATABASE = "database"
    AWS = "aws"
    DOCKER = "docker"


@dataclass
class ToolRequest:
    """Tool execution request."""

    id: str
    tool: ToolType
    operation: str
    parameters: dict[str, Any]
    metadata: Optional[dict[str, Any]] = None


@dataclass
class ToolResponse:
    """Tool execution response."""

    id: str
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None


class SecurityValidator:
    """Validates tool requests against security policies."""

    def __init__(self, config: dict[str, Any]):
        """Initialize security validator.

        Args:
            config: Security configuration
        """
        self.config = config
        self.token = os.getenv("MCP_SECURITY_TOKEN")

    def validate_authentication(self, token: Optional[str]) -> bool:
        """Validate authentication token.

        Args:
            token: Provided authentication token

        Returns:
            True if authenticated
        """
        if not self.config.get("authentication", {}).get("enabled"):
            return True

        if not token or token != self.token:
            logger.warning("Authentication failed")
            return False

        return True

    def validate_request(self, request: ToolRequest) -> bool:
        """Validate tool request against security policies.

        Args:
            request: Tool request to validate

        Returns:
            True if request is allowed
        """
        # If no tools config, allow all
        if "tools" not in self.config:
            return True

        tool_config = self.config.get("tools", {}).get(request.tool.value, {})

        # If tool not in config, allow by default
        if not tool_config:
            return True

        if not tool_config.get("enabled", True):
            logger.warning(f"Tool {request.tool.value} is disabled")
            return False

        permissions = tool_config.get("permissions", {})

        # Check operation permissions
        if request.tool == ToolType.GIT:
            allowed_ops = permissions.get("allowed_operations", [])
            if request.operation not in allowed_ops:
                logger.warning(f"Git operation {request.operation} not allowed")
                return False

        # Add more validation logic as needed

        return True


class ToolExecutor:
    """Executes validated tool requests."""

    def __init__(self, config: dict[str, Any]):
        """Initialize tool executor.

        Args:
            config: Tool configuration
        """
        self.config = config

    async def execute(self, request: ToolRequest) -> ToolResponse:
        """Execute a tool request.

        Args:
            request: Validated tool request

        Returns:
            Tool execution response
        """
        try:
            if request.tool == ToolType.FILESYSTEM:
                result = await self._execute_filesystem(request)
            elif request.tool == ToolType.GIT:
                result = await self._execute_git(request)
            elif request.tool == ToolType.WEB:
                result = await self._execute_web(request)
            elif request.tool == ToolType.AWS:
                result = await self._execute_aws(request)
            elif request.tool == ToolType.DOCKER:
                result = await self._execute_docker(request)
            else:
                raise ValueError(f"Unsupported tool: {request.tool}")

            return ToolResponse(id=request.id, success=True, result=result)
        except Exception as e:
            logger.error(f"Tool execution failed: {e}")
            return ToolResponse(id=request.id, success=False, error=str(e))

    async def _execute_filesystem(self, request: ToolRequest) -> Any:
        """Execute filesystem operations.

        Args:
            request: Filesystem tool request

        Returns:
            Operation result
        """
        operation = request.operation
        params = request.parameters

        if operation == "read":
            path = Path(params["path"])
            if path.exists() and path.is_file():
                return path.read_text()
            else:
                raise FileNotFoundError(f"File not found: {path}")

        elif operation == "write":
            path = Path(params["path"])
            content = params["content"]
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
            return f"File written: {path}"

        elif operation == "list":
            path = Path(params.get("path", "."))
            if path.exists() and path.is_dir():
                return [str(p) for p in path.iterdir()]
            else:
                raise NotADirectoryError(f"Not a directory: {path}")

        else:
            raise ValueError(f"Unknown filesystem operation: {operation}")

    async def _execute_git(self, request: ToolRequest) -> Any:
        """Execute git operations.

        Args:
            request: Git tool request

        Returns:
            Operation result
        """
        import subprocess

        operation = request.operation
        params = request.parameters

        # Map operations to git commands
        git_commands = {
            "status": ["git", "status"],
            "diff": ["git", "diff"],
            "add": ["git", "add"] + params.get("files", ["."]),
            "commit": ["git", "commit", "-m", params.get("message", "")],
            "push": ["git", "push"],
            "pull": ["git", "pull"],
            "branch": ["git", "branch"],
        }

        if operation not in git_commands:
            raise ValueError(f"Unknown git operation: {operation}")

        cmd = git_commands[operation]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        if result.returncode != 0:
            raise RuntimeError(f"Git command failed: {result.stderr}")

        return result.stdout

    async def _execute_web(self, request: ToolRequest) -> Any:
        """Execute web requests.

        Args:
            request: Web tool request

        Returns:
            Operation result
        """
        # Placeholder for web operations
        return {"message": "Web operations not yet implemented"}

    async def _execute_aws(self, request: ToolRequest) -> Any:
        """Execute AWS operations.

        Args:
            request: AWS tool request

        Returns:
            Operation result
        """
        # Placeholder for AWS operations
        return {"message": "AWS operations not yet implemented"}

    async def _execute_docker(self, request: ToolRequest) -> Any:
        """Execute Docker operations.

        Args:
            request: Docker tool request

        Returns:
            Operation result
        """
        # Placeholder for Docker operations
        return {"message": "Docker operations not yet implemented"}


class MCPServer:
    """Main MCP Server implementation."""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize MCP Server.

        Args:
            config_path: Path to configuration file
        """
        self.config = self._load_config(config_path)
        self.validator = SecurityValidator(self.config.get("security", {}))
        self.executor = ToolExecutor(self.config)
        self.running = False

    def _load_config(self, config_path: Optional[str]) -> dict[str, Any]:
        """Load server configuration.

        Args:
            config_path: Path to configuration file

        Returns:
            Configuration dictionary
        """
        if config_path is None:
            config_path = Path(__file__).parent / "config.json"

        with open(config_path) as f:
            config = json.load(f)

        # Expand environment variables
        config = self._expand_env_vars(config)

        return config

    def _expand_env_vars(self, obj: Any) -> Any:
        """Recursively expand environment variables in configuration.

        Args:
            obj: Configuration object

        Returns:
            Configuration with expanded variables
        """
        if isinstance(obj, str):
            # Expand ${VAR} patterns
            import re

            pattern = r"\$\{([^}]+)\}"

            def replacer(match):
                var_name = match.group(1)
                return os.getenv(var_name, match.group(0))

            return re.sub(pattern, replacer, obj)
        elif isinstance(obj, dict):
            return {k: self._expand_env_vars(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._expand_env_vars(item) for item in obj]
        else:
            return obj

    async def handle_request(self, raw_request: str) -> str:
        """Handle incoming MCP request.

        Args:
            raw_request: Raw JSON request string

        Returns:
            JSON response string
        """
        try:
            # Parse request
            request_data = json.loads(raw_request)

            # Validate authentication
            token = request_data.get("auth", {}).get("token")
            if not self.validator.validate_authentication(token):
                return json.dumps({"error": "Authentication failed"})

            # Create tool request
            request = ToolRequest(
                id=request_data.get("id", ""),
                tool=ToolType(request_data["tool"]),
                operation=request_data["operation"],
                parameters=request_data.get("parameters", {}),
                metadata=request_data.get("metadata"),
            )

            # Validate request
            if not self.validator.validate_request(request):
                return json.dumps({"id": request.id, "error": "Request validation failed"})

            # Execute request
            response = await self.executor.execute(request)

            # Format response
            return json.dumps(
                {
                    "id": response.id,
                    "success": response.success,
                    "result": response.result,
                    "error": response.error,
                    "metadata": response.metadata,
                }
            )

        except Exception as e:
            logger.error(f"Request handling failed: {e}")
            return json.dumps({"error": str(e)})

    async def run_stdio(self):
        """Run server in stdio mode."""
        logger.info("Starting MCP Server in stdio mode")
        self.running = True

        while self.running:
            try:
                # Read request from stdin
                line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)

                if not line:
                    break

                # Handle request
                response = await self.handle_request(line.strip())

                # Write response to stdout
                print(response)
                sys.stdout.flush()

            except KeyboardInterrupt:
                logger.info("Server interrupted")
                break
            except Exception as e:
                logger.error(f"Server error: {e}")

    def stop(self):
        """Stop the server."""
        self.running = False
        logger.info("Server stopped")


async def main():
    """Main entry point."""
    config_path = os.getenv("MCP_CONFIG_PATH")
    server = MCPServer(config_path)

    try:
        await server.run_stdio()
    finally:
        server.stop()


if __name__ == "__main__":
    asyncio.run(main())
