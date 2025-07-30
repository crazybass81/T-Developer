# T-Developer

AI-powered multi-agent development platform using **Agno Framework** + **AWS Agent Squad** + **Bedrock AgentCore**.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  T-Developer Web Interface                    │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│            AWS Agent Squad Orchestration Layer               │
│    - Master Supervisor Agent (Project Manager)               │
│    - Intelligent Task Routing & Delegation                   │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│              Agno Framework - Ultra High Performance         │
│    - 3μs Agent Instantiation                                 │
│    - 6.5KB Memory per Agent                                  │
│    - 9 Specialized T-Developer Agents                        │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│          AWS Bedrock AgentCore Runtime Layer                │
│    - Enterprise Runtime Environment                          │
│    - 8-hour Session Support                                  │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Getting Started

### Prerequisites
- Node.js 18+
- Python 3.9+
- AWS Account with Bedrock access
- Docker

### Installation
```bash
# Clone repository
git clone https://github.com/crazybass81/T-DeveloperMVP.git
cd T-DeveloperMVP

# Install Agno Framework (Open Source)
pip install agno

# Install Agent Squad (Open Source)  
npm install agent-squad

# Install dependencies
cd backend && npm install
```

### Configuration
```bash
# Copy environment template
cp .env.example .env

# Configure AWS credentials and Bedrock access
# Note: Agno and Agent Squad are open source - no API keys needed
```

## 🤖 9 Core Agents

1. **NL Input Agent** - Natural language processing
2. **UI Selection Agent** - Interface framework selection  
3. **Parsing Agent** - Code analysis and parsing
4. **Component Decision Agent** - Architecture decisions
5. **Matching Rate Agent** - Component compatibility scoring
6. **Search Agent** - Component discovery
7. **Generation Agent** - Code generation
8. **Assembly Agent** - Service integration
9. **Download Agent** - Project packaging

## 📊 Performance

- **Agent Instantiation**: ~3μs (Agno Framework)
- **Memory Usage**: 6.5KB per agent
- **Concurrent Agents**: Up to 10,000
- **Session Runtime**: 8 hours (Bedrock AgentCore)

## 📚 Documentation
- [Architecture](./docs/architecture.md)
- [API Reference](./docs/api.md)
- [Agent Guide](./docs/agents.md)