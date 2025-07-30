interface Task {
  id: string;
  type: string;
  description: string;
  priority: number;
  createdAt: Date;
}

interface Agent {
  name: string;
  capabilities: string[];
  currentLoad: number;
  maxCapacity: number;
}

interface RoutingScore {
  agentName: string;
  score: number;
  reasoning: string;
}

export class IntelligentRouter {
  private routingHistory: Map<string, string> = new Map();
  private performanceMetrics: Map<string, number> = new Map();
  
  async routeTask(task: Task): Promise<Agent> {
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
  
  private async extractFeatures(task: Task): Promise<number[]> {
    return [
      task.description.length / 100, // 복잡도
      task.priority / 10, // 우선순위
      this.getTaskTypeScore(task.type), // 타입 점수
      Date.now() - task.createdAt.getTime() // 대기 시간
    ];
  }
  
  private async calculateAgentScores(features: number[]): Promise<RoutingScore[]> {
    const agents = ['code-agent', 'test-agent', 'design-agent'];
    
    return agents.map(agentName => {
      let score = 0;
      let reasoning = '';
      
      // 간단한 점수 계산 로직
      if (agentName === 'code-agent' && features[2] > 0.7) {
        score = 0.9;
        reasoning = 'High code complexity detected';
      } else if (agentName === 'test-agent' && features[1] > 0.8) {
        score = 0.8;
        reasoning = 'High priority testing task';
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
  
  private async getAvailableAgents(): Promise<Agent[]> {
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
  
  private selectBestAgent(scores: RoutingScore[], availableAgents: Agent[]): Agent {
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
  
  private getTaskTypeScore(type: string): number {
    const typeScores: Record<string, number> = {
      'code': 0.9,
      'test': 0.8,
      'design': 0.7,
      'general': 0.5
    };
    
    return typeScores[type] || 0.5;
  }
  
  private async recordRoutingDecision(task: Task, agent: Agent): Promise<void> {
    this.routingHistory.set(task.id, agent.name);
    console.log(`Task ${task.id} routed to ${agent.name}`);
  }
}