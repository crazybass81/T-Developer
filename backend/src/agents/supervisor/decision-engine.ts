interface Decision {
  agentName: string;
  confidence: number;
  reasoning: string;
  alternativeAgents?: string[];
}

interface Intent {
  description: string;
  type: string;
  priority: number;
  requirements: string[];
}

interface MLPrediction {
  agentName: string;
  confidence: number;
  features: string[];
}

interface HistoricalPattern {
  intentType: string;
  successfulAgents: string[];
  averagePerformance: number;
  frequency: number;
}

export class DecisionEngine {
  private modelEndpoint: string;
  private decisionHistory: Map<string, Decision[]> = new Map();
  private performanceMetrics: Map<string, number> = new Map();
  private agentCapabilities: Map<string, string[]> = new Map();

  constructor(modelEndpoint?: string) {
    this.modelEndpoint = modelEndpoint || 'http://localhost:8080/predict';
    this.initializeAgentCapabilities();
  }

  async determineAgents(intent: Intent): Promise<Decision[]> {
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

  private matchByRules(intent: Intent): Decision[] {
    const rules = [
      { pattern: /code|implement|develop|build|create/i, agents: ['CodeAgent'], confidence: 0.9 },
      { pattern: /test|verify|validate|check|quality/i, agents: ['TestAgent'], confidence: 0.85 },
      { pattern: /design|architect|structure|plan/i, agents: ['DesignAgent'], confidence: 0.8 },
      { pattern: /security|vulnerabilit|audit|protect/i, agents: ['SecurityAgent'], confidence: 0.9 },
      { pattern: /ui|interface|frontend|react|vue/i, agents: ['UIAgent'], confidence: 0.85 },
      { pattern: /api|backend|server|database/i, agents: ['APIAgent'], confidence: 0.85 },
      { pattern: /deploy|infrastructure|aws|cloud/i, agents: ['DeploymentAgent'], confidence: 0.8 }
    ];

    const matches: Decision[] = [];
    
    for (const rule of rules) {
      if (rule.pattern.test(intent.description)) {
        for (const agentName of rule.agents) {
          matches.push({
            agentName,
            confidence: rule.confidence,
            reasoning: `Rule-based match: ${rule.pattern.source}`,
            alternativeAgents: this.findAlternativeAgents(agentName)
          });
        }
      }
    }

    // 요구사항 기반 추가 매칭
    for (const requirement of intent.requirements) {
      const reqMatches = this.matchRequirement(requirement);
      matches.push(...reqMatches);
    }

    return matches;
  }

  private async predictAgents(intent: Intent): Promise<MLPrediction[]> {
    try {
      // 특징 추출
      const features = this.extractFeatures(intent);
      
      // ML 모델 호출 (실제 환경에서는 AWS Bedrock 등 사용)
      const predictions = await this.callMLModel(features);
      
      return predictions;
    } catch (error) {
      console.warn('ML prediction failed, using fallback:', error.message);
      return this.getFallbackPredictions(intent);
    }
  }

  private analyzeHistory(intent: Intent): HistoricalPattern[] {
    const patterns: HistoricalPattern[] = [];
    const historyKey = this.getHistoryKey(intent);
    
    const pastDecisions = this.decisionHistory.get(historyKey) || [];
    
    if (pastDecisions.length > 0) {
      // 성공률이 높은 에이전트 식별
      const agentSuccess = new Map<string, { success: number; total: number }>();
      
      pastDecisions.forEach(decision => {
        const performance = this.performanceMetrics.get(decision.agentName) || 0.5;
        const stats = agentSuccess.get(decision.agentName) || { success: 0, total: 0 };
        
        stats.total++;
        if (performance > 0.7) stats.success++;
        
        agentSuccess.set(decision.agentName, stats);
      });

      // 패턴 생성
      agentSuccess.forEach((stats, agentName) => {
        if (stats.total >= 2) { // 최소 2회 이상 사용된 에이전트
          patterns.push({
            intentType: intent.type,
            successfulAgents: [agentName],
            averagePerformance: stats.success / stats.total,
            frequency: stats.total
          });
        }
      });
    }

    return patterns;
  }

  private combineDecisions(
    ruleBasedAgents: Decision[],
    mlPredictions: MLPrediction[],
    historicalPatterns: HistoricalPattern[]
  ): Decision[] {
    const combinedDecisions = new Map<string, Decision>();

    // 규칙 기반 결정 추가
    ruleBasedAgents.forEach(decision => {
      combinedDecisions.set(decision.agentName, decision);
    });

    // ML 예측 결과 통합
    mlPredictions.forEach(prediction => {
      const existing = combinedDecisions.get(prediction.agentName);
      if (existing) {
        // 신뢰도 가중 평균
        existing.confidence = (existing.confidence * 0.6) + (prediction.confidence * 0.4);
        existing.reasoning += ` + ML prediction (${prediction.confidence.toFixed(2)})`;
      } else {
        combinedDecisions.set(prediction.agentName, {
          agentName: prediction.agentName,
          confidence: prediction.confidence * 0.7, // ML만으로는 신뢰도 낮춤
          reasoning: `ML prediction based on features: ${prediction.features.join(', ')}`,
          alternativeAgents: this.findAlternativeAgents(prediction.agentName)
        });
      }
    });

    // 히스토리 패턴 적용
    historicalPatterns.forEach(pattern => {
      pattern.successfulAgents.forEach(agentName => {
        const existing = combinedDecisions.get(agentName);
        if (existing) {
          // 히스토리 성능으로 신뢰도 조정
          const historyBoost = pattern.averagePerformance * 0.2;
          existing.confidence = Math.min(0.95, existing.confidence + historyBoost);
          existing.reasoning += ` + Historical success (${pattern.averagePerformance.toFixed(2)})`;
        }
      });
    });

    // 신뢰도 순으로 정렬하고 상위 3개 반환
    return Array.from(combinedDecisions.values())
      .sort((a, b) => b.confidence - a.confidence)
      .slice(0, 3);
  }

  private extractFeatures(intent: Intent): string[] {
    const features = [];
    const text = intent.description.toLowerCase();
    
    // 기술 키워드
    const techKeywords = ['react', 'vue', 'angular', 'node', 'python', 'java', 'aws', 'docker'];
    techKeywords.forEach(keyword => {
      if (text.includes(keyword)) features.push(`tech_${keyword}`);
    });

    // 액션 키워드
    const actionKeywords = ['build', 'create', 'develop', 'test', 'deploy', 'design'];
    actionKeywords.forEach(keyword => {
      if (text.includes(keyword)) features.push(`action_${keyword}`);
    });

    // 복잡도 추정
    if (text.length > 200) features.push('complexity_high');
    else if (text.length > 100) features.push('complexity_medium');
    else features.push('complexity_low');

    // 우선순위
    features.push(`priority_${intent.priority}`);

    return features;
  }

  private async callMLModel(features: string[]): Promise<MLPrediction[]> {
    // 실제 환경에서는 AWS Bedrock, SageMaker 등 사용
    // 여기서는 간단한 휴리스틱으로 시뮬레이션
    const predictions: MLPrediction[] = [];
    
    if (features.includes('action_build') || features.includes('action_create')) {
      predictions.push({
        agentName: 'CodeAgent',
        confidence: 0.8,
        features: features.filter(f => f.startsWith('action_') || f.startsWith('tech_'))
      });
    }

    if (features.includes('tech_react') || features.includes('tech_vue')) {
      predictions.push({
        agentName: 'UIAgent',
        confidence: 0.75,
        features: features.filter(f => f.startsWith('tech_'))
      });
    }

    return predictions;
  }

  private getFallbackPredictions(intent: Intent): MLPrediction[] {
    return [{
      agentName: 'GeneralAgent',
      confidence: 0.5,
      features: ['fallback']
    }];
  }

  private matchRequirement(requirement: string): Decision[] {
    const reqMap = {
      'authentication': { agent: 'SecurityAgent', confidence: 0.9 },
      'database': { agent: 'APIAgent', confidence: 0.8 },
      'user-interface': { agent: 'UIAgent', confidence: 0.9 },
      'api-integration': { agent: 'APIAgent', confidence: 0.85 },
      'testing': { agent: 'TestAgent', confidence: 0.9 },
      'deployment': { agent: 'DeploymentAgent', confidence: 0.85 }
    };

    const match = reqMap[requirement];
    if (match) {
      return [{
        agentName: match.agent,
        confidence: match.confidence,
        reasoning: `Requirement match: ${requirement}`,
        alternativeAgents: this.findAlternativeAgents(match.agent)
      }];
    }

    return [];
  }

  private findAlternativeAgents(primaryAgent: string): string[] {
    const alternatives = {
      'CodeAgent': ['GeneralAgent', 'APIAgent'],
      'UIAgent': ['CodeAgent', 'DesignAgent'],
      'APIAgent': ['CodeAgent', 'GeneralAgent'],
      'TestAgent': ['CodeAgent', 'SecurityAgent'],
      'SecurityAgent': ['TestAgent', 'GeneralAgent'],
      'DesignAgent': ['UIAgent', 'GeneralAgent'],
      'DeploymentAgent': ['GeneralAgent', 'SecurityAgent']
    };

    return alternatives[primaryAgent] || ['GeneralAgent'];
  }

  private initializeAgentCapabilities(): void {
    this.agentCapabilities.set('CodeAgent', ['programming', 'algorithms', 'debugging']);
    this.agentCapabilities.set('UIAgent', ['frontend', 'design', 'user-experience']);
    this.agentCapabilities.set('APIAgent', ['backend', 'databases', 'integration']);
    this.agentCapabilities.set('TestAgent', ['testing', 'quality-assurance', 'validation']);
    this.agentCapabilities.set('SecurityAgent', ['security', 'authentication', 'encryption']);
    this.agentCapabilities.set('DesignAgent', ['architecture', 'system-design', 'planning']);
    this.agentCapabilities.set('DeploymentAgent', ['deployment', 'infrastructure', 'devops']);
  }

  private getHistoryKey(intent: Intent): string {
    return `${intent.type}_${intent.priority}`;
  }

  // 성능 피드백 기록
  recordPerformance(agentName: string, performance: number): void {
    this.performanceMetrics.set(agentName, performance);
  }

  // 결정 히스토리 기록
  recordDecision(intent: Intent, decisions: Decision[]): void {
    const historyKey = this.getHistoryKey(intent);
    this.decisionHistory.set(historyKey, decisions);
  }
}