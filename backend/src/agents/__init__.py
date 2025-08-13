"""T-Developer Agents Package

This package contains all the AI agents for the T-Developer system.
Use the framework components for agent creation and management.
"""

# Import available components
try:
    from .framework.core.interfaces import IAgent, ICollaborativeAgent

    INTERFACES_AVAILABLE = True
except ImportError:
    INTERFACES_AVAILABLE = False
    IAgent = None
    ICollaborativeAgent = None

try:
    from .framework import AgentFactory as CoreAgentFactory

    FACTORY_AVAILABLE = True
except ImportError:
    FACTORY_AVAILABLE = False
    CoreAgentFactory = None

# Import production-ready base agent
try:
    from .ecs_integrated.base_agent import BaseAgent

    BASE_AGENT_AVAILABLE = True
except ImportError:
    BASE_AGENT_AVAILABLE = False
    BaseAgent = None

__all__ = [
    "CoreAgentFactory" if FACTORY_AVAILABLE else None,
    "BaseAgent" if BASE_AGENT_AVAILABLE else None,
    "IAgent" if INTERFACES_AVAILABLE else None,
    "ICollaborativeAgent" if INTERFACES_AVAILABLE else None,
]

# Remove None values
__all__ = [item for item in __all__ if item is not None]
