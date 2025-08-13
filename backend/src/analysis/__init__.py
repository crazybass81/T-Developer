"""
AI Analysis Engine Module
Day 7: AI Analysis Engine
Generated: 2024-11-18

AI-powered analysis system for agent code optimization and performance assessment
"""

from .ai_analysis_engine import (
    AIAnalysisEngine,
    ConsensusAnalyzer,
    OptimizationSuggester,
    PerformanceScorer,
)
from .analysis_history import AnalysisHistory, IssueTracker, PatternDetector, TrendAnalyzer
from .metrics import (
    AnalysisQualityChecker,
    ConsistencyChecker,
    FalsePositiveDetector,
    PerformanceMetrics,
)
from .model_integrations import (
    ClaudeAnalyzer,
    ConsensusModelAnalyzer,
    FallbackAnalyzer,
    OpenAIAnalyzer,
)
from .realtime_analyzer import AnalysisQueue, BatchAnalyzer, RealtimeAnalyzer, StreamingAnalyzer

__all__ = [
    # Core engine
    "AIAnalysisEngine",
    "PerformanceScorer",
    "OptimizationSuggester",
    "ConsensusAnalyzer",
    # History and patterns
    "AnalysisHistory",
    "IssueTracker",
    "PatternDetector",
    "TrendAnalyzer",
    # Real-time processing
    "RealtimeAnalyzer",
    "BatchAnalyzer",
    "AnalysisQueue",
    "StreamingAnalyzer",
    # Model integrations
    "ClaudeAnalyzer",
    "OpenAIAnalyzer",
    "FallbackAnalyzer",
    "ConsensusModelAnalyzer",
    # Quality metrics
    "AnalysisQualityChecker",
    "ConsistencyChecker",
    "FalsePositiveDetector",
    "PerformanceMetrics",
]

# Version info
__version__ = "1.0.0"
__author__ = "T-Developer AI Evolution System"
__description__ = "AI Analysis Engine for agent code optimization"
