
import { BaseAgent, AgentMessage, AgentCapability } from '../framework/base-agent';
import { Logger } from 'winston';

export class TestAgent extends BaseAgent {
  protected initialize(): void {
    this.registerCapability({
      name: 'test-capability',
      description: 'Test capability for framework validation',
      inputSchema: { type: 'object' },
      outputSchema: { type: 'object' },
      version: '1.0.0'
    });
  }

  async process(message: AgentMessage): Promise<any> {
    return {
      processed: true,
      messageId: message.id,
      timestamp: new Date()
    };
  }
}
