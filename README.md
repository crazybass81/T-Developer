# 🚀 T-Developer v2: Self-Evolving Service-as-Code Factory

[![Phase](https://img.shields.io/badge/Phase-6%20Complete-success)](docs/00_planning/PROJECT_STATUS.md)
[![Coverage](https://img.shields.io/badge/Coverage-85%25+-brightgreen)](tests/)
[![Agents](https://img.shields.io/badge/Agents-11-blue)](packages/agents/)
[![Templates](https://img.shields.io/badge/Templates-6-purple)](blueprints/)

## 🎯 Vision

**"A system that creates services from requirements and evolves itself to create better services over time"**

T-Developer v2 is an autonomous development system that:

- 🤖 Takes natural language requirements → Produces production-ready services
- 🔄 Continuously improves its own code and capabilities
- 📈 Learns from every cycle to become more efficient
- 🚀 Operates with minimal human intervention

## 📊 Current Status

**Phase 6 Complete** - 75% Overall Progress

| Component | Status | Coverage |
|-----------|--------|----------|
| Core Agents | ✅ Complete | 85%+ |
| Quality Gates | ✅ Complete | 85%+ |
| Service Creation | ✅ Complete | 85%+ |
| Performance & Reliability | ✅ Complete | 85%+ |
| Learning System | 🔜 Next | - |
| Production Deployment | 📅 Future | - |

[📋 Full Status Dashboard →](docs/00_planning/PROJECT_STATUS.md)

## 🏗️ Architecture

```
Requirements → SpecAgent → BlueprintAgent → InfrastructureAgent → ServiceCreator
                   ↓            ↓                 ↓                     ↓
              OpenAPI Spec  Code Scaffold    IaC Generated      Deployed Service
                                                                        ↓
                                                              Performance & Monitoring
```

### Core Components

#### 🤖 Intelligent Agents

- **ResearchAgent**: Analyzes codebase and identifies improvements
- **PlannerAgent**: Creates HTN-based execution plans
- **RefactorAgent**: Generates and modifies code
- **EvaluatorAgent**: Validates quality and metrics

#### 🛡️ Quality Gates

- **SecurityGate**: Vulnerability scanning and remediation
- **QualityGate**: Code metrics and standards enforcement
- **TestGate**: Coverage and mutation testing

#### 🏭 Service Creation

- **SpecificationAgent**: Requirements → OpenAPI specifications
- **BlueprintAgent**: Template-based code generation
- **InfrastructureAgent**: IaC generation (Terraform/CDK)
- **ServiceCreator**: End-to-end orchestration

#### ⚡ Performance & Reliability

- **Performance Profiler**: Bottleneck analysis
- **Auto-Optimizer**: Code optimization
- **Load Testing**: k6 integration
- **Chaos Engineering**: Failure injection
- **Monitoring**: Real-time metrics

## 🚀 Quick Start

### Prerequisites

```bash
# Python 3.9+
python --version

# AWS CLI configured
aws configure

# Node.js for k6 (optional)
node --version
```

### Installation

```bash
# Clone repository
git clone https://github.com/your-org/T-DeveloperMVP.git
cd T-DeveloperMVP

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e .
pip install -r requirements.txt

# Run tests
pytest tests/ -v
```

### Basic Usage

#### 1. Generate a Service from Requirements

```python
from packages.agents.service_creator import ServiceCreator

creator = ServiceCreator()
result = await creator.execute({
    "intent": "create_service",
    "requirements": "I need a REST API for user management with CRUD operations",
    "blueprint": "rest-api",
    "name": "user-service"
})
```

#### 2. Run Self-Evolution Cycle

```python
from packages.runtime.orchestrator import EvolutionOrchestrator

orchestrator = EvolutionOrchestrator()
result = await orchestrator.run_evolution_cycle(
    goal="Improve code documentation coverage to 90%"
)
```

#### 3. Perform Security Scan

```python
from packages.evaluation.security_gate import SecurityGate

gate = SecurityGate()
result = gate.scan_codebase("./packages")
print(f"Security Score: {result.score}/100")
```

## 📦 Available Blueprint Templates

| Template | Description | Use Case |
|----------|-------------|----------|
| `rest-api` | RESTful API with database | CRUD applications |
| `microservice` | Event-driven microservice | Distributed systems |
| `web-app` | Full-stack web application | User-facing apps |
| `cli-tool` | Command-line interface | Developer tools |
| `serverless-function` | Cloud functions | Event processing |
| `data-pipeline` | ETL/ELT pipeline | Data processing |

## 📈 Key Metrics

### Quality Standards

- **Test Coverage**: ≥85%
- **Docstring Coverage**: ≥80%
- **Code Complexity**: MI ≥65
- **Security**: 0 critical/high issues

### Performance Targets

- **P95 Latency**: <200ms
- **Availability**: 99.9%
- **Throughput**: >100 RPS
- **Cache Hit Rate**: >70%

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=packages --cov-report=html

# Run specific test suite
pytest tests/test_agents.py -v

# Run performance tests
python -m packages.performance.benchmarks

# Run load tests
k6 run config/k6-scripts/load-test.js
```

## 📚 Documentation

- [📋 Project Status](docs/00_planning/PROJECT_STATUS.md)
- [🗺️ Master Plan](MASTER_PLAN.md)
- [🤖 AI Guidelines](CLAUDE.md)
- [🏗️ System Architecture](docs/architecture/SYSTEM_DESIGN.md)
- [📖 API Reference](docs/reference/API_REFERENCE.md)
- [🚀 Quick Start Guide](docs/implementation/QUICK_START.md)

## 🔄 Development Workflow

### 1. Evolution Cycle

```
Research → Plan → Code → Evaluate → Gate → Merge → Learn
```

### 2. Git Workflow

```bash
# Feature branch
git checkout -b feature/phase-X-description

# Auto-evolution branch
git checkout -b tdev/auto/YYYYMMDD-improvement

# Commit with metrics
git commit -m "feat(agents): improve docstring coverage

Metrics-Impact:
- Docstring: 75% → 85% (+10%)
- Coverage: 80% → 82% (+2%)"
```

### 3. Quality Gates

All PRs must pass:

- ✅ Security scan (0 critical/high)
- ✅ Test coverage (≥85%)
- ✅ Code quality (MI ≥65)
- ✅ Performance tests
- ✅ Documentation updated

## 🛠️ Configuration

### Environment Variables

```bash
# .env file
AWS_REGION=us-east-1
BEDROCK_ENDPOINT=https://bedrock.us-east-1.amazonaws.com
CLAUDE_API_KEY=your-api-key
LOG_LEVEL=INFO
ENVIRONMENT=development
```

### SLO Configuration

```yaml
# config/slo-definitions.yaml
availability:
  target: 99.9
  window: 30d

latency:
  p95: 200ms
  p99: 500ms

error_rate:
  target: 1%
```

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run pre-commit hooks
pre-commit install

# Run linting
ruff check packages/

# Run type checking
mypy packages/
```

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- AWS Bedrock Team for AgentCore platform
- Claude (Anthropic) for AI assistance
- Open source community for amazing tools

## 📞 Support

- 📧 Email: <support@t-developer.ai>
- 💬 Slack: [t-developer.slack.com](https://t-developer.slack.com)
- 🐛 Issues: [GitHub Issues](https://github.com/your-org/T-DeveloperMVP/issues)

---

**Built with ❤️ by T-Developer Team**

*"Evolving software development, one cycle at a time"* 🔄
