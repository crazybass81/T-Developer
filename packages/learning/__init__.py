"""
T-Developer Learning System

This package implements continuous learning capabilities for T-Developer,
including pattern recognition, knowledge management, and intelligent recommendations.

The learning system consists of:
- Pattern Recognition: Extracts and matches patterns from successful operations
- Failure Analysis: Learns from failures to prevent recurrence
- Memory Curator: Manages persistent knowledge storage
- Knowledge Graph: Builds relationships between learned concepts
- Recommendation Engine: Provides intelligent suggestions
- Feedback Loop: Enables continuous improvement

Key Classes:
    PatternRecognizer: Extracts patterns from evolution cycles
    PatternDatabase: Stores and retrieves patterns efficiently
    FailureAnalyzer: Analyzes failures and creates prevention rules
    MemoryCurator: Manages learning memory storage
    KnowledgeGraph: Builds and queries knowledge relationships
    RecommendationEngine: Provides intelligent recommendations
    FeedbackLoop: Measures and improves learning effectiveness

Example:
    >>> from packages.learning import PatternRecognizer, MemoryCurator
    >>> recognizer = PatternRecognizer()
    >>> curator = MemoryCurator()
    >>>
    >>> # Extract patterns from successful cycle
    >>> patterns = await recognizer.extract_patterns(cycle_data)
    >>> await curator.store_patterns(patterns)
"""

from __future__ import annotations

__version__ = "1.0.0"
__author__ = "T-Developer System"

# Core components
from .failure_analyzer import FailureAnalyzer, FailurePattern
from .feedback_loop import FeedbackLoop, LearningMetrics
from .knowledge_graph import KnowledgeGraph, KnowledgeNode
from .memory_curator import Memory, MemoryCurator
from .pattern_database import Pattern, PatternDatabase
from .pattern_recognition import PatternRecognizer
from .recommendation_engine import Recommendation, RecommendationEngine

__all__ = [
    "PatternRecognizer",
    "PatternDatabase",
    "Pattern",
    "FailureAnalyzer",
    "FailurePattern",
    "MemoryCurator",
    "Memory",
    "KnowledgeGraph",
    "KnowledgeNode",
    "RecommendationEngine",
    "Recommendation",
    "FeedbackLoop",
    "LearningMetrics",
]
