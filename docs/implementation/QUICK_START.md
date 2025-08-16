# Quick Start Guide

## Prerequisites

### Required Tools
- Python 3.9+
- AWS CLI configured
- Docker (for sandbox execution)
- Git

### Required Accounts
- AWS Account with Bedrock access
- GitHub account with repo permissions
- Claude API key (for Claude Code)

## Installation

### 1. Clone and Setup Environment

```bash
# Clone repository
git clone https://github.com/your-org/t-developer-v2.git
cd t-developer-v2

# Create Python environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install uv
uv pip install -r requirements.txt
```

### 2. Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your values
nano .env
```

Required environment variables:
```env
# AWS Configuration
AWS_REGION=us-east-1
AWS_PROFILE=default

# Bedrock Configuration
BEDROCK_AGENT_ID=your-agent-id
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0

# Claude Configuration
CLAUDE_API_KEY=your-claude-api-key

# GitHub Configuration
MCP_GITHUB_TOKEN=your-github-token

# Evolution Settings
EVOLUTION_MODE=enabled
AI_AUTONOMY_LEVEL=0.85
```

### 3. Initialize the System

```bash
# Run initialization script
python scripts/init_evolution.py

# This will:
# - Check environment configuration
# - Setup MCP servers
# - Create agent skeletons
# - Verify connections
```

## First Evolution Cycle

### 1. Manual Test Run

```bash
# Dry run to see what would happen
python scripts/run_evolution.py --target ./packages/agents --cycles 1 --dry-run

# If everything looks good, run for real
python scripts/run_evolution.py --target ./packages/agents --cycles 1
```

### 2. Monitor Progress

The evolution cycle will:
1. **Research**: Scan code for improvements
2. **Plan**: Create task breakdown
3. **Code**: Implement changes
4. **Evaluate**: Measure impact

You can monitor progress in real-time:
```bash
# Watch logs
tail -f evolution_history/latest.log

# Check metrics
python scripts/check_metrics.py --target packages/agents
```

### 3. Review Results

After completion:
- Check the created PR on GitHub
- Review the evaluation report
- Verify all quality gates passed

## Common Tasks

### Running Specific Phases

```bash
# Just research
python scripts/run_evolution.py --phase research --target ./packages/

# Just planning
python scripts/run_evolution.py --phase plan --input research_output.json

# Just coding
python scripts/run_evolution.py --phase code --task "Add docstrings to all functions"
```

### Checking System Health

```bash
# Run health checks
python scripts/health_check.py

# Check agent status
python scripts/agent_status.py

# Verify MCP connections
python scripts/test_mcp.py
```

### Manual Quality Checks

```bash
# Check code quality
ruff check packages/
black --check packages/
mypy packages/

# Check documentation
interrogate -v packages/

# Check complexity
radon cc packages/ -nb
radon mi packages/ -nb

# Run security scan
semgrep --config=auto packages/
```

## Troubleshooting

### Common Issues

#### 1. MCP Connection Failed
```bash
# Test MCP servers individually
python -m mcp.test filesystem
python -m mcp.test git
python -m mcp.test github

# Check server logs
cat ~/.mcp/logs/server.log
```

#### 2. AWS Authentication Issues
```bash
# Verify AWS credentials
aws sts get-caller-identity

# Check Bedrock access
aws bedrock list-foundation-models
```

#### 3. Evolution Cycle Stuck
```bash
# Check running processes
ps aux | grep evolution

# Force stop if needed
python scripts/stop_evolution.py --force

# Clean up incomplete cycles
python scripts/cleanup.py --incomplete
```

### Debug Mode

Run with detailed logging:
```bash
# Set debug environment
export DEBUG=true
export LOG_LEVEL=DEBUG

# Run with verbose output
python scripts/run_evolution.py --verbose --debug
```

## Next Steps

1. **Customize Agents**: Modify agent behavior in `packages/agents/`
2. **Add Patterns**: Create new improvement patterns in `configs/patterns/`
3. **Extend MCP**: Add new MCP servers for additional tools
4. **Configure A2A**: Integrate external specialized agents
5. **Setup Monitoring**: Deploy CloudWatch dashboards

## Getting Help

- **Documentation**: See `/docs/` folder
- **Issues**: Report at GitHub Issues
- **Logs**: Check `evolution_history/` for detailed logs
- **Metrics**: Run `python scripts/show_metrics.py`

## Safety Notes

⚠️ **Important Safety Guidelines**:

1. **Always run in sandbox first**: Use `--dry-run` flag
2. **Set resource limits**: Configure max cycles and timeouts
3. **Monitor costs**: Check AWS billing regularly
4. **Review PRs**: Don't auto-merge without review
5. **Backup before major changes**: Use git tags

## Example Workflows

### Improve Documentation
```bash
python scripts/run_evolution.py \
  --target ./packages/agents \
  --focus documentation \
  --metric "docstring_coverage>90"
```

### Reduce Complexity
```bash
python scripts/run_evolution.py \
  --target ./packages/agents \
  --focus complexity \
  --metric "mi>70"
```

### Add Tests
```bash
python scripts/run_evolution.py \
  --target ./packages/agents \
  --focus testing \
  --metric "coverage>85"
```

### Full Improvement Cycle
```bash
python scripts/run_evolution.py \
  --target ./packages/ \
  --cycles 3 \
  --all-metrics
```