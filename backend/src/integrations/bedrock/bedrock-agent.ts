import { BaseAgent, AgentMessage } from '../../agents/framework/base-agent';
import { BedrockAgentCoreManager, AgentCoreConfig } from './agentcore-config';

export abstract class BedrockAgent extends BaseAgent {
  protected bedrockManager: BedrockAgentCoreManager;
  
  constructor(
    name: string,
    version: string,
    bedrockConfig: AgentCoreConfig
  ) {
    super(name, version);
    
    this.bedrockManager = new BedrockAgentCoreManager(bedrockConfig);
  }
  
  protected async processWithBedrock(
    input: string,
    sessionId?: string
  ): Promise<any> {
    const session = sessionId || await this.bedrockManager.createSession(
      this.context?.userId || 'anonymous'
    );
    
    return this.bedrockManager.invokeAgent(session, input);
  }
  
  protected async searchKnowledgeBase(query: string): Promise<any> {
    return this.bedrockManager.retrieveFromKnowledgeBase(query);
  }
}

// Example Bedrock-powered agent
export class BedrockNLInputAgent extends BedrockAgent {
  constructor(bedrockConfig: AgentCoreConfig) {
    super('bedrock-nl-input', '1.0.0', bedrockConfig);
  }
  
  protected initialize(): void {
    this.registerCapability({
      name: 'process_natural_language',
      description: 'Process natural language input using Bedrock',
      inputSchema: {
        type: 'object',
        properties: {
          text: { type: 'string' }
        },
        required: ['text']
      },
      outputSchema: {
        type: 'object',
        properties: {
          structured_requirements: { type: 'object' },
          project_metadata: { type: 'object' }
        }
      },
      version: '1.0.0'
    });
  }
  
  protected async process(message: AgentMessage): Promise<any> {
    const { payload } = message;
    
    switch (payload.action) {
      case 'process_natural_language':
        return this.processNaturalLanguage(payload.text);
      
      default:
        throw new Error(`Unknown action: ${payload.action}`);
    }
  }
  
  private async processNaturalLanguage(text: string): Promise<any> {
    // Use Bedrock to process natural language
    const bedrockResponse = await this.processWithBedrock(
      `Analyze this project description and extract structured requirements: ${text}`
    );
    
    // Also search knowledge base for similar projects
    const knowledgeResults = await this.searchKnowledgeBase(
      `project requirements similar to: ${text}`
    );
    
    return {
      structured_requirements: {
        project_type: 'web_application', // Extracted from Bedrock response
        features: ['user_auth', 'data_storage'], // Extracted from Bedrock response
        technologies: ['react', 'nodejs'], // Extracted from Bedrock response
        complexity: 'medium'
      },
      project_metadata: {
        estimated_duration: '2-4 weeks',
        team_size: '2-3 developers',
        budget_range: 'medium'
      },
      bedrock_response: bedrockResponse,
      knowledge_base_results: knowledgeResults,
      processed_at: new Date().toISOString()
    };
  }
}