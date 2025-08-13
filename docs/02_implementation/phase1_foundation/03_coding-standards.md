# Coding Standards

## Python Standards

### Code Style
- **Formatter**: Black
- **Linter**: Flake8
- **Type Checker**: MyPy
- **Import Sorting**: isort

### Naming Conventions
- **Functions**: snake_case
- **Classes**: PascalCase
- **Constants**: UPPER_SNAKE_CASE
- **Files**: snake_case.py

### Example
```python
from typing import Dict, List, Optional
import asyncio

class AgentManager:
    """Manages agent lifecycle and communication."""
    
    def __init__(self, config: Dict[str, Any]) -> None:
        self.config = config
        self._agents: List[Agent] = []
    
    async def create_agent(self, agent_type: str) -> Optional[Agent]:
        """Create and initialize a new agent."""
        try:
            agent = Agent(agent_type)
            await agent.initialize()
            self._agents.append(agent)
            return agent
        except Exception as e:
            logger.error(f"Failed to create agent: {e}")
            return None
```

## TypeScript Standards

### Code Style
- **Formatter**: Prettier
- **Linter**: ESLint
- **Style Guide**: Airbnb

### Naming Conventions
- **Variables**: camelCase
- **Functions**: camelCase
- **Classes**: PascalCase
- **Interfaces**: PascalCase (with I prefix)
- **Types**: PascalCase
- **Files**: kebab-case.ts

### Example
```typescript
interface IAgentConfig {
  name: string;
  type: AgentType;
  timeout: number;
}

class AgentManager {
  private agents: Map<string, Agent> = new Map();
  
  constructor(private config: IAgentConfig) {}
  
  async createAgent(type: AgentType): Promise<Agent | null> {
    try {
      const agent = new Agent(type);
      await agent.initialize();
      this.agents.set(agent.id, agent);
      return agent;
    } catch (error) {
      console.error('Failed to create agent:', error);
      return null;
    }
  }
}
```

## Documentation Standards

### Code Comments
- Use docstrings for all public functions/classes
- Explain WHY, not WHAT
- Include examples for complex functions

### Commit Messages
```
type(scope): description

feat(agents): add NL input processing
fix(parser): resolve AST parsing error
docs(readme): update installation guide
```

## Testing Standards

### Test Structure
```
tests/
├── unit/           # Unit tests
├── integration/    # Integration tests
└── e2e/           # End-to-end tests
```

### Test Naming
- `test_function_name_scenario`
- `test_agent_creation_success`
- `test_parser_invalid_input_error`
