"""MCP Client for interacting with the MCP Server."""

import asyncio
import json
import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Optional

from packages.mcp.server.main import ToolResponse, ToolType

logger = logging.getLogger("mcp.client")


class MCPClient:
    """Client for interacting with MCP Server."""

    def __init__(self, server_config: Optional[str] = None):
        """Initialize MCP Client.

        Args:
            server_config: Path to server configuration
        """
        self.server_config = server_config or str(Path(__file__).parent / "server" / "config.json")
        self.token = os.getenv("MCP_SECURITY_TOKEN", "")
        self.process: Optional[subprocess.Popen] = None
        self.request_id = 0

    async def start_server(self):
        """Start the MCP server process."""
        if self.process and self.process.poll() is None:
            logger.info("Server already running")
            return

        env = os.environ.copy()
        env["MCP_CONFIG_PATH"] = self.server_config

        self.process = subprocess.Popen(
            [sys.executable, "-m", "packages.mcp.server.main"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            text=True,
            bufsize=1,
        )

        logger.info("MCP Server started")

        # Wait for server to be ready
        await asyncio.sleep(1)

    async def stop_server(self):
        """Stop the MCP server process."""
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            self.process = None
            logger.info("MCP Server stopped")

    async def send_request(
        self,
        tool: ToolType,
        operation: str,
        parameters: dict[str, Any],
        metadata: Optional[dict[str, Any]] = None,
    ) -> ToolResponse:
        """Send a request to the MCP server.

        Args:
            tool: Tool type
            operation: Operation to perform
            parameters: Operation parameters
            metadata: Optional metadata

        Returns:
            Tool response

        Raises:
            RuntimeError: If server is not running
        """
        if not self.process or self.process.poll() is not None:
            raise RuntimeError("MCP Server is not running")

        self.request_id += 1

        request = {
            "id": str(self.request_id),
            "tool": tool.value,
            "operation": operation,
            "parameters": parameters,
            "metadata": metadata,
            "auth": {"token": self.token},
        }

        # Send request
        request_json = json.dumps(request) + "\n"
        self.process.stdin.write(request_json)
        self.process.stdin.flush()

        # Read response
        response_line = self.process.stdout.readline()
        if not response_line:
            raise RuntimeError("No response from server")

        response_data = json.loads(response_line.strip())

        if "error" in response_data and "id" not in response_data:
            raise RuntimeError(f"Server error: {response_data['error']}")

        return ToolResponse(
            id=response_data["id"],
            success=response_data.get("success", False),
            result=response_data.get("result"),
            error=response_data.get("error"),
            metadata=response_data.get("metadata"),
        )

    # Convenience methods for common operations

    async def read_file(self, path: str) -> str:
        """Read a file through MCP.

        Args:
            path: File path to read

        Returns:
            File contents
        """
        response = await self.send_request(ToolType.FILESYSTEM, "read", {"path": path})

        if not response.success:
            raise RuntimeError(f"Failed to read file: {response.error}")

        return response.result

    async def write_file(self, path: str, content: str) -> None:
        """Write a file through MCP.

        Args:
            path: File path to write
            content: Content to write
        """
        response = await self.send_request(
            ToolType.FILESYSTEM, "write", {"path": path, "content": content}
        )

        if not response.success:
            raise RuntimeError(f"Failed to write file: {response.error}")

    async def list_directory(self, path: str = ".") -> list:
        """List directory contents through MCP.

        Args:
            path: Directory path

        Returns:
            List of items in directory
        """
        response = await self.send_request(ToolType.FILESYSTEM, "list", {"path": path})

        if not response.success:
            raise RuntimeError(f"Failed to list directory: {response.error}")

        return response.result

    async def git_status(self) -> str:
        """Get git status through MCP.

        Returns:
            Git status output
        """
        response = await self.send_request(ToolType.GIT, "status", {})

        if not response.success:
            raise RuntimeError(f"Failed to get git status: {response.error}")

        return response.result

    async def git_commit(self, message: str, files: Optional[list] = None) -> str:
        """Commit changes through MCP.

        Args:
            message: Commit message
            files: Files to add (defaults to all)

        Returns:
            Commit output
        """
        # Add files
        add_response = await self.send_request(ToolType.GIT, "add", {"files": files or ["."]})

        if not add_response.success:
            raise RuntimeError(f"Failed to add files: {add_response.error}")

        # Commit
        commit_response = await self.send_request(ToolType.GIT, "commit", {"message": message})

        if not commit_response.success:
            raise RuntimeError(f"Failed to commit: {commit_response.error}")

        return commit_response.result


async def example_usage():
    """Example usage of MCP Client."""
    client = MCPClient()

    try:
        # Start server
        await client.start_server()

        # List current directory
        items = await client.list_directory()
        print(f"Directory contents: {items}")

        # Write a test file
        test_file = "/tmp/mcp_test.txt"
        await client.write_file(test_file, "Hello from MCP!")

        # Read it back
        content = await client.read_file(test_file)
        print(f"File content: {content}")

        # Get git status
        try:
            status = await client.git_status()
            print(f"Git status: {status}")
        except Exception as e:
            print(f"Git operation failed: {e}")

    finally:
        # Stop server
        await client.stop_server()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(example_usage())
