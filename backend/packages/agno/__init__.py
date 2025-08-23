"""Agno - Agent Definition and Design Manager.

Agno is responsible for:
- Defining agent specifications from requirements
- Checking for duplicates (DD-Gate)
- Requesting implementation from Claude
- Validating and registering new agents

This is the core component that enables autonomous agent creation.
"""

from .spec import AgentSpec, AgentInputSchema, AgentOutputSchema, AgentPolicy
from .manager import AgnoManager
from .dedup import DeDupChecker

__all__ = [
    "AgnoManager",
    "AgentSpec",
    "AgentInputSchema",
    "AgentOutputSchema", 
    "AgentPolicy",
    "DeDupChecker",
]