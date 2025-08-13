"""
Data wrapper classes for unified agents
Provides compatibility between production pipeline and unified agents
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
import time


@dataclass
class AgentContext:
    """Context for agent execution"""

    pipeline_id: str = ""
    trace_id: str = ""
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    start_time: float = None
    timestamp: Optional[str] = None
    project_id: Optional[str] = None

    def __post_init__(self):
        if not self.pipeline_id:
            self.pipeline_id = f"pipeline_{int(time.time())}"
        if not self.trace_id:
            self.trace_id = f"trace_{int(time.time())}"
        if self.start_time is None:
            self.start_time = time.time()


@dataclass
class AgentInput:
    """Wrapper for agent input data"""

    data: Dict[str, Any]
    context: AgentContext = None

    def __post_init__(self):
        if self.context is None:
            self.context = AgentContext()

    def get(self, key: str, default=None):
        """Get value from data dict"""
        return self.data.get(key, default)


def wrap_input(
    data: Dict[str, Any], context: Optional[AgentContext] = None
) -> AgentInput:
    """
    Wrap raw dict data into AgentInput format

    Args:
        data: Raw input dictionary
        context: Optional context object

    Returns:
        AgentInput object that unified agents expect
    """
    if isinstance(data, AgentInput):
        return data

    if context is None:
        context = AgentContext()

    return AgentInput(data=data, context=context)


def unwrap_result(result: Any) -> Dict[str, Any]:
    """
    Unwrap agent result to raw dict

    Args:
        result: Agent result object

    Returns:
        Raw dictionary data
    """
    if hasattr(result, "data"):
        return result.data
    elif hasattr(result, "__dict__"):
        return result.__dict__
    elif isinstance(result, dict):
        return result
    else:
        return {"result": result}
