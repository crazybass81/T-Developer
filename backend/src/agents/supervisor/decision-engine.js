class DecisionEngine {
  constructor() {
    this.decisionHistory = new Map();
  }
  
  async determineAgents(intent) {
    // 1. 규칙 기반 매칭
    const ruleBasedAgents = this.matchByRules(intent);
    
    // 2. ML 기반 예측
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
  
  matchByRules(intent) {
    const rules = [
      { pattern: /code|implement|develop/i, agents: ['CodeAgent'] },
      { pattern: /test|verify|validate/i, agents: ['TestAgent'] },
      { pattern: /design|architect/i, agents: ['DesignAgent'] },
      { pattern: /security|vulnerabilit|secure/i, agents: ['SecurityAgent'] }
    ];
    
    return rules
      .filter(rule => rule.pattern.test(intent.description))
      .map(rule => ({
        agentName: rule.agents[0],
        confidence: 0.8,
        reasoning: `Rule-based match: ${rule.pattern}`
      }));
  }
  
  async predictAgents(intent) {
    const predictions = [];
    
    if (intent.complexity > 0.5) {
      predictions.push({
        agentName: 'ComplexTaskAgent',
        confidence: 0.7,
        reasoning: 'High complexity detected'
      });
    }
    
    return predictions;
  }
  
  analyzeHistory(intent) {
    const historyKey = intent.type;
    const history = this.decisionHistory.get(historyKey) || [];
    
    const successfulAgents = history
      .filter(d => d.confidence > 0.8)
      .map(d => d.agentName);
    
    return successfulAgents.map(agentName => ({
      agentName,
      confidence: 0.6,
      reasoning: 'Historical success pattern'
    }));
  }
  
  combineDecisions(ruleBasedAgents, mlPredictions, historicalPatterns) {
    const allDecisions = [
      ...ruleBasedAgents,
      ...mlPredictions,
      ...historicalPatterns
    ];
    
    const uniqueDecisions = new Map();
    
    allDecisions.forEach(decision => {
      const existing = uniqueDecisions.get(decision.agentName);
      if (!existing || decision.confidence > existing.confidence) {
        uniqueDecisions.set(decision.agentName, decision);
      }
    });
    
    return Array.from(uniqueDecisions.values())
      .sort((a, b) => b.confidence - a.confidence);
  }
  
  recordDecision(intent, decision) {
    const historyKey = intent.type;
    const history = this.decisionHistory.get(historyKey) || [];
    history.push(decision);
    this.decisionHistory.set(historyKey, history);
  }
}

module.exports = { DecisionEngine };