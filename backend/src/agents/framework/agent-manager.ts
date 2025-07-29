import { BaseAgent, AgentContext, AgentMessage } from './base-agent';
import { EventEmitter } from 'events';

export interface AgentRegistry {
  [key: string]: new (...args: any[]) => BaseAgent;
}

export class AgentManager extends EventEmitter {
  private agents: Map<string, BaseAgent> = new Map();
  private registry: AgentRegistry = {};
  
  registerAgentType(name: string, agentClass: new (...args: any[]) => BaseAgent): void {
    this.registry[name] = agentClass;
    console.log(`Agent type registered: ${name}`);
  }
  
  async createAgent(type: string, ...args: any[]): Promise<string> {
    const AgentClass = this.registry[type];
    if (!AgentClass) {
      throw new Error(`Unknown agent type: ${type}`);
    }
    
    const agent = new AgentClass(...args);
    this.agents.set(agent.id, agent);
    
    // Forward agent events
    agent.on('started', (data) => this.emit('agent:started', data));
    agent.on('stopped', (data) => this.emit('agent:stopped', data));
    
    console.log(`Agent created: ${agent.id} (${type})`);
    return agent.id;
  }
  
  async startAgent(agentId: string, context: AgentContext): Promise<void> {
    const agent = this.agents.get(agentId);
    if (!agent) {
      throw new Error(`Agent not found: ${agentId}`);
    }
    
    await agent.start(context);
  }
  
  async stopAgent(agentId: string): Promise<void> {
    const agent = this.agents.get(agentId);
    if (!agent) {
      throw new Error(`Agent not found: ${agentId}`);
    }
    
    await agent.stop();
    this.agents.delete(agentId);
  }
  
  async sendMessage(agentId: string, message: AgentMessage): Promise<AgentMessage> {
    const agent = this.agents.get(agentId);
    if (!agent) {
      throw new Error(`Agent not found: ${agentId}`);
    }
    
    return await agent.handleMessage(message);
  }
  
  getAgent(agentId: string): BaseAgent | undefined {
    return this.agents.get(agentId);
  }
  
  listAgents(): Array<{ id: string; name: string; status: string }> {
    return Array.from(this.agents.values()).map(agent => ({
      id: agent.id,
      name: agent.name,
      status: agent.getStatus()
    }));
  }
  
  getAgentMetrics(): any[] {
    return Array.from(this.agents.values()).map(agent => agent.getMetrics());
  }
}