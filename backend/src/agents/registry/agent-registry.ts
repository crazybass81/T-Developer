import { BaseAgent, AgentContext } from '../framework/base-agent';
import { EnhancedBaseAgent } from '../framework/enhanced-base-agent';

export interface RegisteredAgent {
  id: string;
  name: string;
  type: string;
  instance: BaseAgent | EnhancedBaseAgent;
  status: string;
  registeredAt: Date;
  lastActivity: Date;
}

export class AgentRegistry {
  private agents: Map<string, RegisteredAgent> = new Map();
  private agentTypes: Map<string, typeof BaseAgent> = new Map();

  registerAgentType(type: string, agentClass: typeof BaseAgent): void {
    this.agentTypes.set(type, agentClass);
    console.log(`Agent type registered: ${type}`);
  }

  async createAgent(type: string, name: string, context: AgentContext): Promise<string> {
    const AgentClass = this.agentTypes.get(type);
    if (!AgentClass) {
      throw new Error(`Unknown agent type: ${type}`);
    }

    const agent = new (AgentClass as any)(name);
    await agent.start(context);

    const registeredAgent: RegisteredAgent = {
      id: agent.id || `${name}-${Date.now()}`,
      name,
      type,
      instance: agent,
      status: agent.getStatus(),
      registeredAt: new Date(),
      lastActivity: new Date()
    };

    this.agents.set(registeredAgent.id, registeredAgent);
    console.log(`Agent created and registered: ${registeredAgent.id}`);

    return registeredAgent.id;
  }

  getAgent(agentId: string): RegisteredAgent | undefined {
    return this.agents.get(agentId);
  }

  getAllAgents(): RegisteredAgent[] {
    return Array.from(this.agents.values());
  }

  getAgentsByType(type: string): RegisteredAgent[] {
    return Array.from(this.agents.values()).filter(agent => agent.type === type);
  }

  async stopAgent(agentId: string): Promise<void> {
    const agent = this.agents.get(agentId);
    if (!agent) {
      throw new Error(`Agent not found: ${agentId}`);
    }

    await agent.instance.stop();
    this.agents.delete(agentId);
    console.log(`Agent stopped and removed: ${agentId}`);
  }

  getRegisteredTypes(): string[] {
    return Array.from(this.agentTypes.keys());
  }

  getMetrics(): any {
    const agents = Array.from(this.agents.values());
    return {
      totalAgents: agents.length,
      agentsByType: agents.reduce((acc, agent) => {
        acc[agent.type] = (acc[agent.type] || 0) + 1;
        return acc;
      }, {} as Record<string, number>),
      agentsByStatus: agents.reduce((acc, agent) => {
        acc[agent.status] = (acc[agent.status] || 0) + 1;
        return acc;
      }, {} as Record<string, number>),
      registeredTypes: this.getRegisteredTypes()
    };
  }
}

export const agentRegistry = new AgentRegistry();