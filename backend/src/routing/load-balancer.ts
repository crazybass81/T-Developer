export type BalancingStrategy = 'least-connections' | 'weighted-round-robin' | 'resource-based';

export interface AgentLoad {
  agentId: string;
  currentTasks: number;
  cpuUsage: number;
  memoryUsage: number;
  avgResponseTime: number;
  capacity: number;
}

export class LoadBalancer {
  private agentLoads: Map<string, AgentLoad> = new Map();
  private strategy: BalancingStrategy;
  private roundRobinIndex = 0;

  constructor(strategy: BalancingStrategy = 'weighted-round-robin') {
    this.strategy = strategy;
    this.startMonitoring();
  }

  async getAvailableAgents(): Promise<string[]> {
    const agents = Array.from(this.agentLoads.entries());
    
    // 용량이 남은 에이전트 필터링
    const available = agents.filter(([_, load]) => 
      load.currentTasks < load.capacity * 0.8
    );
    
    // 전략에 따라 정렬
    switch (this.strategy) {
      case 'least-connections':
        return this.sortByLeastConnections(available);
      case 'weighted-round-robin':
        return this.weightedRoundRobin(available);
      case 'resource-based':
        return this.sortByResourceUsage(available);
      default:
        return available.map(([id]) => id);
    }
  }

  updateAgentLoad(agentId: string, load: AgentLoad): void {
    this.agentLoads.set(agentId, load);
  }

  private sortByLeastConnections(agents: [string, AgentLoad][]): string[] {
    return agents
      .sort((a, b) => a[1].currentTasks - b[1].currentTasks)
      .map(([id]) => id);
  }

  private weightedRoundRobin(agents: [string, AgentLoad][]): string[] {
    return agents
      .sort((a, b) => {
        const weightA = this.calculateWeight(a[1]);
        const weightB = this.calculateWeight(b[1]);
        return weightB - weightA;
      })
      .map(([id]) => id);
  }

  private sortByResourceUsage(agents: [string, AgentLoad][]): string[] {
    return agents
      .sort((a, b) => {
        const scoreA = this.calculateResourceScore(a[1]);
        const scoreB = this.calculateResourceScore(b[1]);
        return scoreA - scoreB;
      })
      .map(([id]) => id);
  }

  private calculateResourceScore(load: AgentLoad): number {
    // 리소스 사용량 종합 점수
    return (
      load.cpuUsage * 0.4 +
      load.memoryUsage * 0.3 +
      (load.currentTasks / load.capacity) * 0.3
    );
  }

  private calculateWeight(load: AgentLoad): number {
    const utilizationRate = load.currentTasks / load.capacity;
    const resourceScore = (load.cpuUsage + load.memoryUsage) / 2;
    return Math.max(0, 1 - (utilizationRate * 0.6 + resourceScore * 0.4));
  }

  private startMonitoring(): void {
    // 모니터링 로직 구현
  }

  getMetrics() {
    const agents = Array.from(this.agentLoads.values());
    return {
      totalAgents: agents.length,
      totalTasks: agents.reduce((sum, a) => sum + a.currentTasks, 0),
      avgCpuUsage: agents.reduce((sum, a) => sum + a.cpuUsage, 0) / agents.length || 0
    };
  }
}