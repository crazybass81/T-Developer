# Agent Base Classes

## Overview
T-Developer의 모든 에이전트는 공통 베이스 클래스를 상속받아 일관된 인터페이스와 동작을 보장합니다.

## Base Agent Architecture

### BaseAgent Class
```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from agno.agent import Agent

class BaseAgent(ABC):
    """모든 T-Developer 에이전트의 베이스 클래스"""
    
    def __init__(self, config: Dict[str, Any]):
        self.agent_id = str(uuid.uuid4())
        self.config = config
        self.status = AgentStatus.IDLE
        
    @abstractmethod
    async def initialize(self) -> None:
        """에이전트 초기화"""
        pass
        
    @abstractmethod
    async def execute(self, input_data: Any) -> Any:
        """에이전트 실행"""
        pass
        
    @abstractmethod
    async def cleanup(self) -> None:
        """리소스 정리"""
        pass
```

## Agent Types

### Processing Agents
- **NL Input Agent**: 자연어 처리
- **Parser Agent**: 코드 파싱
- **Generation Agent**: 코드 생성

### Decision Agents
- **UI Selection Agent**: UI 프레임워크 선택
- **Component Decision Agent**: 컴포넌트 결정
- **Match Rate Agent**: 매칭률 계산

### Integration Agents
- **Search Agent**: 컴포넌트 검색
- **Assembly Agent**: 서비스 조립
- **Download Agent**: 프로젝트 패키징

## Common Features

### State Management
- Agent status tracking
- Context preservation
- Error state handling

### Communication
- Event-based messaging
- Async/await patterns
- Error propagation

### Performance
- 3μs instantiation (Agno Framework)
- 6.5KB memory per agent
- Concurrent execution support

## Usage Example

```python
from agents.nl_input_agent import NLInputAgent

# Initialize agent
agent = NLInputAgent(config={
    'model': 'claude-3-sonnet',
    'temperature': 0.2
})

# Execute processing
result = await agent.execute({
    'description': 'Build a React todo app'
})
```