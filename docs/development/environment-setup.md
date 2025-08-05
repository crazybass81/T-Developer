# Development Environment Setup

## System Requirements
- **OS**: macOS, Linux, Windows (WSL2)
- **Node.js**: 18.0.0 or higher
- **Python**: 3.9.0 or higher
- **Memory**: 8GB RAM minimum
- **Storage**: 10GB free space

## Tool Installation

### UV Package Manager
```bash
# Install uv (107x faster than pip)
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### AWS CLI
```bash
# Install AWS CLI v2
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```

### Docker
```bash
# Install Docker Desktop
# Follow platform-specific instructions
```

## IDE Configuration

### VS Code Extensions
- Python
- TypeScript
- AWS Toolkit
- Docker
- GitLens

### Settings
```json
{
  "python.defaultInterpreterPath": "./.venv/bin/python",
  "typescript.preferences.importModuleSpecifier": "relative"
}
```