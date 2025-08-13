# T-Developer AI Autonomous Evolution System - Folder Structure

## 📁 Root Directory Structure

```
T-Developer-Evolution/
├── AI-DRIVEN-EVOLUTION.md       # 80-day implementation plan
├── .amazonq/                    # Architecture rules
│   └── rules/                   # System design rules
├── backend/                     # Python-only backend
├── docs/                        # System documentation
├── infrastructure/              # AWS infrastructure
├── scripts/                     # Deployment scripts
└── docker/                      # Container configs
```

## 🧬 Backend Structure (/backend)

```
backend/
├── src/
│   ├── agents/                  # Agent implementations
│   │   └── unified/             # Python agents
│   │       ├── nl_input/
│   │       ├── ui_selection/
│   │       ├── parser/
│   │       ├── component_decision/
│   │       ├── match_rate/
│   │       ├── search/
│   │       ├── generation/
│   │       ├── assembly/
│   │       └── download/
│   ├── evolution/               # Evolution system
│   │   ├── engine.py           # Genetic algorithm engine
│   │   ├── fitness.py          # Fitness evaluation
│   │   ├── mutation.py         # AI-guided mutation
│   │   └── selection.py        # Selection strategies
│   ├── security/               # Security frameworks
│   │   ├── evolution_safety.py # Evolution safety
│   │   ├── prompt_defender.py  # Prompt injection defense
│   │   └── pii_detector.py    # PII detection
│   ├── agno/                  # Agno Framework
│   ├── monitoring/            # Performance tracking
│   └── deployment/            # AgentCore deployment
├── tests/                     # Test suites (87% coverage)
│   ├── unit/
│   ├── integration/
│   ├── evolution/
│   └── security/
├── migrations/                # Database migrations
└── requirements.txt          # Python dependencies
```

## 📚 Documentation Structure (/docs)

```
docs/
├── security/                  # Security frameworks
│   ├── ai-security-framework.md
│   └── evolution-safety-framework.md
├── architecture/             # System architecture
│   └── performance-optimization-strategy.md
├── operations/              # Operations guides
│   ├── cost-management-strategy.md
│   └── sla-slo-definitions.md
├── deployment/              # Deployment guides
│   └── cicd-pipeline-strategy.md
└── development/            # Development guides
    └── comprehensive-test-strategy.md
```

## 🏗️ Infrastructure Structure (/infrastructure)

```
infrastructure/
├── aws/                    # AWS resources
│   ├── ecs/               # ECS Fargate configs
│   ├── bedrock/           # Bedrock AgentCore
│   └── cloudformation/    # IaC templates
├── terraform/             # Terraform configs
└── monitoring/           # Monitoring setup
```

## ⚠️ Important Rules

### Language Requirements
- **Backend**: Python 3.11+ ONLY
- **No Frontend**: System is backend-only
- **No TypeScript/JavaScript**: Removed entirely
- **Infrastructure**: Python/YAML/JSON only

### Agent Structure
- All agents in `/backend/src/agents/unified/`
- Each agent has its own module directory
- Memory constraint: < 6.5KB per agent
- Instantiation: < 3μs

### Evolution System
- Core engine in `/backend/src/evolution/`
- Safety checks mandatory
- Continuous validation required
- Genetic algorithms for improvement

### Security
- All AI outputs validated
- Evolution safety framework active
- PII detection automated
- 98/100 security score maintained

### Testing
- Minimum 85% code coverage
- Evolution-specific tests required
- Security validation tests mandatory
- Performance benchmarks continuous

---
**System**: AI Autonomous Evolution  
**Language**: Python Only  
**Updated**: November 2024