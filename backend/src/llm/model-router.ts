/**
 * 모델 선택 및 라우팅 엔진
 */

interface ModelCapabilities {
  contextLength: number;
  supportedLanguages: string[];
  specialties: string[];
  costPerToken: number;
  latency: 'low' | 'medium' | 'high';
  availability: number;  // 0-1
}

interface RoutingCriteria {
  taskType: string;
  requiredContext: number;
  targetLanguage?: string;
  maxCost?: number;
  maxLatency?: 'low' | 'medium' | 'high';
  requiredCapabilities?: string[];
}

interface ModelScore {
  model: string;
  score: number;
  reasoning: string[];
}

export class ModelRouter {
  private modelRegistry: Map<string, ModelCapabilities> = new Map();
  private performanceHistory: Map<string, any[]> = new Map();
  private selectionHistory: Array<{model: string, criteria: RoutingCriteria, timestamp: Date}> = [];
  
  constructor() {
    this.initializeModelRegistry();
  }
  
  private initializeModelRegistry(): void {
    // OpenAI 모델들
    this.modelRegistry.set('gpt-4', {
      contextLength: 128000,
      supportedLanguages: ['all'],
      specialties: ['reasoning', 'coding', 'analysis'],
      costPerToken: 0.00003,
      latency: 'medium',
      availability: 0.99
    });
    
    this.modelRegistry.set('gpt-3.5-turbo', {
      contextLength: 16385,
      supportedLanguages: ['all'],
      specialties: ['general', 'fast-response'],
      costPerToken: 0.000002,
      latency: 'low',
      availability: 0.995
    });
    
    // Anthropic 모델들
    this.modelRegistry.set('claude-3-opus', {
      contextLength: 200000,
      supportedLanguages: ['all'],
      specialties: ['long-context', 'analysis', 'creative'],
      costPerToken: 0.000015,
      latency: 'low',
      availability: 0.98
    });
    
    this.modelRegistry.set('claude-3-sonnet', {
      contextLength: 200000,
      supportedLanguages: ['all'],
      specialties: ['balanced', 'coding', 'analysis'],
      costPerToken: 0.000003,
      latency: 'low',
      availability: 0.99
    });
    
    // AWS Bedrock 모델들
    this.modelRegistry.set('bedrock-claude-3', {
      contextLength: 200000,
      supportedLanguages: ['all'],
      specialties: ['enterprise', 'secure', 'analysis'],
      costPerToken: 0.000008,
      latency: 'medium',
      availability: 0.97
    });
    
    this.modelRegistry.set('bedrock-titan', {
      contextLength: 32000,
      supportedLanguages: ['all'],
      specialties: ['aws-native', 'cost-effective'],
      costPerToken: 0.0000008,
      latency: 'medium',
      availability: 0.98
    });
    
    // 추가 모델들 (25+ 모델 지원)
    const additionalModels = [
      'cohere-command', 'huggingface-llama2', 'ai21-jurassic',
      'google-palm', 'aleph-alpha-luminous', 'together-llama',
      'replicate-llama', 'mistral-7b', 'falcon-40b'
    ];
    
    additionalModels.forEach(model => {
      this.modelRegistry.set(model, {
        contextLength: 4096,
        supportedLanguages: ['en'],
        specialties: ['general'],
        costPerToken: 0.000001,
        latency: 'medium',
        availability: 0.95
      });
    });
  }
  
  async selectModel(criteria: RoutingCriteria): Promise<string> {
    const candidates = this.filterCandidates(criteria);
    
    if (candidates.length === 0) {
      throw new Error('No suitable model found for criteria');
    }
    
    // 점수 계산
    const scores = await this.scoreModels(candidates, criteria);
    
    // 최적 모델 선택
    const bestModel = this.selectBestModel(scores);
    
    // 선택 기록
    await this.recordSelection(bestModel, criteria);
    
    return bestModel;
  }
  
  private filterCandidates(criteria: RoutingCriteria): string[] {
    const candidates = [];
    
    for (const [model, capabilities] of this.modelRegistry) {
      // 컨텍스트 길이 확인
      if (capabilities.contextLength < criteria.requiredContext) {
        continue;
      }
      
      // 언어 지원 확인
      if (criteria.targetLanguage && 
          !capabilities.supportedLanguages.includes('all') &&
          !capabilities.supportedLanguages.includes(criteria.targetLanguage)) {
        continue;
      }
      
      // 지연시간 요구사항 확인
      if (criteria.maxLatency) {
        const latencyOrder = ['low', 'medium', 'high'];
        if (latencyOrder.indexOf(capabilities.latency) > 
            latencyOrder.indexOf(criteria.maxLatency)) {
          continue;
        }
      }
      
      // 비용 제한 확인
      if (criteria.maxCost && capabilities.costPerToken > criteria.maxCost) {
        continue;
      }
      
      candidates.push(model);
    }
    
    return candidates;
  }
  
  private async scoreModels(
    candidates: string[], 
    criteria: RoutingCriteria
  ): Promise<ModelScore[]> {
    const scores: ModelScore[] = [];
    
    for (const model of candidates) {
      const capabilities = this.modelRegistry.get(model)!;
      let score = 0;
      const reasoning: string[] = [];
      
      // 전문성 점수 (30%)
      const specialtyScore = this.calculateSpecialtyScore(
        capabilities.specialties,
        criteria.taskType
      );
      score += specialtyScore * 0.3;
      reasoning.push(`Specialty match: ${specialtyScore.toFixed(2)}`);
      
      // 비용 점수 (20%)
      if (criteria.maxCost) {
        const costScore = Math.max(0, 1 - (capabilities.costPerToken / criteria.maxCost));
        score += costScore * 0.2;
        reasoning.push(`Cost efficiency: ${costScore.toFixed(2)}`);
      }
      
      // 성능 이력 점수 (30%)
      const performanceScore = await this.getPerformanceScore(model);
      score += performanceScore * 0.3;
      reasoning.push(`Performance history: ${performanceScore.toFixed(2)}`);
      
      // 가용성 점수 (20%)
      score += capabilities.availability * 0.2;
      reasoning.push(`Availability: ${capabilities.availability}`);
      
      scores.push({
        model,
        score,
        reasoning
      });
    }
    
    return scores.sort((a, b) => b.score - a.score);
  }
  
  private calculateSpecialtyScore(
    modelSpecialties: string[],
    taskType: string
  ): number {
    // 태스크 타입별 전문성 매칭
    const taskSpecialtyMap: Record<string, string[]> = {
      'code-generation': ['coding', 'programming', 'development'],
      'analysis': ['analysis', 'reasoning', 'research'],
      'creative': ['creative', 'writing', 'content'],
      'long-context': ['long-context', 'document-analysis'],
      'fast-response': ['fast-response', 'general', 'quick']
    };
    
    const requiredSpecialties = taskSpecialtyMap[taskType] || ['general'];
    
    let matchScore = 0;
    for (const required of requiredSpecialties) {
      if (modelSpecialties.includes(required)) {
        matchScore += 1;
      }
    }
    
    return Math.min(1, matchScore / requiredSpecialties.length);
  }
  
  private async getPerformanceScore(model: string): Promise<number> {
    const history = this.performanceHistory.get(model) || [];
    
    if (history.length === 0) {
      return 0.5; // 기본 점수
    }
    
    // 최근 10개 실행 결과 기준
    const recentHistory = history.slice(-10);
    const successRate = recentHistory.filter(h => h.success).length / recentHistory.length;
    const avgLatency = recentHistory.reduce((sum, h) => sum + h.latency, 0) / recentHistory.length;
    
    // 성공률과 지연시간을 종합한 점수
    const latencyScore = Math.max(0, 1 - (avgLatency / 5000)); // 5초 기준
    return (successRate * 0.7) + (latencyScore * 0.3);
  }
  
  private selectBestModel(scores: ModelScore[]): string {
    if (scores.length === 0) {
      throw new Error('No models to select from');
    }
    
    return scores[0].model;
  }
  
  private async recordSelection(model: string, criteria: RoutingCriteria): Promise<void> {
    this.selectionHistory.push({
      model,
      criteria,
      timestamp: new Date()
    });
    
    // 히스토리 크기 제한 (최근 1000개)
    if (this.selectionHistory.length > 1000) {
      this.selectionHistory = this.selectionHistory.slice(-1000);
    }
  }
  
  // 성능 기록 업데이트
  async recordPerformance(
    model: string,
    success: boolean,
    latency: number,
    error?: string
  ): Promise<void> {
    if (!this.performanceHistory.has(model)) {
      this.performanceHistory.set(model, []);
    }
    
    const history = this.performanceHistory.get(model)!;
    history.push({
      success,
      latency,
      error,
      timestamp: new Date()
    });
    
    // 히스토리 크기 제한 (최근 100개)
    if (history.length > 100) {
      this.performanceHistory.set(model, history.slice(-100));
    }
  }
  
  // 라우팅 통계
  getRoutingStats(): any {
    const modelCounts = new Map<string, number>();
    
    this.selectionHistory.forEach(entry => {
      const count = modelCounts.get(entry.model) || 0;
      modelCounts.set(entry.model, count + 1);
    });
    
    return {
      totalSelections: this.selectionHistory.length,
      modelDistribution: Object.fromEntries(modelCounts),
      availableModels: Array.from(this.modelRegistry.keys()),
      performanceData: Object.fromEntries(this.performanceHistory)
    };
  }
}