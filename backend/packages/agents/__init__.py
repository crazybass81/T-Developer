"""Agents Package for T-Developer v2.

This package contains the agent system components:
- Base agent interface with AI capabilities
- Agent registry for managing agents
- Concrete agent implementations
"""

from .base import BaseAgent, AgentResult, AgentTask
from .registry import AgentRegistry

__all__ = [
    "BaseAgent",
    "AgentResult", 
    "AgentTask",
    "AgentRegistry",
]