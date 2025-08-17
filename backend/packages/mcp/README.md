# MCP (Model Context Protocol) Server

## Overview

The MCP Server provides safe, controlled tool access for AI agents in T-Developer v2. It implements the Model Context Protocol standard for secure agent-tool communication.

## Architecture

```
AI Agent → MCP Client → MCP Server → Tool Executor → System Resources
                ↓              ↓              ↓
         Authentication   Validation    Sandboxing
```

## Features

### Security

- **Token-based authentication**
- **Path-based permissions**
- **Command whitelisting/blacklisting**
- **Resource limits enforcement**
- **Audit logging**

### Supported Tools

1. **Filesystem**: Safe file operations
2. **Git**: Version control operations
3. **Web**: HTTP requests to approved domains
4. **AWS**: Limited AWS service access
5. **Docker**: Container management
6. **Database**: Safe database queries

## Quick Start

### Server Setup

```python
from packages.mcp import MCPServer

# Start server with default config
server = MCPServer()
await server.run_stdio()
```

### Client Usage

```python
from packages.mcp import MCPClient

# Initialize client
client = MCPClient()
await client.start_server()

# Read file
content = await client.read_file("/path/to/file.txt")

# Write file
await client.write_file("/path/to/output.txt", "Content")

# Git operations
status = await client.git_status()
await client.git_commit("feat: Add new feature")

# Stop server
await client.stop_server()
```

## Configuration

### Environment Variables

```bash
# Security token for authentication
export MCP_SECURITY_TOKEN=your-secret-token

# Configuration file path
export MCP_CONFIG_PATH=/path/to/config.json

# Workspace directory
export WORKSPACE_DIR=/tmp/workspace

# Log directory
export LOG_DIR=/var/log/mcp
```

### Configuration File

```json
{
  "security": {
    "authentication": {
      "enabled": true,
      "method": "token"
    }
  },
  "tools": {
    "filesystem": {
      "enabled": true,
      "permissions": {
        "read": {
          "allowed_paths": ["${WORKSPACE_DIR}/**"],
          "denied_paths": ["**/.env", "**/*.key"]
        },
        "write": {
          "allowed_paths": ["${WORKSPACE_DIR}/**"],
          "denied_paths": ["**/.git/**"]
        }
      }
    }
  }
}
```

## Security Model

### Permission Hierarchy

1. **Global deny rules** (highest priority)
2. **Tool-specific deny rules**
3. **Tool-specific allow rules**
4. **Global allow rules** (lowest priority)

### Path Validation

- Paths are resolved to absolute paths
- Symlinks are followed and validated
- Parent directory traversal is blocked
- Hidden files require explicit permission

### Command Execution

- Commands must be whitelisted
- Arguments are sanitized
- Environment variables are controlled
- Resource limits are enforced

## Tool Reference

### Filesystem Tool

```python
# Read file
response = await client.send_request(
    ToolType.FILESYSTEM,
    "read",
    {"path": "/path/to/file"}
)

# Write file
response = await client.send_request(
    ToolType.FILESYSTEM,
    "write",
    {"path": "/path/to/file", "content": "data"}
)

# List directory
response = await client.send_request(
    ToolType.FILESYSTEM,
    "list",
    {"path": "/path/to/dir"}
)
```

### Git Tool

```python
# Get status
response = await client.send_request(
    ToolType.GIT,
    "status",
    {}
)

# Commit changes
response = await client.send_request(
    ToolType.GIT,
    "commit",
    {"message": "Commit message", "files": ["file1.py"]}
)
```

## Testing

### Unit Tests

```bash
# Run MCP tests
pytest tests/test_mcp_server.py -v

# Run with coverage
pytest tests/test_mcp_server.py --cov=packages.mcp
```

### Integration Testing

```python
# Test script
import asyncio
from packages.mcp import MCPClient

async def test_integration():
    client = MCPClient()
    await client.start_server()

    # Test operations
    items = await client.list_directory()
    print(f"Files: {items}")

    await client.stop_server()

asyncio.run(test_integration())
```

## Monitoring

### Metrics

- Request count by tool
- Request latency
- Error rate
- Authentication failures
- Resource usage

### Logging

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Audit log location
tail -f /var/log/mcp/audit.log
```

## Troubleshooting

### Common Issues

1. **Authentication Failed**
   - Check MCP_SECURITY_TOKEN is set
   - Verify token matches in client and server

2. **Permission Denied**
   - Check path is in allowed_paths
   - Verify path is not in denied_paths
   - Check file permissions

3. **Tool Not Found**
   - Verify tool is enabled in config
   - Check tool name spelling

4. **Server Not Starting**
   - Check port is not in use
   - Verify Python path
   - Check config file syntax

## Development

### Adding New Tools

1. Create tool class in `tools/` directory
2. Implement tool interface
3. Add to ToolType enum
4. Update executor to handle tool
5. Add tests

### Custom Validators

```python
class CustomValidator:
    def validate(self, request: ToolRequest) -> bool:
        # Custom validation logic
        return True

# Register validator
server.add_validator(CustomValidator())
```

## Best Practices

1. **Always use authentication** in production
2. **Minimize allowed paths** to necessary directories
3. **Regularly rotate** security tokens
4. **Monitor audit logs** for suspicious activity
5. **Set resource limits** to prevent abuse
6. **Test permissions** thoroughly before deployment
7. **Use sandboxing** for untrusted operations

## Support

For issues or questions:

1. Check the logs in `${LOG_DIR}`
2. Review configuration
3. Run diagnostic tests
4. Check GitHub issues
