import { ModelProvider, ModelConfig, ModelResponse, ModelMetricsCollector } from './model-provider';
import { ModelProviderFactory } from './model-provider';

export interface ModelCapabilities {
  contextLength: number;
  supportedLanguages: string[];
  specialties: string[];
  costPerToken: number;
  latency: 'low' | 'medium' | 'high';
  availability: number; // 0-1
  qualityScore: number; // 0-1
}

export interface RoutingCriteria {
  taskType: string;
  requiredContext: number;
  targetLanguage?: string;
  maxCost?: number;
  maxLatency?: 'low' | 'medium' | 'high';
  requiredCapabilities?: string[];
  qualityThreshold?: number;
}

export interface RoutingDecision {
  selectedModel: string;
  provider: string;
  confidence: number;
  reasoning: string;
  alternatives: Array<{
    model: string;
    provider: string;
    score: number;
  }>;
}

export class ModelRouter {
  private modelRegistry: Map<string, ModelCapabilities>;
  private providerInstances: Map<string, ModelProvider>;
  private metricsCollector: ModelMetricsCollector;
  private loadBalancer: ModelLoadBalancer;
  
  constructor() {
    this.modelRegistry = new Map();
    this.providerInstances = new Map();
    this.metricsCollector = new ModelMetricsCollector();
    this.loadBalancer = new ModelLoadBalancer();
    
    this.initializeModelRegistry();
  }
  
  private initializeModelRegistry(): void {
    // OpenAI 모델들
    this.modelRegistry.set('gpt-4', {
      contextLength: 128000,
      supportedLanguages: ['all'],
      specialties: ['reasoning', 'coding', 'analysis', 'creative'],
      costPerToken: 0.00003,
      latency: 'medium',
      availability: 0.99,
      qualityScore: 0.95
    });
    
    this.modelRegistry.set('gpt-4-turbo', {
      contextLength: 128000,
      supportedLanguages: ['all'],
      specialties: ['reasoning', 'coding', 'analysis', 'speed'],
      costPerToken: 0.00001,
      latency: 'low',
      availability: 0.98,
      qualityScore: 0.93
    });
    
    this.modelRegistry.set('gpt-3.5-turbo', {
      contextLength: 16385,
      supportedLanguages: ['all'],
      specialties: ['general', 'speed', 'cost-effective'],
      costPerToken: 0.0000015,
      latency: 'low',
      availability: 0.99,
      qualityScore: 0.85
    });
    
    // Anthropic 모델들
    this.modelRegistry.set('claude-3-opus-20240229', {
      contextLength: 200000,
      supportedLanguages: ['all'],
      specialties: ['long-context', 'analysis', 'creative', 'reasoning'],
      costPerToken: 0.000015,
      latency: 'medium',
      availability: 0.97,
      qualityScore: 0.96
    });
    
    this.modelRegistry.set('claude-3-sonnet-20240229', {
      contextLength: 200000,
      supportedLanguages: ['all'],
      specialties: ['balanced', 'coding', 'analysis'],
      costPerToken: 0.000003,
      latency: 'low',
      availability: 0.98,
      qualityScore: 0.92
    });
    
    this.modelRegistry.set('claude-3-haiku-20240307', {
      contextLength: 200000,
      supportedLanguages: ['all'],
      specialties: ['speed', 'cost-effective', 'simple-tasks'],
      costPerToken: 0.00000025,
      latency: 'low',
      availability: 0.99,
      qualityScore: 0.88
    });
    
    // Bedrock 모델들
    this.modelRegistry.set('anthropic.claude-3-opus-20240229-v1:0', {
      contextLength: 200000,
      supportedLanguages: ['all'],
      specialties: ['long-context', 'analysis', 'aws-native'],
      costPerToken: 0.000015,
      latency: 'medium',
      availability: 0.96,
      qualityScore: 0.95
    });
    
    this.modelRegistry.set('amazon.titan-text-express-v1', {
      contextLength: 8000,
      supportedLanguages: ['en', 'es', 'fr', 'de', 'it', 'pt'],
      specialties: ['aws-native', 'cost-effective', 'general'],
      costPerToken: 0.0000008,
      latency: 'low',
      availability: 0.98,
      qualityScore: 0.82
    });
  }
  
  async selectModel(criteria: RoutingCriteria): Promise<RoutingDecision> {
    // 1. 후보 모델 필터링
    const candidates = this.filterCandidates(criteria);
    
    if (candidates.length === 0) {
      throw new Error('No suitable model found for the given criteria');
    }
    
    // 2. 모델 점수 계산
    const scores = await this.scoreModels(candidates, criteria);
    
    // 3. 로드 밸런싱 고려
    const availableModels = await this.loadBalancer.getAvailableModels(candidates);
    
    // 4. 최종 선택
    const decision = this.makeFinalDecision(scores, availableModels, criteria);
    
    // 5. 선택 기록
    await this.recordSelection(decision, criteria);
    
    return decision;
  }
  
  private filterCandidates(criteria: RoutingCriteria): string[] {
    const candidates: string[] = [];
    
    for (const [modelName, capabilities] of this.modelRegistry) {
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
      
      // 비용 제한 확인
      if (criteria.maxCost && capabilities.costPerToken > criteria.maxCost) {
        continue;
      }
      
      // 지연시간 요구사항 확인
      if (criteria.maxLatency) {
        const latencyOrder = ['low', 'medium', 'high'];
        const maxIndex = latencyOrder.indexOf(criteria.maxLatency);
        const modelIndex = latencyOrder.indexOf(capabilities.latency);
        
        if (modelIndex > maxIndex) {
          continue;
        }
      }
      
      // 품질 임계값 확인
      if (criteria.qualityThreshold && 
          capabilities.qualityScore < criteria.qualityThreshold) {
        continue;
      }
      
      // 필수 기능 확인
      if (criteria.requiredCapabilities) {
        const hasAllCapabilities = criteria.requiredCapabilities.every(cap =>
          capabilities.specialties.includes(cap)
        );
        if (!hasAllCapabilities) {
          continue;
        }
      }
      
      candidates.push(modelName);
    }
    
    return candidates;
  }
  
  private async scoreModels(
    candidates: string[],
    criteria: RoutingCriteria
  ): Promise<Map<string, number>> {
    const scores = new Map<string, number>();
    
    for (const modelName of candidates) {
      const capabilities = this.modelRegistry.get(modelName)!;
      let score = 0;
      
      // 전문성 점수 (40%)
      const specialtyScore = this.calculateSpecialtyScore(
        capabilities.specialties,
        criteria.taskType
      );
      score += specialtyScore * 0.4;
      
      // 비용 효율성 점수 (20%)
      const costScore = this.calculateCostScore(
        capabilities.costPerToken,
        criteria.maxCost
      );
      score += costScore * 0.2;
      
      // 성능 이력 점수 (20%)
      const performanceScore = await this.getPerformanceScore(modelName);
      score += performanceScore * 0.2;
      
      // 가용성 점수 (10%)
      score += capabilities.availability * 0.1;
      
      // 품질 점수 (10%)
      score += capabilities.qualityScore * 0.1;
      
      scores.set(modelName, score);
    }
    
    return scores;
  }
  
  private calculateSpecialtyScore(
    specialties: string[],
    taskType: string
  ): number {
    // 태스크 타입과 전문성 매칭
    const taskSpecialtyMap: Record<string, string[]> = {
      'code-generation': ['coding', 'reasoning'],
      'text-analysis': ['analysis', 'reasoning'],
      'creative-writing': ['creative', 'general'],
      'translation': ['general', 'multilingual'],
      'summarization': ['analysis', 'general'],
      'question-answering': ['reasoning', 'general'],
      'long-document': ['long-context', 'analysis']
    };
    
    const relevantSpecialties = taskSpecialtyMap[taskType] || ['general'];
    
    let matchScore = 0;
    for (const specialty of relevantSpecialties) {
      if (specialties.includes(specialty)) {
        matchScore += 1;
      }
    }
    
    return Math.min(matchScore / relevantSpecialties.length, 1.0);
  }
  
  private calculateCostScore(
    modelCost: number,
    maxCost?: number
  ): number {
    if (!maxCost) return 0.5; // 중립적 점수
    
    // 비용이 낮을수록 높은 점수
    return Math.max(0, 1 - (modelCost / maxCost));
  }
  
  private async getPerformanceScore(modelName: string): Promise<number> {
    const metrics = this.metricsCollector.getMetrics();
    const modelMetrics = metrics.find(m => m.model === modelName);
    
    if (!modelMetrics) return 0.5; // 기본 점수
    
    // 성공률과 지연시간을 고려한 점수
    const successScore = modelMetrics.successRate;
    const latencyScore = Math.max(0, 1 - (modelMetrics.averageLatency / 10000)); // 10초 기준
    
    return (successScore * 0.7) + (latencyScore * 0.3);
  }
  
  private makeFinalDecision(
    scores: Map<string, number>,
    availableModels: string[],
    criteria: RoutingCriteria
  ): RoutingDecision {
    // 사용 가능한 모델 중에서 점수 순으로 정렬
    const sortedCandidates = Array.from(scores.entries())
      .filter(([model]) => availableModels.includes(model))
      .sort(([, scoreA], [, scoreB]) => scoreB - scoreA);
    
    if (sortedCandidates.length === 0) {
      throw new Error('No available models found');
    }
    
    const [selectedModel, selectedScore] = sortedCandidates[0];
    const provider = this.getProviderForModel(selectedModel);
    
    return {
      selectedModel,
      provider,
      confidence: selectedScore,
      reasoning: this.generateReasoning(selectedModel, criteria, selectedScore),
      alternatives: sortedCandidates.slice(1, 4).map(([model, score]) => ({
        model,
        provider: this.getProviderForModel(model),
        score
      }))
    };
  }
  
  private getProviderForModel(modelName: string): string {
    if (modelName.startsWith('gpt-')) return 'openai';
    if (modelName.startsWith('claude-')) return 'anthropic';
    if (modelName.includes('.')) return 'bedrock';
    return 'unknown';
  }
  
  private generateReasoning(
    selectedModel: string,
    criteria: RoutingCriteria,
    score: number
  ): string {
    const capabilities = this.modelRegistry.get(selectedModel)!;
    
    const reasons: string[] = [];
    
    if (capabilities.specialties.some(s => 
        ['coding', 'reasoning', 'analysis'].includes(s))) {
      reasons.push('strong technical capabilities');
    }
    
    if (capabilities.costPerToken < 0.00001) {
      reasons.push('cost-effective');
    }
    
    if (capabilities.latency === 'low') {
      reasons.push('fast response time');
    }
    
    if (capabilities.contextLength > 100000) {
      reasons.push('large context window');
    }
    
    return `Selected ${selectedModel} (score: ${score.toFixed(3)}) due to ${reasons.join(', ')}`;
  }
  
  private async recordSelection(
    decision: RoutingDecision,
    criteria: RoutingCriteria
  ): Promise<void> {
    // 선택 기록을 메트릭으로 저장
    console.log(`Model selection: ${decision.selectedModel} for task ${criteria.taskType}`);
  }
  
  async getModelInstance(modelName: string): Promise<ModelProvider> {
    const cacheKey = modelName;
    
    if (this.providerInstances.has(cacheKey)) {
      return this.providerInstances.get(cacheKey)!;
    }
    
    const provider = this.getProviderForModel(modelName);
    const config: ModelConfig = {
      name: modelName,
      provider,
      maxTokens: 4096,
      temperature: 0.7,
      topP: 1.0,
      frequencyPenalty: 0,
      presencePenalty: 0,
      stopSequences: []
    };
    
    const instance = ModelProviderFactory.create(provider, config);
    await instance.initialize();
    
    this.providerInstances.set(cacheKey, instance);
    
    return instance;
  }
}

class ModelLoadBalancer {
  private modelLoads: Map<string, number> = new Map();
  
  async getAvailableModels(candidates: string[]): Promise<string[]> {
    // 간단한 로드 밸런싱 - 실제로는 더 정교한 로직 필요
    return candidates.filter(model => {
      const load = this.modelLoads.get(model) || 0;
      return load < 100; // 최대 100개 동시 요청
    });
  }
  
  incrementLoad(model: string): void {
    const current = this.modelLoads.get(model) || 0;
    this.modelLoads.set(model, current + 1);
  }
  
  decrementLoad(model: string): void {
    const current = this.modelLoads.get(model) || 0;
    this.modelLoads.set(model, Math.max(0, current - 1));
  }
}