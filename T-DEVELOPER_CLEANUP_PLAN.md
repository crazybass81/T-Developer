# T-Developer Codebase Cleanup Plan

## 📋 Executive Summary

After analyzing the entire T-Developer codebase against the rule documents, significant gaps exist between the current implementation and the required architecture. This cleanup plan addresses critical issues and provides a roadmap for alignment.

## 🚨 Critical Issues Identified

### 1. **Architecture Misalignment**
- **Current**: Basic Express.js app with minimal agent implementation
- **Required**: Agno Framework + AWS Agent Squad + Bedrock AgentCore integration
- **Impact**: Core architecture doesn't match specifications

### 2. **Missing Core Dependencies**
- **Missing**: Agno framework integration (only basic Python files exist)
- **Missing**: AWS Agent Squad orchestration layer
- **Missing**: Bedrock AgentCore runtime configuration
- **Current**: Basic AWS SDK usage without proper integration

### 3. **Incomplete Agent Implementation**
- **Current**: 9 agents exist as basic Python/TypeScript files
- **Required**: Full Agno-based agents with 3μs instantiation, 6.5KB memory
- **Gap**: No proper agent framework, lifecycle management, or performance optimization

### 4. **Package.json Mismatch**
- **Current**: Basic Express dependencies
- **Required**: Agno, Agent Squad, AWS Bedrock SDK, multi-modal processing
- **Missing**: 80% of required dependencies

## 🎯 Cleanup Strategy

### Phase 1: Foundation Cleanup (Week 1-2)

#### 1.1 Remove Obsolete Code
```bash
# Files to remove
backend/src/app.ts                    # Basic Express app
backend/src/main.ts                   # Simple bootstrap
backend/src/server.ts                 # Redundant server file
frontend/                             # Premature frontend implementation
```

#### 1.2 Restructure Core Architecture
```bash
# New structure needed
backend/src/
├── agno/                            # Agno Framework integration
│   ├── agent-pool.ts               # 3μs instantiation pool
│   ├── performance-optimizer.ts    # Memory optimization
│   └── monitoring-integration.ts   # agno.com integration
├── agent-squad/                    # AWS Agent Squad layer
│   ├── orchestrator.ts            # Master orchestrator
│   ├── supervisor-agent.ts        # SupervisorAgent
│   └── task-routing.ts            # Intelligent routing
├── bedrock/                        # Bedrock AgentCore
│   ├── agentcore-runtime.ts       # 8-hour sessions
│   ├── model-integration.ts       # Claude/GPT integration
│   └── scaling-manager.ts         # Auto-scaling
└── agents/                         # 9 Core Agents
    ├── nl-input/                   # NL Input Agent
    ├── ui-selection/               # UI Selection Agent
    ├── parser/                     # Parser Agent
    ├── component-decision/         # Component Decision Agent
    ├── match-rate/                 # Match Rate Agent
    ├── search/                     # Search Agent
    ├── generation/                 # Generation Agent
    ├── assembly/                   # Assembly Agent
    └── download/                   # Download Agent
```

### Phase 2: Dependency Alignment (Week 2-3)

#### 2.1 Update package.json
```json
{
  "dependencies": {
    "agno": "latest",
    "agent-squad": "latest",
    "@aws-sdk/client-bedrock": "^3.0.0",
    "@aws-sdk/client-bedrock-runtime": "^3.0.0",
    "@aws-sdk/client-bedrock-agent": "^3.0.0",
    "@aws-sdk/client-dynamodb": "^3.0.0",
    "@aws-sdk/lib-dynamodb": "^3.0.0",
    "sentence-transformers": "^1.0.0",
    "spacy": "^3.0.0",
    "transformers": "^4.0.0"
  }
}
```

#### 2.2 Python Requirements Cleanup
```txt
# Remove current basic requirements
# Add required packages:
agno>=1.0.0
agent-squad>=1.0.0
boto3>=1.26.0
transformers>=4.21.0
sentence-transformers>=2.2.0
spacy>=3.4.0
torch>=1.12.0
numpy>=1.21.0
pandas>=1.5.0
scikit-learn>=1.1.0
```

### Phase 3: Agent Implementation Cleanup (Week 3-6)

#### 3.1 NL Input Agent Refactor
**Current Issues:**
- Basic Python class without Agno integration
- Missing multimodal processing
- No performance optimization

**Required Changes:**
```python
# Remove: backend/src/agents/implementations/nl_input_agent.py
# Replace with: backend/src/agents/nl-input/agno-nl-agent.py

from agno.agent import Agent
from agno.models.aws import AwsBedrock
from agno.memory import ConversationSummaryMemory
from agno.tools import ImageAnalyzer, PDFExtractor

class NLInputAgent:
    def __init__(self):
        self.agent = Agent(
            name="NL-Input-Processor",
            model=AwsBedrock(id="anthropic.claude-3-sonnet-v2:0"),
            memory=ConversationSummaryMemory(
                storage_type="dynamodb",
                table_name="t-dev-nl-conversations"
            ),
            tools=[
                ImageAnalyzer(),
                PDFExtractor(),
                DiagramInterpreter()
            ],
            performance_target={
                "instantiation_time_us": 3,
                "memory_limit_kb": 6.5
            }
        )
```

#### 3.2 Parser Agent Refactor
**Current Issues:**
- Incomplete implementation
- Missing NLP pipeline
- No rule engine

**Required Changes:**
```python
# Implement missing components:
backend/src/agents/parser/
├── nlp-pipeline.py          # SpaCy + Transformers
├── parsing-rules.py         # Rule engine
├── requirement-classifier.py # ML classification
└── dependency-analyzer.py   # Dependency graph
```

#### 3.3 All Agents Performance Alignment
**Current**: No performance optimization
**Required**: 3μs instantiation, 6.5KB memory per agent

```typescript
// Add to all agents
interface AgentPerformanceConfig {
  instantiation_target_us: 3;
  memory_target_kb: 6.5;
  enable_optimizations: true;
  use_native_extensions: true;
}
```

### Phase 4: Integration Layer Cleanup (Week 6-8)

#### 4.1 AWS Agent Squad Integration
**Current**: Missing orchestration layer
**Required**: Full SupervisorAgent implementation

```typescript
// Add: backend/src/agent-squad/supervisor-agent.ts
import { SupervisorAgent } from 'agent-squad';

export class TDeveloperSupervisor extends SupervisorAgent {
  constructor() {
    super({
      name: "T-Developer-Master",
      agents: [
        new NLInputAgent(),
        new UISelectionAgent(),
        new ParserAgent(),
        // ... all 9 agents
      ],
      orchestration_strategy: "intelligent_routing",
      max_concurrent: 50
    });
  }
}
```

#### 4.2 Bedrock AgentCore Runtime
**Current**: Basic AWS SDK calls
**Required**: Full AgentCore integration

```typescript
// Add: backend/src/bedrock/agentcore-runtime.ts
import { BedrockAgentCoreClient } from '@aws-sdk/client-bedrock-agent';

export class AgentCoreRuntime {
  private client: BedrockAgentCoreClient;
  
  async createRuntime() {
    return await this.client.createAgentRuntime({
      runtimeName: "t-developer-runtime",
      sessionDuration: 28800, // 8 hours
      autoScaling: true,
      memoryConfiguration: {
        maxMemoryMB: 8192
      }
    });
  }
}
```

### Phase 5: Testing Infrastructure Cleanup (Week 8-10)

#### 5.1 Remove Inadequate Tests
```bash
# Remove basic tests that don't match architecture
rm -rf backend/tests/unit/
rm -rf backend/tests/integration/
```

#### 5.2 Add Performance Tests
```typescript
// Add: backend/tests/performance/agent-instantiation.test.ts
describe('Agent Performance', () => {
  test('Agent instantiation under 3μs', async () => {
    const start = performance.now();
    const agent = new NLInputAgent();
    const duration = (performance.now() - start) * 1000; // Convert to μs
    
    expect(duration).toBeLessThan(3);
  });
  
  test('Agent memory under 6.5KB', async () => {
    const agent = new NLInputAgent();
    const memoryUsage = process.memoryUsage().heapUsed;
    
    expect(memoryUsage / 1024).toBeLessThan(6.5);
  });
});
```

## 🗂️ File-by-File Cleanup Actions

### Files to DELETE
```bash
# Obsolete implementations
backend/src/app.ts
backend/src/main.ts
backend/src/server.ts
frontend/                           # Premature implementation
backend/src/agents/base-agent.ts    # Wrong base class
backend/src/agents/core-agents.ts   # Incomplete implementation

# Redundant files
backend/src/agents/implementations/example-agent.ts
backend/src/agents/examples/
backend/src/framework/base-agent.ts
```

### Files to REFACTOR
```bash
# Major refactoring needed
backend/src/agents/implementations/nl_input_agent.py     → backend/src/agents/nl-input/
backend/src/agents/implementations/parser_agent.py      → backend/src/agents/parser/
backend/src/agents/implementations/ui_selection_agent.py → backend/src/agents/ui-selection/
backend/package.json                                     → Add 50+ missing dependencies
backend/requirements.txt                                 → Complete rewrite
```

### Files to CREATE
```bash
# Core architecture files
backend/src/agno/agent-pool.ts
backend/src/agno/performance-optimizer.ts
backend/src/agent-squad/orchestrator.ts
backend/src/bedrock/agentcore-runtime.ts

# Agent implementations (9 agents × 4 files each = 36 files)
backend/src/agents/*/agent.py
backend/src/agents/*/performance.ts
backend/src/agents/*/tests.py
backend/src/agents/*/integration.ts

# Infrastructure
backend/src/infrastructure/monitoring.ts
backend/src/infrastructure/scaling.ts
backend/src/infrastructure/session-management.ts
```

## 📊 Cleanup Metrics

### Before Cleanup
- **Architecture Alignment**: 15%
- **Dependency Completeness**: 20%
- **Agent Implementation**: 30%
- **Performance Compliance**: 0%
- **Test Coverage**: 25%

### After Cleanup Target
- **Architecture Alignment**: 95%
- **Dependency Completeness**: 100%
- **Agent Implementation**: 90%
- **Performance Compliance**: 95%
- **Test Coverage**: 85%

## 🚀 Implementation Priority

### Critical (Must Fix First)
1. **Package Dependencies** - Add Agno, Agent Squad, Bedrock SDK
2. **Core Architecture** - Implement proper agent framework
3. **Agent Performance** - Achieve 3μs/6.5KB targets

### High Priority
1. **9 Agent Implementations** - Complete all agent functionality
2. **Integration Layer** - AWS Agent Squad + Bedrock AgentCore
3. **Testing Infrastructure** - Performance and integration tests

### Medium Priority
1. **Documentation Updates** - Align with new architecture
2. **CI/CD Pipeline** - Update for new structure
3. **Monitoring Integration** - agno.com dashboard

### Low Priority
1. **Frontend Implementation** - Defer until backend complete
2. **Advanced Features** - Focus on core functionality first
3. **Optimization** - After basic functionality works

## 🎯 Success Criteria

### Technical Metrics
- [ ] All 9 agents instantiate in <3μs
- [ ] Memory usage <6.5KB per agent
- [ ] 10,000 concurrent agents supported
- [ ] 8-hour session runtime achieved
- [ ] Integration tests pass at 95%

### Architecture Compliance
- [ ] Agno Framework fully integrated
- [ ] AWS Agent Squad orchestration working
- [ ] Bedrock AgentCore runtime operational
- [ ] All dependencies properly configured
- [ ] Performance targets met

### Code Quality
- [ ] No obsolete code remaining
- [ ] All files follow naming conventions
- [ ] Test coverage >85%
- [ ] Documentation updated
- [ ] CI/CD pipeline functional

## 📅 Timeline

| Week | Focus | Deliverables |
|------|-------|-------------|
| 1-2 | Foundation Cleanup | Remove obsolete code, restructure |
| 2-3 | Dependency Alignment | Update package.json, requirements.txt |
| 3-6 | Agent Implementation | Refactor all 9 agents |
| 6-8 | Integration Layer | Agent Squad + Bedrock integration |
| 8-10 | Testing & Validation | Performance tests, integration tests |

## 🔧 Execution Commands

### Phase 1: Cleanup
```bash
# Remove obsolete files
rm -rf frontend/
rm backend/src/app.ts backend/src/main.ts backend/src/server.ts
rm -rf backend/src/agents/examples/

# Create new structure
mkdir -p backend/src/{agno,agent-squad,bedrock}
mkdir -p backend/src/agents/{nl-input,ui-selection,parser,component-decision,match-rate,search,generation,assembly,download}
```

### Phase 2: Dependencies
```bash
# Update Node.js dependencies
npm install agno agent-squad @aws-sdk/client-bedrock @aws-sdk/client-bedrock-runtime

# Update Python dependencies
pip install agno agent-squad boto3 transformers sentence-transformers spacy
```

### Phase 3: Implementation
```bash
# Generate agent templates
for agent in nl-input ui-selection parser component-decision match-rate search generation assembly download; do
  mkdir -p backend/src/agents/$agent
  touch backend/src/agents/$agent/{agent.py,performance.ts,tests.py,integration.ts}
done
```

This cleanup plan provides a comprehensive roadmap to align the T-Developer codebase with the architectural requirements specified in the rule documents.