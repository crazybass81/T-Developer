export { BedrockAgentCoreManager, AgentCoreConfig } from './agentcore-config';
export { BedrockAgent, BedrockNLInputAgent } from './bedrock-agent';

// Configuration factory
export function createBedrockConfig(
  agentId: string,
  agentAliasId: string,
  region: string = 'us-east-1',
  knowledgeBaseId?: string
): AgentCoreConfig {
  return {
    agentId,
    agentAliasId,
    region,
    knowledgeBaseId,
    instructionTemplate: 'You are a helpful AI assistant for software development.'
  };
}

// Environment-based configuration
export function getBedrockConfigFromEnv(): AgentCoreConfig {
  const agentId = process.env.BEDROCK_AGENT_ID;
  const agentAliasId = process.env.BEDROCK_AGENT_ALIAS_ID;
  const region = process.env.AWS_BEDROCK_REGION || 'us-east-1';
  const knowledgeBaseId = process.env.BEDROCK_KNOWLEDGE_BASE_ID;
  
  if (!agentId || !agentAliasId) {
    throw new Error('Bedrock agent configuration missing. Set BEDROCK_AGENT_ID and BEDROCK_AGENT_ALIAS_ID');
  }
  
  return createBedrockConfig(agentId, agentAliasId, region, knowledgeBaseId);
}