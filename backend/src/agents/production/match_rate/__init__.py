"""
Match Rate Agent Production Implementation
Phase 4 Tasks 4.41-4.50 완전 구현
"""

from .core import (
    MatchRateAgent,
    MatchingResult,
    ComponentMatch,
    TemplateMatch,
    SimilarityMetrics,
    OptimizationRecommendation,
    MatchType,
    MatchingStrategy
)

__all__ = [
    'MatchRateAgent',
    'MatchingResult',
    'ComponentMatch',
    'TemplateMatch',
    'SimilarityMetrics',
    'OptimizationRecommendation',
    'MatchType',
    'MatchingStrategy'
]

# 버전 정보
__version__ = '1.0.0'