"""Mini Base Agent - Lightweight base class for 6.5KB constraint"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class B(ABC):
    """Ultra-lightweight base class (B for Base)"""

    def __init__(self, c: Dict[str, Any] = None):
        """Initialize with config (c)"""
        self.c = c or {}

    @abstractmethod
    def p(self, i: Any) -> Dict[str, Any]:
        """Process input (p for process, i for input)"""
        pass

    def v(self, i: Any) -> bool:
        """Validate input (v for validate)"""
        return i is not None
