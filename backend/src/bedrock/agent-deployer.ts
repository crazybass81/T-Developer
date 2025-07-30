import { BedrockAgentClient, CreateAgentCommand, UpdateAgentCommand } from '@aws-sdk/client-bedrock-agent';

interface AgentConfig {
  name: string;
  code: string;
  runtime: string;
  timeout: number;
  memory: number;
}

export class AgentDeployer {
  private client: BedrockAgentClient;
  
  constructor() {
    this.client = new BedrockAgentClient({
      region: process.env.AWS_BEDROCK_REGION || 'us-east-1'
    });
  }
  
  async deployAgent(agentConfig: AgentConfig): Promise<string> {
    const command = new CreateAgentCommand({
      agentName: agentConfig.name,
      instruction: agentConfig.code,
      foundationModel: 'anthropic.claude-3-sonnet-20240229-v1:0'
    });
    
    const response = await this.client.send(command);
    return response.agent?.agentId!;
  }
  
  async updateAgent(agentId: string, config: AgentConfig): Promise<void> {
    const command = new UpdateAgentCommand({
      agentId,
      agentName: config.name,
      instruction: config.code,
      foundationModel: 'anthropic.claude-3-sonnet-20240229-v1:0',
      agentResourceRoleArn: process.env.BEDROCK_AGENT_ROLE_ARN || 'arn:aws:iam::123456789012:role/BedrockAgentRole'
    });
    
    await this.client.send(command);
  }
}