"""
T-Developer Orchestration Module

Provides orchestration capabilities for managing the 9 core agents
and Agent Squad integration.
"""

# from .agent_squad_core import AgentSquadOrchestrator, TaskStatus, AgentTask
# from .agent_orchestrator import AgentOrchestrator, ProjectRequest, ProjectResult

try:
    from .production_pipeline import ProductionECSPipeline, production_pipeline

    __all__ = ["ProductionECSPipeline", "production_pipeline"]
except ImportError as e:
    print(f"Production pipeline import failed: {e}")
    __all__ = []
