import { BaseAgent, AgentCapability } from './base-agent';
import { Logger } from 'winston';

export interface AgentRegistration {
  id: string;
  name: string;
  version: string;
  type: string;
  instance: BaseAgent;
  capabilities: AgentCapability[];
  status: 'active' | 'inactive' | 'error';
  registeredAt: Date;
  lastHeartbeat: Date;
}

export class AgentRegistry {
  private agents: Map<string, AgentRegistration> = new Map();
  private typeIndex: Map<string, Set<string>> = new Map();
  private capabilityIndex: Map<string, Set<string>> = new Map();
  private logger: Logger;

  constructor(logger: Logger) {
    this.logger = logger;
  }

  register(agent: BaseAgent, type: string): string {
    const registration: AgentRegistration = {
      id: agent['id'],
      name: agent['name'],
      version: '1.0.0',
      type,
      instance: agent,
      capabilities: agent.getCapabilities(),
      status: 'active',
      registeredAt: new Date(),
      lastHeartbeat: new Date()
    };

    this.agents.set(registration.id, registration);
    
    // Type index
    if (!this.typeIndex.has(type)) {
      this.typeIndex.set(type, new Set());
    }
    this.typeIndex.get(type)!.add(registration.id);

    // Capability index
    registration.capabilities.forEach(cap => {
      if (!this.capabilityIndex.has(cap.name)) {
        this.capabilityIndex.set(cap.name, new Set());
      }
      this.capabilityIndex.get(cap.name)!.add(registration.id);
    });

    this.logger.info(`Agent registered: ${registration.name}`, {
      agentId: registration.id,
      type,
      capabilities: registration.capabilities.map(c => c.name)
    });

    return registration.id;
  }

  unregister(agentId: string): boolean {
    const registration = this.agents.get(agentId);
    if (!registration) return false;

    // Remove from type index
    const typeAgents = this.typeIndex.get(registration.type);
    if (typeAgents) {
      typeAgents.delete(agentId);
      if (typeAgents.size === 0) {
        this.typeIndex.delete(registration.type);
      }
    }

    // Remove from capability index
    registration.capabilities.forEach(cap => {
      const capAgents = this.capabilityIndex.get(cap.name);
      if (capAgents) {
        capAgents.delete(agentId);
        if (capAgents.size === 0) {
          this.capabilityIndex.delete(cap.name);
        }
      }
    });

    this.agents.delete(agentId);
    
    this.logger.info(`Agent unregistered: ${registration.name}`, {
      agentId
    });

    return true;
  }

  getAgent(agentId: string): BaseAgent | undefined {
    return this.agents.get(agentId)?.instance;
  }

  getAgentsByType(type: string): BaseAgent[] {
    const agentIds = this.typeIndex.get(type) || new Set();
    return Array.from(agentIds)
      .map(id => this.agents.get(id)?.instance)
      .filter(agent => agent !== undefined) as BaseAgent[];
  }

  getAgentsByCapability(capability: string): BaseAgent[] {
    const agentIds = this.capabilityIndex.get(capability) || new Set();
    return Array.from(agentIds)
      .map(id => this.agents.get(id)?.instance)
      .filter(agent => agent !== undefined) as BaseAgent[];
  }

  getAllAgents(): AgentRegistration[] {
    return Array.from(this.agents.values());
  }

  updateHeartbeat(agentId: string): void {
    const registration = this.agents.get(agentId);
    if (registration) {
      registration.lastHeartbeat = new Date();
      registration.status = 'active';
    }
  }

  getHealthyAgents(): AgentRegistration[] {
    const now = new Date();
    const timeout = 30000; // 30 seconds

    return Array.from(this.agents.values()).filter(reg => {
      const timeSinceHeartbeat = now.getTime() - reg.lastHeartbeat.getTime();
      return timeSinceHeartbeat < timeout && reg.status === 'active';
    });
  }
}