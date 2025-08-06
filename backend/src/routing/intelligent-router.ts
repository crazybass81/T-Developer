interface Task {
  id: string;
  type: string;
  description: string;
  requirements: string[];
  priority: number;
  createdAt: number;
}

interface Agent {
  id: string;
  type: string;
  capabilities: string[];
  currentLoad: number;
  maxCapacity: number;
  performance: number;
}

interface RoutingDecision {
  taskId: string;
  selectedAgent: string;
  score: number;
  reasoning: string;
  timestamp: number;
}

export class IntelligentRouter {
  private agents: Map<string, Agent> = new Map();
  private routingHistory: RoutingDecision[] = [];
  private performanceWeights = { capability: 0.4, load: 0.3, performance: 0.3 };

  async routeTask(task: Task): Promise<Agent> {
    // 1. Get available agents
    const availableAgents = this.getAvailableAgents();
    
    // 2. Calculate scores for each agent
    const agentScores = await this.calculateAgentScores(task, availableAgents);
    
    // 3. Select best agent
    const selectedAgent = this.selectBestAgent(agentScores);
    
    // 4. Record decision
    await this.recordRoutingDecision(task, selectedAgent, agentScores);
    
    return selectedAgent;
  }

  private getAvailableAgents(): Agent[] {
    return Array.from(this.agents.values())
      .filter(agent => agent.currentLoad < agent.maxCapacity * 0.8);
  }

  private async calculateAgentScores(task: Task, agents: Agent[]): Promise<Map<string, number>> {
    const scores = new Map<string, number>();

    for (const agent of agents) {
      // Capability match score
      const capabilityScore = this.calculateCapabilityMatch(task, agent);
      
      // Load balance score
      const loadScore = 1 - (agent.currentLoad / agent.maxCapacity);
      
      // Historical performance score
      const performanceScore = await this.getHistoricalPerformance(agent.id, task.type);
      
      // Weighted final score
      const finalScore = 
        capabilityScore * this.performanceWeights.capability +
        loadScore * this.performanceWeights.load +
        performanceScore * this.performanceWeights.performance;

      scores.set(agent.id, finalScore);
    }

    return scores;
  }

  private calculateCapabilityMatch(task: Task, agent: Agent): number {
    const taskRequirements = new Set(task.requirements);
    const agentCapabilities = new Set(agent.capabilities);
    
    const intersection = new Set([...taskRequirements].filter(x => agentCapabilities.has(x)));
    return intersection.size / taskRequirements.size;
  }

  private async getHistoricalPerformance(agentId: string, taskType: string): Promise<number> {
    const recentDecisions = this.routingHistory
      .filter(d => d.selectedAgent === agentId)
      .slice(-10); // Last 10 decisions

    if (recentDecisions.length === 0) return 0.5; // Default score

    const avgScore = recentDecisions.reduce((sum, d) => sum + d.score, 0) / recentDecisions.length;
    return Math.min(avgScore * 1.1, 1.0); // Slight boost for consistent performers
  }

  private selectBestAgent(scores: Map<string, number>): Agent {
    let bestAgentId = '';
    let bestScore = -1;

    for (const [agentId, score] of scores) {
      if (score > bestScore) {
        bestScore = score;
        bestAgentId = agentId;
      }
    }

    const agent = this.agents.get(bestAgentId);
    if (!agent) throw new Error(`Agent ${bestAgentId} not found`);
    
    return agent;
  }

  private async recordRoutingDecision(task: Task, agent: Agent, scores: Map<string, number>): Promise<void> {
    const decision: RoutingDecision = {
      taskId: task.id,
      selectedAgent: agent.id,
      score: scores.get(agent.id) || 0,
      reasoning: `Selected ${agent.type} agent with score ${scores.get(agent.id)?.toFixed(3)}`,
      timestamp: Date.now()
    };

    this.routingHistory.push(decision);
    
    // Keep only last 1000 decisions
    if (this.routingHistory.length > 1000) {
      this.routingHistory = this.routingHistory.slice(-1000);
    }
  }

  // Agent management
  registerAgent(agent: Agent): void {
    this.agents.set(agent.id, agent);
  }

  updateAgentLoad(agentId: string, newLoad: number): void {
    const agent = this.agents.get(agentId);
    if (agent) {
      agent.currentLoad = newLoad;
    }
  }

  getRoutingStats(): { totalRouted: number; avgScore: number; agentUtilization: Record<string, number> } {
    const totalRouted = this.routingHistory.length;
    const avgScore = totalRouted > 0 
      ? this.routingHistory.reduce((sum, d) => sum + d.score, 0) / totalRouted 
      : 0;

    const agentUtilization: Record<string, number> = {};
    for (const [id, agent] of this.agents) {
      agentUtilization[id] = agent.currentLoad / agent.maxCapacity;
    }

    return { totalRouted, avgScore, agentUtilization };
  }
}