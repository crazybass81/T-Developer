"""Enterprise Base Agent"""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class AgentContext:
    """Context for enterprise agent execution"""

    pipeline_id: str
    request_id: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
