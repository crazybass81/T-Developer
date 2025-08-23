"""Agents Package for T-Developer v2.

This package contains the agent system components:
- Base agent interface with AI capabilities
- Agent registry for managing agents
- Concrete agent implementations
"""

from .base import BaseAgent, AgentResult, AgentTask
from .registry import AgentRegistry
from .requirement_analyzer import RequirementAnalyzer
from .static_analyzer import StaticAnalyzer
from .code_analysis import CodeAnalysisAgent
from .behavior_analyzer import BehaviorAnalyzer
from .impact_analyzer import ImpactAnalyzer
from .quality_gate import QualityGate
from .external_researcher import ExternalResearcher
from .gap_analyzer import GapAnalyzer
from .system_architect import SystemArchitect
from .orchestrator_designer import OrchestratorDesigner
from .planner_agent import PlannerAgent
from .task_creator_agent import TaskCreatorAgent
from .code_generator import CodeGenerator
from .test_agent import TestAgent

__all__ = [
    "BaseAgent",
    "AgentResult", 
    "AgentTask",
    "AgentRegistry",
    "RequirementAnalyzer",
    "StaticAnalyzer",
    "CodeAnalysisAgent",
    "BehaviorAnalyzer",
    "ImpactAnalyzer",
    "QualityGate",
    "ExternalResearcher",
    "GapAnalyzer",
    "SystemArchitect",
    "OrchestratorDesigner",
    "PlannerAgent",
    "TaskCreatorAgent",
    "CodeGenerator",
    "TestAgent"
]