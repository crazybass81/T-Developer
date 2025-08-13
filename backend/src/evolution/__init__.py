"""
T-Developer Evolution Engine

AI Autonomous Evolution System with 85% autonomy level.
This module implements the core evolution mechanisms for self-improving agents.
"""

from .engine import EvolutionEngine
from .registry import AgentRegistry
from .safety import EvolutionSafety

__version__ = "5.0.0"
__all__ = ["EvolutionEngine", "EvolutionSafety", "AgentRegistry"]
