import { BaseAgent, AgentMessage, AgentCapability } from '../framework/base-agent';

export class ExampleAgent extends BaseAgent {
  constructor() {
    super('example-agent', '1.0.0');
  }
  
  protected initialize(): void {
    // Register capabilities
    this.registerCapability({
      name: 'process_text',
      description: 'Process text input and return analysis',
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
          analysis: { type: 'string' },
          wordCount: { type: 'number' }
        }
      },
      version: '1.0.0'
    });
  }
  
  protected async process(message: AgentMessage): Promise<any> {
    const { payload } = message;
    
    switch (payload.action) {
      case 'process_text':
        return this.processText(payload.text);
      
      default:
        throw new Error(`Unknown action: ${payload.action}`);
    }
  }
  
  private async processText(text: string): Promise<any> {
    // Simulate processing
    await new Promise(resolve => setTimeout(resolve, 100));
    
    return {
      analysis: `Processed text: "${text}"`,
      wordCount: text.split(' ').length,
      timestamp: new Date().toISOString()
    };
  }
  
  protected async onStart(): Promise<void> {
    console.log('Example agent started and ready');
  }
  
  protected async onStop(): Promise<void> {
    console.log('Example agent stopped');
  }
}