import { BedrockAgentRuntimeClient, InvokeAgentCommand } from '@aws-sdk/client-bedrock-agent-runtime';

export class AgentCoreClient {
  private client: BedrockAgentRuntimeClient;
  private runtimeId: string;
  
  constructor() {
    this.client = new BedrockAgentRuntimeClient({
      region: process.env.AWS_BEDROCK_REGION || 'us-east-1'
    });
    this.runtimeId = process.env.BEDROCK_AGENTCORE_RUNTIME_ID!;
  }
  
  async createSession(sessionId: string): Promise<string> {
    const command = new InvokeAgentCommand({
      agentId: this.runtimeId,
      agentAliasId: process.env.BEDROCK_AGENT_ALIAS_ID || 'TSTALIASID',
      sessionId,
      inputText: 'initialize'
    });
    
    const response = await this.client.send(command);
    return response.sessionId!;
  }
  
  async executeAgent(sessionId: string, input: any): Promise<any> {
    const command = new InvokeAgentCommand({
      agentId: this.runtimeId,
      agentAliasId: process.env.BEDROCK_AGENT_ALIAS_ID || 'TSTALIASID',
      sessionId,
      inputText: JSON.stringify(input)
    });
    
    return await this.client.send(command);
  }
}