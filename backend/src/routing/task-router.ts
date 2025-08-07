/**
 * T-Developer Dynamic Task Router
 * 동적 태스크 라우팅 엔진
 */

import { EventEmitter } from 'events';
import { BaseAgent } from '../agents/framework/base-agent';
import { Logger } from '../utils/logger';

export interface Task {
  id: string;
  type: string;
  priority: number;
  payload: any;
  metadata?: {
    requiredCapabilities?: string[];
    preferredAgent?: string;
    timeout?: number;
    retries?: number;
  };
  createdAt: Date;
  status: 'pending' | 'routing' | 'assigned' | 'processing' | 'completed' | 'failed';
}

export interface RoutingRule {
  id: string;
  name: string;
  condition: (task: Task) => boolean;
  agentSelector: (agents: BaseAgent[]) => BaseAgent | null;
  priority: number;
}

export interface RoutingDecision {
  taskId: string;
  agentId: string;
  rule: string;
  score: number;
  timestamp: Date;
}

/**
 * Task Router
 */
export class TaskRouter extends EventEmitter {
  private logger: Logger;
  private rules: Map<string, RoutingRule>;
  private routingHistory: RoutingDecision[];
  private agentCapabilities: Map<string, string[]>;
  private agentLoad: Map<string, number>;
  private readonly MAX_HISTORY = 1000;
  
  constructor() {
    super();
    this.logger = new Logger('TaskRouter');
    this.rules = new Map();
    this.routingHistory = [];
    this.agentCapabilities = new Map();
    this.agentLoad = new Map();
    
    this.initializeDefaultRules();
  }
  
  /**
   * Route a task to the best available agent
   */
  async route(task: Task, availableAgents: BaseAgent[]): Promise<BaseAgent | null> {
    this.logger.debug(`Routing task ${task.id} of type ${task.type}`);
    
    try {
      // Update task status
      task.status = 'routing';
      
      // Filter agents by capabilities
      const capableAgents = this.filterByCapabilities(task, availableAgents);
      
      if (capableAgents.length === 0) {
        this.logger.warn(`No capable agents found for task ${task.id}`);
        return null;
      }
      
      // Apply routing rules
      const selectedAgent = this.applyRoutingRules(task, capableAgents);
      
      if (selectedAgent) {
        // Record routing decision
        this.recordRoutingDecision(task, selectedAgent);
        
        // Update agent load
        this.updateAgentLoad(selectedAgent.getMetadata().agentId, 1);
        
        // Update task status
        task.status = 'assigned';
        
        this.emit('task:routed', { task, agent: selectedAgent });
        
        return selectedAgent;
      }
      
      // Fallback to load balancing
      return this.loadBalanceRoute(task, capableAgents);
    } catch (error) {
      this.logger.error(`Error routing task ${task.id}:`, error);
      this.emit('routing:error', { task, error });
      return null;
    }
  }
  
  /**
   * Register a routing rule
   */
  registerRule(rule: RoutingRule): void {
    this.rules.set(rule.id, rule);
    this.logger.info(`Registered routing rule: ${rule.name}`);
  }
  
  /**
   * Unregister a routing rule
   */
  unregisterRule(ruleId: string): void {
    if (this.rules.delete(ruleId)) {
      this.logger.info(`Unregistered routing rule: ${ruleId}`);
    }
  }
  
  /**
   * Update agent capabilities
   */
  updateAgentCapabilities(agentId: string, capabilities: string[]): void {
    this.agentCapabilities.set(agentId, capabilities);
  }
  
  /**
   * Get routing statistics
   */
  getRoutingStats(): {
    totalRouted: number;
    byAgent: Map<string, number>;
    byRule: Map<string, number>;
    avgRoutingTime: number;
  } {
    const byAgent = new Map<string, number>();
    const byRule = new Map<string, number>();
    
    for (const decision of this.routingHistory) {
      // Count by agent
      const agentCount = byAgent.get(decision.agentId) || 0;
      byAgent.set(decision.agentId, agentCount + 1);
      
      // Count by rule
      const ruleCount = byRule.get(decision.rule) || 0;
      byRule.set(decision.rule, ruleCount + 1);
    }
    
    return {
      totalRouted: this.routingHistory.length,
      byAgent,
      byRule,
      avgRoutingTime: 0 // TODO: Implement timing
    };
  }
  
  /**
   * Get agent load information
   */
  getAgentLoad(): Map<string, number> {
    return new Map(this.agentLoad);
  }
  
  /**
   * Reset agent load
   */
  resetAgentLoad(agentId?: string): void {
    if (agentId) {
      this.agentLoad.set(agentId, 0);
    } else {
      this.agentLoad.clear();
    }
  }
  
  /**
   * Initialize default routing rules
   */
  private initializeDefaultRules(): void {
    // NL Input tasks
    this.registerRule({
      id: 'nl-input-rule',
      name: 'NL Input Task Routing',
      condition: (task) => task.type === 'nl-input',
      agentSelector: (agents) => {
        return agents.find(a => 
          a.getMetadata().agentType === 'NLInputAgent'
        ) || null;
      },
      priority: 100
    });
    
    // UI Selection tasks
    this.registerRule({
      id: 'ui-selection-rule',
      name: 'UI Selection Task Routing',
      condition: (task) => task.type === 'ui-selection',
      agentSelector: (agents) => {
        return agents.find(a => 
          a.getMetadata().agentType === 'UISelectionAgent'
        ) || null;
      },
      priority: 100
    });
    
    // Parser tasks
    this.registerRule({
      id: 'parser-rule',
      name: 'Parser Task Routing',
      condition: (task) => task.type === 'parsing',
      agentSelector: (agents) => {
        return agents.find(a => 
          a.getMetadata().agentType === 'ParserAgent'
        ) || null;
      },
      priority: 100
    });
    
    // High priority tasks
    this.registerRule({
      id: 'high-priority-rule',
      name: 'High Priority Task Routing',
      condition: (task) => task.priority >= 8,
      agentSelector: (agents) => {
        // Select least loaded agent
        let minLoad = Infinity;
        let selectedAgent = null;
        
        for (const agent of agents) {
          const load = this.agentLoad.get(agent.getMetadata().agentId) || 0;
          if (load < minLoad) {
            minLoad = load;
            selectedAgent = agent;
          }
        }
        
        return selectedAgent;
      },
      priority: 200
    });
    
    // Preferred agent rule
    this.registerRule({
      id: 'preferred-agent-rule',
      name: 'Preferred Agent Routing',
      condition: (task) => !!task.metadata?.preferredAgent,
      agentSelector: (agents) => {
        if (!task.metadata?.preferredAgent) return null;
        
        return agents.find(a => 
          a.getMetadata().agentId === task.metadata!.preferredAgent
        ) || null;
      },
      priority: 150
    });
  }
  
  /**
   * Filter agents by capabilities
   */
  private filterByCapabilities(task: Task, agents: BaseAgent[]): BaseAgent[] {
    if (!task.metadata?.requiredCapabilities) {
      return agents;
    }
    
    const requiredCaps = task.metadata.requiredCapabilities;
    
    return agents.filter(agent => {
      const agentId = agent.getMetadata().agentId;
      const agentCaps = this.agentCapabilities.get(agentId) || 
                       agent.getMetadata().capabilities || [];
      
      // Check if agent has all required capabilities
      return requiredCaps.every(cap => agentCaps.includes(cap));
    });
  }
  
  /**
   * Apply routing rules
   */
  private applyRoutingRules(task: Task, agents: BaseAgent[]): BaseAgent | null {
    // Sort rules by priority (higher priority first)
    const sortedRules = Array.from(this.rules.values())
      .sort((a, b) => b.priority - a.priority);
    
    for (const rule of sortedRules) {
      if (rule.condition(task)) {
        const selectedAgent = rule.agentSelector(agents);
        
        if (selectedAgent) {
          this.logger.debug(
            `Task ${task.id} routed by rule ${rule.name} to agent ${selectedAgent.getMetadata().agentId}`
          );
          return selectedAgent;
        }
      }
    }
    
    return null;
  }
  
  /**
   * Load balance routing
   */
  private loadBalanceRoute(task: Task, agents: BaseAgent[]): BaseAgent | null {
    if (agents.length === 0) return null;
    
    // Find agent with lowest load
    let minLoad = Infinity;
    let selectedAgent = agents[0];
    
    for (const agent of agents) {
      const agentId = agent.getMetadata().agentId;
      const load = this.agentLoad.get(agentId) || 0;
      
      if (load < minLoad) {
        minLoad = load;
        selectedAgent = agent;
      }
    }
    
    this.logger.debug(
      `Task ${task.id} load-balanced to agent ${selectedAgent.getMetadata().agentId} (load: ${minLoad})`
    );
    
    return selectedAgent;
  }
  
  /**
   * Record routing decision
   */
  private recordRoutingDecision(task: Task, agent: BaseAgent): void {
    const decision: RoutingDecision = {
      taskId: task.id,
      agentId: agent.getMetadata().agentId,
      rule: 'unknown', // TODO: Track which rule was used
      score: 1.0,
      timestamp: new Date()
    };
    
    this.routingHistory.push(decision);
    
    // Limit history size
    if (this.routingHistory.length > this.MAX_HISTORY) {
      this.routingHistory.shift();
    }
  }
  
  /**
   * Update agent load
   */
  private updateAgentLoad(agentId: string, delta: number): void {
    const currentLoad = this.agentLoad.get(agentId) || 0;
    this.agentLoad.set(agentId, Math.max(0, currentLoad + delta));
  }
  
  /**
   * Task completion handler
   */
  onTaskCompleted(taskId: string, agentId: string): void {
    this.updateAgentLoad(agentId, -1);
    this.emit('task:completed', { taskId, agentId });
  }
}

// Export singleton instance
export const taskRouter = new TaskRouter();