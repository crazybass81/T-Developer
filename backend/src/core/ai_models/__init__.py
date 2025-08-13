"""
AI Models Integration Module
"""

from .base_model import BaseAIModel
from .claude_model import Claude3Opus
from .gpt_model import GPT4Turbo

__all__ = ["Claude3Opus", "GPT4Turbo", "BaseAIModel"]
