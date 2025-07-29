import { BedrockRuntimeClient, InvokeModelCommand } from '@aws-sdk/client-bedrock-runtime';
import { logger } from '../../config/logger';

interface AgentConfig {
  name: string;
  type: 'processing' | 'analysis' | 'generation' | 'integration';
  model: string;
  capabilities: string[];
}

interface AgentResponse {
  success: boolean;
  data: any;
  metadata: {
    agentName: string;
    executionTime: number;
    version: string;
  };
}

export class UnifiedAgentSystem {
  private bedrockClient: BedrockRuntimeClient;
  private agents: Map<string, AgentConfig> = new Map();

  constructor() {
    this.bedrockClient = new BedrockRuntimeClient({
      region: process.env.AWS_BEDROCK_REGION || 'us-east-1'
    });
    
    this.initializeAgents();
  }

  private initializeAgents(): void {
    const agentConfigs: AgentConfig[] = [
      {
        name: 'nl-input',
        type: 'analysis',
        model: 'anthropic.claude-3-sonnet-20240229-v1:0',
        capabilities: ['natural-language-processing', 'requirement-analysis']
      },
      {
        name: 'ui-selection',
        type: 'analysis',
        model: 'anthropic.claude-3-sonnet-20240229-v1:0',
        capabilities: ['ui-framework-selection', 'design-analysis']
      },
      {
        name: 'parsing',
        type: 'processing',
        model: 'amazon.nova-pro-v1:0',
        capabilities: ['code-parsing', 'ast-analysis']
      },
      {
        name: 'component-decision',
        type: 'analysis',
        model: 'anthropic.claude-3-opus-20240229-v1:0',
        capabilities: ['component-selection', 'architecture-decisions']
      },
      {
        name: 'matching-rate',
        type: 'processing',
        model: 'amazon.nova-lite-v1:0',
        capabilities: ['similarity-calculation', 'compatibility-analysis']
      },
      {
        name: 'search',
        type: 'integration',
        model: 'amazon.nova-lite-v1:0',
        capabilities: ['component-search', 'registry-integration']
      },
      {
        name: 'generation',
        type: 'generation',
        model: 'anthropic.claude-3-opus-20240229-v1:0',
        capabilities: ['code-generation', 'template-creation']
      },
      {
        name: 'assembly',
        type: 'integration',
        model: 'anthropic.claude-3-sonnet-20240229-v1:0',
        capabilities: ['service-assembly', 'integration-orchestration']
      },
      {
        name: 'download',
        type: 'processing',
        model: 'amazon.nova-lite-v1:0',
        capabilities: ['packaging', 'delivery-management']
      }
    ];

    agentConfigs.forEach(config => {
      this.agents.set(config.name, config);
    });
  }

  async executeAgent(agentName: string, input: any): Promise<AgentResponse> {
    const startTime = Date.now();
    const agent = this.agents.get(agentName);

    if (!agent) {
      throw new Error(`Agent '${agentName}' not found`);
    }

    try {
      logger.info(`Executing agent: ${agentName}`, { input });

      const prompt = this.buildPrompt(agent, input);
      const response = await this.invokeModel(agent.model, prompt);

      const result = {
        success: true,
        data: response,
        metadata: {
          agentName,
          executionTime: Date.now() - startTime,
          version: '1.0.0'
        }
      };

      logger.info(`Agent execution completed: ${agentName}`, { 
        duration: result.metadata.executionTime 
      });

      return result;

    } catch (error) {
      logger.error(`Agent execution failed: ${agentName}`, error);
      throw error;
    }
  }

  private buildPrompt(agent: AgentConfig, input: any): string {
    const systemPrompts = {
      'nl-input': 'You are an expert requirements analyst. Extract technical requirements from natural language descriptions.',
      'ui-selection': 'You are a UI/UX expert. Recommend optimal UI frameworks and design systems.',
      'parsing': 'You are a code analysis expert. Parse and analyze code structures.',
      'component-decision': 'You are an architecture expert. Make component selection decisions.',
      'matching-rate': 'You are a compatibility analyst. Calculate matching rates between requirements and components.',
      'search': 'You are a component search specialist. Find relevant components from registries.',
      'generation': 'You are a code generation expert. Generate high-quality code from specifications.',
      'assembly': 'You are an integration architect. Assemble components into complete services.',
      'download': 'You are a packaging expert. Create deployment packages and delivery artifacts.'
    };

    return `${systemPrompts[agent.name] || 'You are a helpful AI assistant.'}

Input: ${JSON.stringify(input)}

Please provide a structured response that addresses the input according to your role.`;
  }

  private async invokeModel(modelId: string, prompt: string): Promise<any> {
    const command = new InvokeModelCommand({
      modelId,
      body: JSON.stringify({
        anthropic_version: "bedrock-2023-05-31",
        max_tokens: 4000,
        messages: [
          {
            role: "user",
            content: prompt
          }
        ]
      }),
      contentType: "application/json",
      accept: "application/json"
    });

    const response = await this.bedrockClient.send(command);
    const responseBody = JSON.parse(new TextDecoder().decode(response.body));
    
    return responseBody.content[0].text;
  }

  async executeWorkflow(projectDescription: string): Promise<any> {
    const workflow = [
      'nl-input',
      'ui-selection', 
      'parsing',
      'component-decision',
      'matching-rate',
      'search',
      'generation',
      'assembly',
      'download'
    ];

    let currentInput = { description: projectDescription };
    const results = [];

    for (const agentName of workflow) {
      const result = await this.executeAgent(agentName, currentInput);
      results.push(result);
      currentInput = { ...currentInput, previousResult: result.data };
    }

    return {
      workflow: results,
      finalResult: results[results.length - 1],
      totalExecutionTime: results.reduce((sum, r) => sum + r.metadata.executionTime, 0)
    };
  }

  getAvailableAgents(): string[] {
    return Array.from(this.agents.keys());
  }

  getAgentInfo(agentName: string): AgentConfig | undefined {
    return this.agents.get(agentName);
  }
}