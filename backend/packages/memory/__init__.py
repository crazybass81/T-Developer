"""Memory Hub Package.

Manages 5 types of contexts for the T-Developer system:
- O_CTX: Orchestrator context (decisions, gates)
- A_CTX: Agent context (personal history, cache)
- S_CTX: Shared context (current work state)
- U_CTX: User context (team/user preferences)
- OBS_CTX: Observer context (metrics, anomalies)
"""

from .contexts import ContextType, MemoryContext
from .hub import MemoryHub
from .storage import MemoryStorage, JSONMemoryStorage

__all__ = [
    "ContextType",
    "MemoryContext",
    "MemoryHub",
    "MemoryStorage",
    "JSONMemoryStorage",
]