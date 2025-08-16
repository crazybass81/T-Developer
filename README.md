# T-Developer v2: Self-Evolving Service Factory

## 🎯 Vision
A service that creates and evolves services autonomously using AI agents.

## 🏗️ Architecture

### Core Components
- **Agents**: 4 core AI agents (Research, Planner, Refactor, Evaluator)
- **MCP**: Model Context Protocol for tool integration
- **Orchestrator**: AWS Agent Squad for multi-agent coordination
- **Runtime**: Bedrock AgentCore for production deployment

### Tech Stack
- **AI**: Claude Code + Bedrock Claude 3.5
- **Orchestration**: AWS Agent Squad
- **Runtime**: Bedrock AgentCore
- **Tools**: MCP (filesystem, git, github, browser)
- **Extension**: A2A Protocol for external agents

## 📁 Project Structure
```
packages/
├── agents/         # Core AI agents
├── mcp/           # MCP server configurations
├── orchestrator/  # AWS Agent Squad integration
├── runtime/       # Bedrock AgentCore wrapper
├── evaluation/    # Quality gates and metrics
└── sandbox/       # Safe execution environment
```

## 🚀 Quick Start

### Prerequisites
```bash
# Install Claude Code CLI
npm install -g @anthropic/claude-code

# Install AWS CLI and configure
aws configure

# Install Python dependencies
pip install uv
uv pip install -r requirements.txt
```

### Running Self-Evolution
```bash
# Initialize the system
python scripts/init_evolution.py

# Start self-evolution loop
python scripts/run_evolution.py --target ./packages/agents --cycles 1
```

## 📋 Roadmap

### Phase 1: Foundation (Week 1)
- [ ] Setup MCP servers
- [ ] Implement 4 core agents
- [ ] Basic orchestration

### Phase 2: Integration (Week 2)
- [ ] AWS Agent Squad setup
- [ ] Bedrock AgentCore deployment
- [ ] Claude Code integration

### Phase 3: Evolution (Week 3)
- [ ] Self-improvement loop
- [ ] Automated PR generation
- [ ] Quality gates

### Phase 4: Service Creation (Week 4)
- [ ] Service blueprint templates
- [ ] Infrastructure as Code
- [ ] End-to-end automation

## 📚 Documentation
See [docs/NEWVERSION/](docs/NEWVERSION/) for detailed architecture and implementation plans.

## 🤝 Contributing
This is a self-evolving system. The system improves itself through automated PRs.

## 📄 License
MIT