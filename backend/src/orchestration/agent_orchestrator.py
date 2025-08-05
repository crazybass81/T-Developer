"""
T-Developer Agent Orchestrator

Manages the execution of 9 core agents in proper sequence for project generation.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import asyncio
import time
import logging
from enum import Enum

from .agent_squad_core import AgentSquadOrchestrator, TaskStatus
from ..agents.framework.base_agent import BaseAgent
from ..agents.framework.agent_types import AgentType

logger = logging.getLogger(__name__)

@dataclass
class ProjectRequest:
    id: str
    description: str
    requirements: Optional[List[str]] = None
    existing_code: Optional[str] = None
    language: Optional[str] = None
    output_format: Optional[str] = 'zip'
    start_time: float = None

    def __post_init__(self):
        if self.start_time is None:
            self.start_time = time.time()

@dataclass
class ProjectResult:
    success: bool
    project_id: str
    download_url: Optional[str] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class AgentOrchestrator:
    """Main orchestrator for T-Developer's 9 core agents"""

    def __init__(self):
        self.agent_squad = AgentSquadOrchestrator()
        self.agents: Dict[str, BaseAgent] = {}
        self.agent_execution_order = [
            AgentType.NL_INPUT,
            AgentType.UI_SELECTION,
            AgentType.PARSER,
            AgentType.COMPONENT_DECISION,
            AgentType.MATCH_RATE,
            AgentType.SEARCH,
            AgentType.GENERATION,
            AgentType.ASSEMBLY,
            AgentType.DOWNLOAD
        ]

    async def initialize(self) -> None:
        """Initialize the orchestrator and all agents"""
        logger.info("Initializing Agent Orchestrator...")

        # Initialize Agent Squad
        await self.agent_squad.initialize()

        # Initialize 9 core agents
        await self._initialize_agents()

        logger.info("Agent Orchestrator initialized successfully")

    async def _initialize_agents(self) -> None:
        """Initialize all 9 core agents"""
        from ..agents.implementations.nl_input_agent import NLInputAgent
        from ..agents.implementations.ui_selection_agent import UISelectionAgent
        from ..agents.implementations.parser_agent import ParserAgent
        from ..agents.implementations.component_decision_agent import ComponentDecisionAgent
        from ..agents.implementations.match_rate_agent import MatchRateAgent
        from ..agents.implementations.search_agent import SearchAgent
        from ..agents.implementations.generation_agent import GenerationAgent
        from ..agents.implementations.assembly_agent import AssemblyAgent
        from ..agents.implementations.download_agent import DownloadAgent

        agent_classes = {
            AgentType.NL_INPUT: NLInputAgent,
            AgentType.UI_SELECTION: UISelectionAgent,
            AgentType.PARSER: ParserAgent,
            AgentType.COMPONENT_DECISION: ComponentDecisionAgent,
            AgentType.MATCH_RATE: MatchRateAgent,
            AgentType.SEARCH: SearchAgent,
            AgentType.GENERATION: GenerationAgent,
            AgentType.ASSEMBLY: AssemblyAgent,
            AgentType.DOWNLOAD: DownloadAgent
        }

        for agent_type in self.agent_execution_order:
            try:
                agent_class = agent_classes[agent_type]
                agent = agent_class()
                await agent.initialize()
                
                self.agents[agent_type.value] = agent
                await self.agent_squad.register_agent(agent)
                
                logger.info(f"Initialized {agent_type.value} agent")
            except Exception as error:
                logger.error(f"Failed to initialize {agent_type.value} agent: {error}")
                raise error

    async def process_project(self, project_request: ProjectRequest) -> ProjectResult:
        """Process a complete project through all 9 agents"""
        logger.info(f"Processing project request: {project_request.id}")

        try:
            # Step 1: Natural Language Processing
            nl_result = await self._execute_agent('nl-input', {
                'description': project_request.description,
                'requirements': project_request.requirements
            })

            # Step 2: UI Framework Selection
            ui_result = await self._execute_agent('ui-selection', {
                'project_type': nl_result.get('project_type'),
                'requirements': nl_result.get('requirements')
            })

            # Step 3: Code Parsing (if existing code provided)
            parse_result = None
            if project_request.existing_code:
                parse_result = await self._execute_agent('parser', {
                    'code': project_request.existing_code,
                    'language': project_request.language
                })

            # Step 4: Component Decision
            decision_result = await self._execute_agent('component-decision', {
                'requirements': nl_result.get('requirements'),
                'framework': ui_result.get('selected_framework'),
                'existing_components': parse_result.get('components') if parse_result else None
            })

            # Step 5: Matching Rate Calculation
            matching_result = await self._execute_agent('match-rate', {
                'requirements': decision_result.get('component_requirements'),
                'available_components': await self._get_available_components()
            })

            # Step 6: Component Search
            search_result = await self._execute_agent('search', {
                'missing_components': matching_result.get('missing_components'),
                'search_criteria': decision_result.get('search_criteria')
            })

            # Step 7: Code Generation
            generation_result = await self._execute_agent('generation', {
                'components': [
                    *matching_result.get('matched_components', []),
                    *search_result.get('found_components', [])
                ],
                'architecture': decision_result.get('architecture'),
                'requirements': nl_result.get('requirements')
            })

            # Step 8: Service Assembly
            assembly_result = await self._execute_agent('assembly', {
                'generated_code': generation_result.get('code'),
                'components': generation_result.get('components'),
                'configuration': generation_result.get('configuration')
            })

            # Step 9: Download Package Creation
            download_result = await self._execute_agent('download', {
                'assembled_project': assembly_result.get('project'),
                'format': project_request.output_format
            })

            return ProjectResult(
                success=True,
                project_id=project_request.id,
                download_url=download_result.get('download_url'),
                metadata={
                    'framework': ui_result.get('selected_framework'),
                    'components': len(generation_result.get('components', [])),
                    'generated_files': assembly_result.get('file_count', 0),
                    'processing_time': time.time() - project_request.start_time
                }
            )

        except Exception as error:
            logger.error(f"Project processing failed: {error}")
            return ProjectResult(
                success=False,
                project_id=project_request.id,
                error=str(error)
            )

    async def _execute_agent(self, agent_name: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific agent with input data"""
        agent = self.agents.get(agent_name)
        if not agent:
            raise ValueError(f"Agent {agent_name} not found")

        start_time = time.time()
        result = await agent.execute(input_data)
        duration = time.time() - start_time

        logger.info(f"Agent {agent_name} executed in {duration:.2f}s")

        if not result.get('success', False):
            raise RuntimeError(f"Agent {agent_name} failed: {result.get('error', 'Unknown error')}")

        return result.get('data', {})

    async def _get_available_components(self) -> List[Dict[str, Any]]:
        """Get available components from registry"""
        # This would typically fetch from a component registry
        # For now, return empty list
        return []

    async def shutdown(self) -> None:
        """Shutdown the orchestrator and all agents"""
        logger.info("Shutting down Agent Orchestrator...")
        
        for agent in self.agents.values():
            try:
                await agent.cleanup()
            except Exception as e:
                logger.error(f"Error cleaning up agent: {e}")
        
        await self.agent_squad.shutdown()
        logger.info("Agent Orchestrator shutdown complete")