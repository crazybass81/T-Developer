interface AgentLoad {
  agentId: string;
  currentTasks: number;
  cpuUsage: number;
  memoryUsage: number;
  avgResponseTime: number;
  capacity: number;
}

type BalancingStrategy = 'round-robin' | 'least-connections' | 'weighted-round-robin' | 'resource-based';

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
      case 'round-robin':
        return this.roundRobin(available);
      default:
        return available.map(([id]) => id);
    }
  }
  
  private sortByLeastConnections(agents: [string, AgentLoad][]): string[] {
    return agents
      .sort((a, b) => a[1].currentTasks - b[1].currentTasks)
      .map(([id]) => id);
  }
  
  private weightedRoundRobin(agents: [string, AgentLoad][]): string[] {
    // 가중치 기반 라운드 로빈
    const weighted: string[] = [];
    
    agents.forEach(([id, load]) => {
      const weight = Math.max(1, load.capacity - load.currentTasks);
      for (let i = 0; i < weight; i++) {
        weighted.push(id);
      }
    });
    
    return weighted;
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
  
  private roundRobin(agents: [string, AgentLoad][]): string[] {
    if (agents.length === 0) return [];
    
    const agentIds = agents.map(([id]) => id);
    const selected = agentIds[this.roundRobinIndex % agentIds.length];
    this.roundRobinIndex++;
    
    return [selected, ...agentIds.filter(id => id !== selected)];
  }
  
  private calculateResourceScore(load: AgentLoad): number {
    // 리소스 사용량 종합 점수 (낮을수록 좋음)
    return (
      load.cpuUsage * 0.4 +
      load.memoryUsage * 0.3 +
      (load.currentTasks / load.capacity) * 0.3
    );
  }
  
  async updateAgentLoad(agentId: string, load: Partial<AgentLoad>): Promise<void> {
    const currentLoad = this.agentLoads.get(agentId) || {
      agentId,
      currentTasks: 0,
      cpuUsage: 0,
      memoryUsage: 0,
      avgResponseTime: 0,
      capacity: 5
    };
    
    this.agentLoads.set(agentId, { ...currentLoad, ...load });
  }
  
  private startMonitoring(): void {
    // 초기 에이전트 로드 설정
    this.agentLoads.set('code-agent', {
      agentId: 'code-agent',
      currentTasks: 1,
      cpuUsage: 0.3,
      memoryUsage: 0.4,
      avgResponseTime: 150,
      capacity: 5
    });
    
    this.agentLoads.set('test-agent', {
      agentId: 'test-agent',
      currentTasks: 0,
      cpuUsage: 0.1,
      memoryUsage: 0.2,
      avgResponseTime: 100,
      capacity: 3
    });
    
    // 주기적 모니터링
    setInterval(() => {
      this.collectMetrics();
    }, 10000); // 10초마다
  }
  
  private collectMetrics(): void {
    // 실제 메트릭 수집 로직 (시뮬레이션)
    for (const [agentId, load] of this.agentLoads) {
      const updatedLoad = {
        ...load,
        cpuUsage: Math.random() * 0.8,
        memoryUsage: Math.random() * 0.6,
        avgResponseTime: 100 + Math.random() * 200
      };
      
      this.agentLoads.set(agentId, updatedLoad);
    }
  }
  
  getLoadStats(): Record<string, AgentLoad> {
    return Object.fromEntries(this.agentLoads);
  }
}