"""
Component Decision Agent Production Implementation
Phase 4 Tasks 4.31-4.40 완전 구현
"""

from .core import (
    ComponentDecisionAgent,
    TechnologyStack,
    ComponentOption,
    ComponentDecision,
    DecisionMatrix,
    ComponentType,
    ComponentCategory,
    DecisionCriteria
)
from .criteria_evaluator import CriteriaEvaluator
from .mcdm_analyzer import MCDMAnalyzer
from .compatibility_checker import CompatibilityChecker
from .performance_predictor import PerformancePredictor
from .cost_estimator import CostEstimator
from .risk_assessor import RiskAssessor
from .migration_planner import MigrationPlanner
from .stack_optimizer import StackOptimizer
from .decision_validator import DecisionValidator
from .documentation_generator import DocumentationGenerator

__all__ = [
    'ComponentDecisionAgent',
    'TechnologyStack',
    'ComponentOption',
    'ComponentDecision',
    'DecisionMatrix',
    'ComponentType',
    'ComponentCategory',
    'DecisionCriteria',
    'CriteriaEvaluator',
    'MCDMAnalyzer',
    'CompatibilityChecker',
    'PerformancePredictor',
    'CostEstimator',
    'RiskAssessor',
    'MigrationPlanner',
    'StackOptimizer',
    'DecisionValidator',
    'DocumentationGenerator'
]

# 버전 정보
__version__ = '1.0.0'