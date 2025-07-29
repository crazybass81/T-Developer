import { TracingHelper } from '../config/tracing';
import { logger } from '../config/logger';

export class TracedAgent {
  constructor(private agentName: string) {}
  
  async execute(projectId: string, input: any): Promise<any> {
    return TracingHelper.traceAgentExecution(
      this.agentName,
      projectId,
      async () => {
        logger.info(`Executing agent: ${this.agentName}`, { projectId, agentName: this.agentName });
        
        // Simulate agent execution
        await new Promise(resolve => setTimeout(resolve, Math.random() * 2000));
        
        if (Math.random() > 0.9) {
          throw new Error(`Agent ${this.agentName} failed`);
        }
        
        return {
          success: true,
          agentName: this.agentName,
          projectId,
          result: `Processed by ${this.agentName}`,
          timestamp: new Date().toISOString()
        };
      }
    );
  }
}

export class TracedExternalService {
  static async callBedrock(model: string, prompt: string): Promise<any> {
    return TracingHelper.traceExternalCall(
      'bedrock',
      `/model/${model}/invoke`,
      async () => {
        // Simulate Bedrock API call
        await new Promise(resolve => setTimeout(resolve, 1000));
        return {
          completion: `Response from ${model}`,
          usage: { input_tokens: 100, output_tokens: 50 }
        };
      }
    );
  }
  
  static async queryDynamoDB(table: string, key: any): Promise<any> {
    return TracingHelper.traceDatabaseOperation(
      'get_item',
      table,
      async () => {
        // Simulate DynamoDB query
        await new Promise(resolve => setTimeout(resolve, 200));
        return { Item: { id: key, data: 'sample' } };
      }
    );
  }
}