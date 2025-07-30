class LoadBalancer {
  constructor(strategy = 'weighted-round-robin') {
    this.agentLoads = new Map();
    this.strategy = strategy;
    this.roundRobinIndex = 0;
    this.startMonitoring();
  }
  
  async getAvailableAgents() {
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
  
  sortByLeastConnections(agents) {
    return agents
      .sort((a, b) => a[1].currentTasks - b[1].currentTasks)
      .map(([id]) => id);
  }
  
  weightedRoundRobin(agents) {
    // 가중치 기반 라운드 로빈
    const weighted = [];
    
    agents.forEach(([id, load]) => {
      const weight = Math.max(1, load.capacity - load.currentTasks);
      for (let i = 0; i < weight; i++) {
        weighted.push(id);
      }
    });
    
    return weighted;
  }
  
  sortByResourceUsage(agents) {
    return agents
      .sort((a, b) => {
        const scoreA = this.calculateResourceScore(a[1]);
        const scoreB = this.calculateResourceScore(b[1]);
        return scoreA - scoreB;
      })
      .map(([id]) => id);
  }
  
  roundRobin(agents) {
    if (agents.length === 0) return [];
    
    const agentIds = agents.map(([id]) => id);
    const selected = agentIds[this.roundRobinIndex % agentIds.length];
    this.roundRobinIndex++;
    
    return [selected, ...agentIds.filter(id => id !== selected)];
  }
  
  calculateResourceScore(load) {
    // 리소스 사용량 종합 점수 (낮을수록 좋음)
    return (
      load.cpuUsage * 0.4 +
      load.memoryUsage * 0.3 +
      (load.currentTasks / load.capacity) * 0.3
    );
  }
  
  async updateAgentLoad(agentId, load) {
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
  
  startMonitoring() {
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
  }
  
  getLoadStats() {
    return Object.fromEntries(this.agentLoads);
  }
}

module.exports = { LoadBalancer };