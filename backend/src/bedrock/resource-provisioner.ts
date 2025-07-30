// backend/src/bedrock/resource-provisioner.ts
import { BedrockAgentClient, CreateAgentCommand, CreateAgentAliasCommand } from '@aws-sdk/client-bedrock-agent';

export interface ProvisioningConfig {
  agentName: string;
  description?: string;
  instruction?: string;
  foundationModel?: string;
  roleArn: string;
}

export class ResourceProvisioner {
  private client: BedrockAgentClient;

  constructor(region: string = 'us-east-1') {
    this.client = new BedrockAgentClient({ region });
  }

  async provisionAgent(config: ProvisioningConfig): Promise<{
    agentId: string;
    agentArn: string;
    aliasId?: string;
  }> {
    try {
      // Create agent
      const createAgentCommand = new CreateAgentCommand({
        agentName: config.agentName,
        description: config.description || 'T-Developer AI Agent',
        instruction: config.instruction || 'You are a helpful AI assistant for software development.',
        foundationModel: config.foundationModel || 'anthropic.claude-3-sonnet-20240229-v1:0',
        agentResourceRoleArn: config.roleArn
      });

      const agentResponse = await this.client.send(createAgentCommand);
      
      if (!agentResponse.agent?.agentId) {
        throw new Error('Failed to create agent');
      }

      // Create alias
      const createAliasCommand = new CreateAgentAliasCommand({
        agentId: agentResponse.agent.agentId,
        agentAliasName: 'PROD',
        description: 'Production alias for T-Developer agent'
      });

      const aliasResponse = await this.client.send(createAliasCommand);

      return {
        agentId: agentResponse.agent.agentId,
        agentArn: agentResponse.agent.agentArn || '',
        aliasId: aliasResponse.agentAlias?.agentAliasId
      };
    } catch (error) {
      throw new Error(`Agent provisioning failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  async checkAgentStatus(agentId: string): Promise<string> {
    try {
      const { GetAgentCommand } = await import('@aws-sdk/client-bedrock-agent');
      const command = new GetAgentCommand({ agentId });
      const response = await this.client.send(command);
      
      return response.agent?.agentStatus || 'UNKNOWN';
    } catch (error) {
      return 'ERROR';
    }
  }

  generateRoleArn(accountId: string, roleName: string = 'BedrockAgentRole'): string {
    return `arn:aws:iam::${accountId}:role/${roleName}`;
  }
}