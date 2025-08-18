"""T-Developer Agents Package - Organized by Function.

Structure:
- analysis_research/: All analysis and research agents (코드 분석 & 리서치)
- specification/: Requirements and specification agents
- generation/: Code and infrastructure generation agents
- modification/: Code refactoring and improvement agents
- orchestration/: Evaluation and coordination agents
- external/: External service integrations
"""

__version__ = "2.1.0"

# Base classes
# Analysis and Research agents
from .analysis_research import (
    CodeAnalysisAgent,
    EnhancedExternalResearchAgent,
    HybridContextAnalyzer,
    ReferenceLibrary,
)
from .base import AgentInput, AgentOutput, AgentStatus, Artifact, BaseAgent

# Generation agents (all code/config generation)
from .generation import BlueprintAgent, InfrastructureAgent, RefactorAgent, UnifiedAIService

# Orchestration agents
from .orchestration import EvaluatorAgent, ServiceCreatorAgent

# Planning agents (new specialized planners)
from .planning import (
    EvolutionPlannerAgent,
    GenerationPlannerAgent,
    MigrationPlannerAgent,
    RefactorPlannerAgent,
)

# Specification agents
from .specification import ServiceSpecification, SpecificationAgent

# External integrations (deprecated - use UnifiedAIService instead)

__all__ = [
    # Base
    "BaseAgent",
    "AgentInput",
    "AgentOutput",
    "AgentStatus",
    "Artifact",
    # Analysis
    "CodeAnalysisAgent",
    "HybridContextAnalyzer",
    # Research
    "EnhancedExternalResearchAgent",
    "ReferenceLibrary",
    # Specification
    "SpecificationAgent",
    "ServiceSpecification",
    # Generation (all code/config generation)
    "BlueprintAgent",
    "InfrastructureAgent",
    "RefactorAgent",
    "UnifiedAIService",
    # Planning (specialized planners)
    "GenerationPlannerAgent",
    "RefactorPlannerAgent",
    "MigrationPlannerAgent",
    "EvolutionPlannerAgent",
    # Orchestration
    "EvaluatorAgent",
    "ServiceCreatorAgent",
]
