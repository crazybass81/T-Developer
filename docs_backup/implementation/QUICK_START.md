# Quick Start Guide

## Prerequisites

### Required Tools

- Python 3.9+
- AWS CLI configured
- Docker (for sandbox execution)
- Git

### Required Accounts

- AWS Account with Bedrock access
- OpenAI/Anthropic API keys (optional for AI features)
- GitHub account (optional for PR creation)

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
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret

# AI Integration (Optional)
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key

# Evolution Settings
EVOLUTION_MAX_CYCLES=10
EVOLUTION_DRY_RUN=false
ENABLE_CODE_MODIFICATION=true

# SharedContextStore Settings
CONTEXT_STORE_ENABLED=true
CONTEXT_STORE_EXPORT_PATH=./evolution_contexts
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

### 1. Start the Backend Server

```bash
# Start the FastAPI server
cd backend
python main.py
# Server runs on http://localhost:8000
```

### 2. Start the Frontend Dashboard (Optional)

```bash
# In a new terminal
cd frontend
npm install
npm run dev
# Dashboard runs on http://localhost:5173
```

### 3. Run Evolution Cycle

```bash
# Using the API
curl -X POST http://localhost:8000/api/evolution/start \
  -H "Content-Type: application/json" \
  -d '{
    "target_path": "./my-project",
    "max_cycles": 1,
    "focus_areas": ["documentation", "complexity"],
    "dry_run": false
  }'

# Or using the Python script
python scripts/run_evolution.py --target ./my-project --cycles 1
```

### 4. Monitor Progress

The evolution cycle now runs in parallel phases:

1. **Phase 1: Parallel Research**
   - ResearchAgent: Searches external best practices
   - CodeAnalysisAgent: Analyzes your code for issues
   - Both results stored in SharedContextStore

2. **Phase 2: Context-Aware Planning**
   - PlannerAgent uses both external and internal analysis
   - Creates tasks based on actual code improvements needed
   - Stores plan in SharedContextStore

3. **Phase 3: Implementation**
   - RefactorAgent executes planned tasks
   - Uses AWS Bedrock, Black, autopep8, doq for modifications
   - Logs all changes to SharedContextStore

4. **Phase 4: Three-way Evaluation**
   - EvaluatorAgent compares: Before vs Plan vs After
   - Determines which goals were achieved
   - Stores comprehensive results

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
