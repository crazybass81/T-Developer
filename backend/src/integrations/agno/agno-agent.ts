import { BaseAgent, AgentMessage } from '../../agents/framework/base-agent';
import { AgnoMonitoringClient, AgnoConfig, AgnoTrace } from './monitoring-config';

export class AgnoMonitoredAgent extends BaseAgent {
  protected agnoClient: AgnoMonitoringClient;
  
  constructor(
    name: string,
    version: string,
    agnoConfig: AgnoConfig
  ) {
    super(name, version);
    this.agnoClient = new AgnoMonitoringClient(agnoConfig);
  }
  
  protected initialize(): void {
    // Override in subclasses
  }
  
  protected async process(message: AgentMessage): Promise<any> {
    // Override in subclasses
    throw new Error('Process method must be implemented');
  }
  
  async handleMessage(message: AgentMessage): Promise<AgentMessage> {
    const startTime = Date.now();
    
    try {
      const response = await super.handleMessage(message);
      
      // Monitor successful operation
      await this.agnoClient.monitorAgentPerformance(
        this.name,
        message.payload.action || 'handle_message',
        Date.now() - startTime,
        true,
        {
          messageType: message.type,
          responseType: response.type
        }
      );
      
      return response;
      
    } catch (error) {
      // Monitor failed operation
      await this.agnoClient.monitorAgentPerformance(
        this.name,
        message.payload.action || 'handle_message',
        Date.now() - startTime,
        false,
        {
          messageType: message.type,
          error: error instanceof Error ? error.message : 'Unknown error'
        }
      );
      
      // Track error
      await this.agnoClient.trackError(
        error instanceof Error ? error : new Error('Unknown error'),
        {
          agent: this.name,
          operation: message.payload.action || 'handle_message',
          userId: this.context?.userId,
          projectId: this.context?.projectId
        }
      );
      
      throw error;
    }
  }
  
  async stop(): Promise<void> {
    await super.stop();
    await this.agnoClient.shutdown();
  }
}

// Example Agno-monitored agent
export class AgnoNLInputAgent extends AgnoMonitoredAgent {
  constructor(agnoConfig: AgnoConfig) {
    super('agno-nl-input', '1.0.0', agnoConfig);
  }
  
  protected initialize(): void {
    this.registerCapability({
      name: 'process_natural_language_with_monitoring',
      description: 'Process natural language with Agno monitoring',
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
          monitoring_data: { type: 'object' }
        }
      },
      version: '1.0.0'
    });
  }
  
  @AgnoTrace('process_natural_language')
  protected async process(message: AgentMessage): Promise<any> {
    const { payload } = message;
    
    switch (payload.action) {
      case 'process_natural_language_with_monitoring':
        return this.processNaturalLanguage(payload.text);
      
      default:
        throw new Error(`Unknown action: ${payload.action}`);
    }
  }
  
  private async processNaturalLanguage(text: string): Promise<any> {
    // Simulate processing time
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Monitor progress
    await this.agnoClient.monitorProjectProgress(
      this.context?.projectId || 'unknown',
      'natural_language_processing',
      50,
      { text_length: text.length }
    );
    
    const result = {
      structured_requirements: {
        project_type: 'web_application',
        features: ['user_auth', 'data_storage'],
        technologies: ['react', 'nodejs'],
        complexity: 'medium'
      },
      confidence: 0.85,
      processed_at: new Date().toISOString(),
      monitoring_data: {
        agent: this.name,
        processing_time: 1000,
        text_length: text.length
      }
    };
    
    // Monitor completion
    await this.agnoClient.monitorProjectProgress(
      this.context?.projectId || 'unknown',
      'natural_language_processing',
      100,
      { result_confidence: result.confidence }
    );
    
    return result;
  }
}