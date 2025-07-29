export { BaseAgent, AgentContext, AgentMessage, AgentCapability } from './base-agent';
export { AgentManager, AgentRegistry } from './agent-manager';
export { AgentType, AgentSpec, AGENT_SPECIFICATIONS, getAgentDependencies, getExecutionOrder } from './agent-types';
export { MessageBus, InMemoryMessageBus, RedisMessageBus, AgentCommunicationManager, AgentRPC } from './communication';
export { AgentWorkflow, WorkflowStep, WorkflowConfig } from './workflow';

// Framework initialization
export function initializeAgentFramework(): { manager: AgentManager; communicationManager: AgentCommunicationManager } {
  const manager = new AgentManager();
  const communicationManager = new AgentCommunicationManager();
  
  console.log('🤖 Agent Framework initialized');
  console.log(`📋 ${Object.keys(AGENT_SPECIFICATIONS).length} agent types defined`);
  
  return { manager, communicationManager };
}