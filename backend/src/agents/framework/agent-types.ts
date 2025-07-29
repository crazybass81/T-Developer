// T-Developer 9개 핵심 에이전트 타입 정의

export enum AgentType {
  NL_INPUT = 'nl-input',
  UI_SELECTION = 'ui-selection', 
  PARSING = 'parsing',
  COMPONENT_DECISION = 'component-decision',
  MATCHING_RATE = 'matching-rate',
  SEARCH = 'search',
  GENERATION = 'generation',
  ASSEMBLY = 'assembly',
  DOWNLOAD = 'download'
}

export interface AgentSpec {
  type: AgentType;
  name: string;
  description: string;
  inputs: string[];
  outputs: string[];
  dependencies: AgentType[];
}

export const AGENT_SPECIFICATIONS: Record<AgentType, AgentSpec> = {
  [AgentType.NL_INPUT]: {
    type: AgentType.NL_INPUT,
    name: 'Natural Language Input Agent',
    description: 'Processes natural language project descriptions',
    inputs: ['user_description', 'project_requirements'],
    outputs: ['structured_requirements', 'project_metadata'],
    dependencies: []
  },
  
  [AgentType.UI_SELECTION]: {
    type: AgentType.UI_SELECTION,
    name: 'UI Framework Selection Agent',
    description: 'Selects optimal UI framework and design system',
    inputs: ['structured_requirements', 'target_platforms'],
    outputs: ['ui_framework', 'design_system', 'component_library'],
    dependencies: [AgentType.NL_INPUT]
  },
  
  [AgentType.PARSING]: {
    type: AgentType.PARSING,
    name: 'Code Parsing Agent',
    description: 'Parses and analyzes existing codebases',
    inputs: ['codebase_url', 'repository_info'],
    outputs: ['code_structure', 'dependencies', 'patterns'],
    dependencies: []
  },
  
  [AgentType.COMPONENT_DECISION]: {
    type: AgentType.COMPONENT_DECISION,
    name: 'Component Decision Agent',
    description: 'Makes architectural decisions about component selection',
    inputs: ['requirements', 'available_components', 'constraints'],
    outputs: ['component_decisions', 'architecture_plan'],
    dependencies: [AgentType.UI_SELECTION, AgentType.PARSING]
  },
  
  [AgentType.MATCHING_RATE]: {
    type: AgentType.MATCHING_RATE,
    name: 'Matching Rate Calculator Agent',
    description: 'Calculates compatibility scores between requirements and components',
    inputs: ['requirements', 'components', 'criteria'],
    outputs: ['matching_scores', 'compatibility_matrix'],
    dependencies: [AgentType.COMPONENT_DECISION]
  },
  
  [AgentType.SEARCH]: {
    type: AgentType.SEARCH,
    name: 'Component Search Agent',
    description: 'Searches for components across multiple registries',
    inputs: ['search_criteria', 'registries', 'filters'],
    outputs: ['found_components', 'search_results'],
    dependencies: [AgentType.MATCHING_RATE]
  },
  
  [AgentType.GENERATION]: {
    type: AgentType.GENERATION,
    name: 'Code Generation Agent',
    description: 'Generates custom components and code',
    inputs: ['specifications', 'templates', 'requirements'],
    outputs: ['generated_code', 'tests', 'documentation'],
    dependencies: [AgentType.SEARCH]
  },
  
  [AgentType.ASSEMBLY]: {
    type: AgentType.ASSEMBLY,
    name: 'Service Assembly Agent',
    description: 'Assembles components into complete services',
    inputs: ['components', 'architecture', 'configuration'],
    outputs: ['assembled_service', 'deployment_config'],
    dependencies: [AgentType.GENERATION]
  },
  
  [AgentType.DOWNLOAD]: {
    type: AgentType.DOWNLOAD,
    name: 'Download & Package Agent',
    description: 'Packages and delivers the complete project',
    inputs: ['assembled_service', 'delivery_options'],
    outputs: ['download_package', 'installation_guide'],
    dependencies: [AgentType.ASSEMBLY]
  }
};

export function getAgentDependencies(agentType: AgentType): AgentType[] {
  return AGENT_SPECIFICATIONS[agentType].dependencies;
}

export function getExecutionOrder(): AgentType[] {
  return [
    AgentType.NL_INPUT,
    AgentType.UI_SELECTION,
    AgentType.PARSING,
    AgentType.COMPONENT_DECISION,
    AgentType.MATCHING_RATE,
    AgentType.SEARCH,
    AgentType.GENERATION,
    AgentType.ASSEMBLY,
    AgentType.DOWNLOAD
  ];
}