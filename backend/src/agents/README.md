# T-Developer Agents Directory Structure

## 📁 Directory Organization

### `/framework/`
Core agent framework components and utilities:
- `core-agents.ts` - Factory for creating all 9 core agents
- `base-agent.ts` - Base agent class with common functionality
- `agent-manager.ts` - Agent lifecycle and orchestration
- `communication.ts` - Inter-agent communication layer
- `workflow.ts` - Workflow engine for agent coordination

### `/implementations/`
Specific implementations of the 9 core agents:
- `nl_input/` - Natural Language Input Agent
- `ui_selection/` - UI Framework Selection Agent  
- `parser/` - Code Parsing Agent
- `component_decision/` - Component Decision Agent
- `match_rate/` - Matching Rate Calculation Agent
- `search/` - Component Search Agent
- `generation/` - Code Generation Agent
- `assembly/` - Service Assembly Agent
- `download/` - Project Download Agent

### `/supervisor/`
Supervisor agent for orchestrating multi-agent workflows

### `/registry/`
Agent registry for discovery and management

### `/examples/`
Example agent implementations and usage patterns

## 🚀 Usage

```typescript
import { CoreAgentsFactory } from './framework';

// Create all agents
const agents = CoreAgentsFactory.createAllAgents();

// Use specific agent
const nlAgent = CoreAgentsFactory.createNLInputAgent();
```

## 📋 Agent Types

Each agent follows the T-Developer architecture pattern:
1. **Input Processing** - Validates and preprocesses input
2. **Core Logic** - Executes agent-specific functionality  
3. **Output Generation** - Formats and returns results
4. **Error Handling** - Manages failures gracefully
5. **Monitoring** - Tracks performance and usage