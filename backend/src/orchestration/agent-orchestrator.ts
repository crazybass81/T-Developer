import { AgentSquad } from 'agent-squad';
import { Agent } from 'agno';
import { logger } from '../config/logger';
import { config } from '../config/environment';
import { NLInputAgent } from '../agents/nl-input-agent';
import { UISelectionAgent } from '../agents/ui-selection-agent';
import { ParsingAgent } from '../agents/parsing-agent';
import { ComponentDecisionAgent } from '../agents/component-decision-agent';
import { MatchingRateAgent } from '../agents/matching-rate-agent';
import { SearchAgent } from '../agents/search-agent';
import { GenerationAgent } from '../agents/generation-agent';
import { AssemblyAgent } from '../agents/assembly-agent';
import { DownloadAgent } from '../agents/download-agent';

export class AgentOrchestrator {
  private agentSquad: AgentSquad;
  private agents: Map<string, Agent> = new Map();

  async initialize(): Promise<void> {
    logger.info('Initializing Agent Orchestrator...');

    // Initialize Agent Squad
    this.agentSquad = new AgentSquad({
      storage: config.agentSquad.storage,
      timeout: config.agentSquad.timeout
    });

    // Initialize 9 Core Agents
    await this.initializeAgents();

    logger.info('Agent Orchestrator initialized successfully');
  }

  private async initializeAgents(): Promise<void> {
    const agentClasses = [
      { name: 'nl-input', class: NLInputAgent },
      { name: 'ui-selection', class: UISelectionAgent },
      { name: 'parsing', class: ParsingAgent },
      { name: 'component-decision', class: ComponentDecisionAgent },
      { name: 'matching-rate', class: MatchingRateAgent },
      { name: 'search', class: SearchAgent },
      { name: 'generation', class: GenerationAgent },
      { name: 'assembly', class: AssemblyAgent },
      { name: 'download', class: DownloadAgent }
    ];

    for (const { name, class: AgentClass } of agentClasses) {
      try {
        const agent = new AgentClass();
        await agent.initialize();
        this.agents.set(name, agent);
        await this.agentSquad.addAgent(agent);
        logger.info(`Initialized ${name} agent`);
      } catch (error) {
        logger.error(`Failed to initialize ${name} agent:`, error);
        throw error;
      }
    }
  }

  async processProject(projectRequest: ProjectRequest): Promise<ProjectResult> {
    logger.info('Processing project request', { projectId: projectRequest.id });

    try {
      // Step 1: Natural Language Processing
      const nlResult = await this.executeAgent('nl-input', {
        description: projectRequest.description,
        requirements: projectRequest.requirements
      });

      // Step 2: UI Framework Selection
      const uiResult = await this.executeAgent('ui-selection', {
        projectType: nlResult.projectType,
        requirements: nlResult.requirements
      });

      // Step 3: Code Parsing (if existing code provided)
      let parseResult = null;
      if (projectRequest.existingCode) {
        parseResult = await this.executeAgent('parsing', {
          code: projectRequest.existingCode,
          language: projectRequest.language
        });
      }

      // Step 4: Component Decision
      const decisionResult = await this.executeAgent('component-decision', {
        requirements: nlResult.requirements,
        framework: uiResult.selectedFramework,
        existingComponents: parseResult?.components
      });

      // Step 5: Matching Rate Calculation
      const matchingResult = await this.executeAgent('matching-rate', {
        requirements: decisionResult.componentRequirements,
        availableComponents: await this.getAvailableComponents()
      });

      // Step 6: Component Search
      const searchResult = await this.executeAgent('search', {
        missingComponents: matchingResult.missingComponents,
        searchCriteria: decisionResult.searchCriteria
      });

      // Step 7: Code Generation
      const generationResult = await this.executeAgent('generation', {
        components: [...matchingResult.matchedComponents, ...searchResult.foundComponents],
        architecture: decisionResult.architecture,
        requirements: nlResult.requirements
      });

      // Step 8: Service Assembly
      const assemblyResult = await this.executeAgent('assembly', {
        generatedCode: generationResult.code,
        components: generationResult.components,
        configuration: generationResult.configuration
      });

      // Step 9: Download Package Creation
      const downloadResult = await this.executeAgent('download', {
        assembledProject: assemblyResult.project,
        format: projectRequest.outputFormat || 'zip'
      });

      return {
        success: true,
        projectId: projectRequest.id,
        downloadUrl: downloadResult.downloadUrl,
        metadata: {
          framework: uiResult.selectedFramework,
          components: generationResult.components.length,
          generatedFiles: assemblyResult.fileCount,
          processingTime: Date.now() - projectRequest.startTime
        }
      };

    } catch (error) {
      logger.error('Project processing failed:', error);
      return {
        success: false,
        projectId: projectRequest.id,
        error: error.message
      };
    }
  }

  private async executeAgent(agentName: string, input: any): Promise<any> {
    const agent = this.agents.get(agentName);
    if (!agent) {
      throw new Error(`Agent ${agentName} not found`);
    }

    const startTime = Date.now();
    const result = await agent.execute(input);
    const duration = Date.now() - startTime;

    logger.info(`Agent ${agentName} executed`, { duration, success: result.success });
    
    if (!result.success) {
      throw new Error(`Agent ${agentName} failed: ${result.error}`);
    }

    return result.data;
  }

  private async getAvailableComponents(): Promise<any[]> {
    // This would typically fetch from a component registry
    return [];
  }
}

export interface ProjectRequest {
  id: string;
  description: string;
  requirements?: string[];
  existingCode?: string;
  language?: string;
  outputFormat?: string;
  startTime: number;
}

export interface ProjectResult {
  success: boolean;
  projectId: string;
  downloadUrl?: string;
  error?: string;
  metadata?: {
    framework: string;
    components: number;
    generatedFiles: number;
    processingTime: number;
  };
}