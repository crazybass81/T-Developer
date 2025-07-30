class IntelligentRouter {
  constructor() {
    this.routingHistory = new Map();
    this.performanceMetrics = new Map();
  }
  
  async routeTask(task) {
    // 1. 특징 추출
    const features = await this.extractFeatures(task);
    
    // 2. 에이전트 점수 계산
    const agentScores = await this.calculateAgentScores(features);
    
    // 3. 로드 밸런싱 고려
    const availableAgents = await this.getAvailableAgents();
    
    // 4. 최종 선택
    const selectedAgent = this.selectBestAgent(agentScores, availableAgents);
    
    // 5. 라우팅 기록
    await this.recordRoutingDecision(task, selectedAgent);
    
    return selectedAgent;
  }
  
  async extractFeatures(task) {
    return [
      task.description.length / 100, // 복잡도
      task.priority / 10, // 우선순위
      this.getTaskTypeScore(task.type), // 타입 점수
      Date.now() - task.createdAt.getTime(), // 대기 시간
      task.type // 원본 타입 정보 보존
    ];
  }
  
  getTaskTypeFromFeatures(features) {
    // features[4]에 원본 타입 정보가 있음
    return features[4] || 'general';
  }
  
  async calculateAgentScores(features) {
    const agents = ['code-agent', 'test-agent', 'design-agent'];
    
    return agents.map(agentName => {
      let score = 0;
      let reasoning = '';
      
      // 간단한 점수 계산 로직 - task type 기반
      const taskType = this.getTaskTypeFromFeatures(features);
      
      if (agentName === 'code-agent' && taskType === 'code') {
        score = 0.95;
        reasoning = 'Code task matched to code agent';
      } else if (agentName === 'test-agent' && (taskType === 'test' || features[1] > 0.8)) {
        score = 0.9;
        reasoning = 'Test task or high priority matched to test agent';
      } else if (agentName === 'design-agent' && taskType === 'design') {
        score = 0.85;
        reasoning = 'Design task matched to design agent';
      } else {
        score = 0.5;
        reasoning = 'Default scoring';
      }
      
      // 과거 성능 가중치 적용
      const historicalWeight = this.performanceMetrics.get(agentName) || 1.0;
      score *= historicalWeight;
      
      return { agentName, score, reasoning };
    });
  }
  
  async getAvailableAgents() {
    return [
      {
        name: 'code-agent',
        capabilities: ['coding', 'refactoring'],
        currentLoad: 2,
        maxCapacity: 5
      },
      {
        name: 'test-agent',
        capabilities: ['testing', 'validation'],
        currentLoad: 1,
        maxCapacity: 3
      }
    ];
  }
  
  selectBestAgent(scores, availableAgents) {
    // 점수와 가용성을 종합하여 최적 에이전트 선택
    const sortedScores = scores.sort((a, b) => b.score - a.score);
    
    for (const score of sortedScores) {
      const agent = availableAgents.find(a => a.name === score.agentName);
      if (agent && agent.currentLoad < agent.maxCapacity) {
        return agent;
      }
    }
    
    // 기본 에이전트 반환
    return availableAgents[0];
  }
  
  getTaskTypeScore(type) {
    const typeScores = {
      'code': 0.9,
      'test': 0.85, // Higher score for test tasks
      'design': 0.7,
      'general': 0.5
    };
    
    return typeScores[type] || 0.5;
  }
  
  async recordRoutingDecision(task, agent) {
    this.routingHistory.set(task.id, agent.name);
    console.log(`Task ${task.id} routed to ${agent.name}`);
  }
}

module.exports = { IntelligentRouter };