"""
T-Developer 9개 핵심 에이전트 타입 정의
"""

from enum import Enum
from typing import List, Dict
from dataclasses import dataclass

class AgentType(Enum):
    """T-Developer 9개 핵심 에이전트 타입"""
    NL_INPUT = 'nl-input'
    UI_SELECTION = 'ui-selection'
    PARSER = 'parser'
    COMPONENT_DECISION = 'component-decision'
    MATCH_RATE = 'match-rate'
    SEARCH = 'search'
    GENERATION = 'generation'
    ASSEMBLY = 'assembly'
    DOWNLOAD = 'download'

@dataclass
class AgentSpec:
    """에이전트 사양 정의"""
    type: AgentType
    name: str
    description: str
    inputs: List[str]
    outputs: List[str]
    dependencies: List[AgentType]

# 에이전트 사양 정의
AGENT_SPECIFICATIONS: Dict[AgentType, AgentSpec] = {
    AgentType.NL_INPUT: AgentSpec(
        type=AgentType.NL_INPUT,
        name='Natural Language Input Agent',
        description='Processes natural language project descriptions',
        inputs=['user_description', 'project_requirements'],
        outputs=['structured_requirements', 'project_metadata'],
        dependencies=[]
    ),
    
    AgentType.UI_SELECTION: AgentSpec(
        type=AgentType.UI_SELECTION,
        name='UI Framework Selection Agent',
        description='Selects optimal UI framework and design system',
        inputs=['structured_requirements', 'target_platforms'],
        outputs=['ui_framework', 'design_system', 'component_library'],
        dependencies=[AgentType.NL_INPUT]
    ),
    
    AgentType.PARSER: AgentSpec(
        type=AgentType.PARSER,
        name='Code Parsing Agent',
        description='Parses and analyzes existing codebases',
        inputs=['codebase_url', 'repository_info'],
        outputs=['code_structure', 'dependencies', 'patterns'],
        dependencies=[]
    ),
    
    AgentType.COMPONENT_DECISION: AgentSpec(
        type=AgentType.COMPONENT_DECISION,
        name='Component Decision Agent',
        description='Makes architectural decisions about component selection',
        inputs=['requirements', 'available_components', 'constraints'],
        outputs=['component_decisions', 'architecture_plan'],
        dependencies=[AgentType.UI_SELECTION, AgentType.PARSER]
    ),
    
    AgentType.MATCH_RATE: AgentSpec(
        type=AgentType.MATCH_RATE,
        name='Matching Rate Calculator Agent',
        description='Calculates compatibility scores between requirements and components',
        inputs=['requirements', 'components', 'criteria'],
        outputs=['matching_scores', 'compatibility_matrix'],
        dependencies=[AgentType.COMPONENT_DECISION]
    ),
    
    AgentType.SEARCH: AgentSpec(
        type=AgentType.SEARCH,
        name='Component Search Agent',
        description='Searches for components across multiple registries',
        inputs=['search_criteria', 'registries', 'filters'],
        outputs=['found_components', 'search_results'],
        dependencies=[AgentType.MATCH_RATE]
    ),
    
    AgentType.GENERATION: AgentSpec(
        type=AgentType.GENERATION,
        name='Code Generation Agent',
        description='Generates custom components and code',
        inputs=['specifications', 'templates', 'requirements'],
        outputs=['generated_code', 'tests', 'documentation'],
        dependencies=[AgentType.SEARCH]
    ),
    
    AgentType.ASSEMBLY: AgentSpec(
        type=AgentType.ASSEMBLY,
        name='Service Assembly Agent',
        description='Assembles components into complete services',
        inputs=['components', 'architecture', 'configuration'],
        outputs=['assembled_service', 'deployment_config'],
        dependencies=[AgentType.GENERATION]
    ),
    
    AgentType.DOWNLOAD: AgentSpec(
        type=AgentType.DOWNLOAD,
        name='Download & Package Agent',
        description='Packages and delivers the complete project',
        inputs=['assembled_service', 'delivery_options'],
        outputs=['download_package', 'installation_guide'],
        dependencies=[AgentType.ASSEMBLY]
    )
}

def get_agent_dependencies(agent_type: AgentType) -> List[AgentType]:
    """Get dependencies for an agent type"""
    return AGENT_SPECIFICATIONS[agent_type].dependencies

def get_execution_order() -> List[AgentType]:
    """Get the execution order of agents"""
    return [
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