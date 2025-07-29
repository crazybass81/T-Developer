import { BaseAgent, AgentMessage, AgentCapability } from '../framework/base-agent';

export class ExampleAgent extends BaseAgent {
  protected initialize(): void {
    const capability: AgentCapability = {
      name: 'example-processing',
      description: 'Example agent for demonstration',
      inputSchema: {
        type: 'object',
        properties: {
          message: { type: 'string' }
        }
      },
      outputSchema: {
        type: 'object',
        properties: {
          processed: { type: 'string' }
        }
      },
      version: '1.0.0'
    };

    this.registerCapability(capability);
  }

  protected async process(message: AgentMessage): Promise<any> {
    const { payload } = message;
    
    // Simulate processing
    await new Promise(resolve => setTimeout(resolve, 100));
    
    return {
      processed: `Processed: ${payload.message || 'No message'}`,
      timestamp: new Date().toISOString(),
      agentId: this.id
    };
  }
}