import { Intent } from './supervisor-agent';

interface Decision {
  agentName: string;
  confidence: number;
  reasoning: string;
  alternativeAgents?: string[];
}

export class DecisionEngine {
  private decisionHistory: Map<string, Decision[]> = new Map();
  
  async determineAgents(intent: Intent): Promise<Decision[]> {
    // 1. 규칙 기반 매칭
    const ruleBasedAgents = this.matchByRules(intent);
    
    // 2. ML 기반 예측 (간단한 구현)
    const mlPredictions = await this.predictAgents(intent);
    
    // 3. 히스토리 기반 최적화
    const historicalPatterns = this.analyzeHistory(intent);
    
    // 4. 최종 결정
    return this.combineDecisions(
      ruleBasedAgents,
      mlPredictions,
      historicalPatterns
    );
  }
  
  private matchByRules(intent: Intent): Decision[] {
    const rules = [
      { pattern: /code|implement|develop/i, agents: ['CodeAgent'] },
      { pattern: /test|verify|validate/i, agents: ['TestAgent'] },
      { pattern: /design|architect/i, agents: ['DesignAgent'] },
      { pattern: /security|vulnerabilit/i, agents: ['SecurityAgent'] }
    ];
    
    return rules
      .filter(rule => rule.pattern.test(intent.description))
      .map(rule => ({
        agentName: rule.agents[0],
        confidence: 0.8,
        reasoning: `Rule-based match: ${rule.pattern}`
      }));
  }
  
  private async predictAgents(intent: Intent): Promise<Decision[]> {
    // 간단한 ML 예측 시뮬레이션
    const predictions: Decision[] = [];
    
    if (intent.complexity > 0.5) {
      predictions.push({
        agentName: 'ComplexTaskAgent',
        confidence: 0.7,
        reasoning: 'High complexity detected'
      });
    }
    
    return predictions;
  }
  
  private analyzeHistory(intent: Intent): Decision[] {
    const historyKey = intent.type;
    const history = this.decisionHistory.get(historyKey) || [];
    
    // 과거 성공한 에이전트 패턴 분석
    const successfulAgents = history
      .filter(d => d.confidence > 0.8)
      .map(d => d.agentName);
    
    return successfulAgents.map(agentName => ({
      agentName,
      confidence: 0.6,
      reasoning: 'Historical success pattern'
    }));
  }
  
  private combineDecisions(
    ruleBasedAgents: Decision[],
    mlPredictions: Decision[],
    historicalPatterns: Decision[]
  ): Decision[] {
    const allDecisions = [
      ...ruleBasedAgents,
      ...mlPredictions,
      ...historicalPatterns
    ];
    
    // 중복 제거 및 신뢰도 기반 정렬
    const uniqueDecisions = new Map<string, Decision>();
    
    allDecisions.forEach(decision => {
      const existing = uniqueDecisions.get(decision.agentName);
      if (!existing || decision.confidence > existing.confidence) {
        uniqueDecisions.set(decision.agentName, decision);
      }
    });
    
    return Array.from(uniqueDecisions.values())
      .sort((a, b) => b.confidence - a.confidence);
  }
}