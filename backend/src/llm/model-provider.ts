export interface ModelConfig {
  name: string;
  provider: string;
  maxTokens: number;
  temperature: number;
  topP: number;
  frequencyPenalty: number;
  presencePenalty: number;
  stopSequences: string[];
  apiKey?: string;
  endpoint?: string;
}

export interface ModelResponse {
  text: string;
  tokensUsed: number;
  finishReason: string;
  metadata: Record<string, any>;
  cost?: number;
}

export interface StreamChunk {
  text: string;
  isComplete: boolean;
  metadata?: Record<string, any>;
}

export abstract class ModelProvider {
  protected config: ModelConfig;
  
  constructor(config: ModelConfig) {
    this.config = config;
  }
  
  abstract initialize(): Promise<void>;
  
  abstract generate(
    prompt: string,
    options?: Partial<ModelConfig>
  ): Promise<ModelResponse>;
  
  abstract streamGenerate(
    prompt: string,
    options?: Partial<ModelConfig>
  ): AsyncIterableIterator<StreamChunk>;
  
  abstract embed(texts: string[]): Promise<number[][]>;
  
  abstract estimateTokens(text: string): number;
  
  abstract getCostEstimate(inputTokens: number, outputTokens: number): number;
  
  // 공통 유틸리티 메서드
  protected mergeConfig(options?: Partial<ModelConfig>): ModelConfig {
    return {
      ...this.config,
      ...options
    };
  }
  
  protected validateInput(prompt: string): void {
    if (!prompt || prompt.trim().length === 0) {
      throw new Error('Prompt cannot be empty');
    }
    
    const estimatedTokens = this.estimateTokens(prompt);
    if (estimatedTokens > this.config.maxTokens) {
      throw new Error(`Prompt too long: ${estimatedTokens} tokens exceeds limit of ${this.config.maxTokens}`);
    }
  }
}

export class ModelProviderFactory {
  private static providers: Map<string, new (config: ModelConfig) => ModelProvider> = new Map();
  
  static register(name: string, providerClass: new (config: ModelConfig) => ModelProvider): void {
    this.providers.set(name, providerClass);
  }
  
  static create(providerName: string, config: ModelConfig): ModelProvider {
    const ProviderClass = this.providers.get(providerName);
    if (!ProviderClass) {
      throw new Error(`Unknown provider: ${providerName}`);
    }
    
    return new ProviderClass(config);
  }
  
  static getAvailableProviders(): string[] {
    return Array.from(this.providers.keys());
  }
}

// 모델 성능 메트릭
export interface ModelMetrics {
  provider: string;
  model: string;
  averageLatency: number;
  successRate: number;
  costPerToken: number;
  lastUpdated: Date;
}

export class ModelMetricsCollector {
  private metrics: Map<string, ModelMetrics> = new Map();
  
  recordRequest(
    provider: string,
    model: string,
    latency: number,
    success: boolean,
    cost: number,
    tokens: number
  ): void {
    const key = `${provider}:${model}`;
    const existing = this.metrics.get(key);
    
    if (existing) {
      // 이동 평균 계산
      existing.averageLatency = (existing.averageLatency * 0.9) + (latency * 0.1);
      existing.successRate = (existing.successRate * 0.9) + (success ? 0.1 : 0);
      existing.costPerToken = tokens > 0 ? cost / tokens : existing.costPerToken;
      existing.lastUpdated = new Date();
    } else {
      this.metrics.set(key, {
        provider,
        model,
        averageLatency: latency,
        successRate: success ? 1 : 0,
        costPerToken: tokens > 0 ? cost / tokens : 0,
        lastUpdated: new Date()
      });
    }
  }
  
  getMetrics(provider?: string, model?: string): ModelMetrics[] {
    const results: ModelMetrics[] = [];
    
    for (const [key, metrics] of this.metrics) {
      if (provider && metrics.provider !== provider) continue;
      if (model && metrics.model !== model) continue;
      results.push(metrics);
    }
    
    return results;
  }
  
  getBestPerformingModel(criteria: 'latency' | 'success' | 'cost' = 'latency'): ModelMetrics | null {
    const allMetrics = this.getMetrics();
    if (allMetrics.length === 0) return null;
    
    switch (criteria) {
      case 'latency':
        return allMetrics.reduce((best, current) => 
          current.averageLatency < best.averageLatency ? current : best
        );
      case 'success':
        return allMetrics.reduce((best, current) => 
          current.successRate > best.successRate ? current : best
        );
      case 'cost':
        return allMetrics.reduce((best, current) => 
          current.costPerToken < best.costPerToken ? current : best
        );
      default:
        return allMetrics[0];
    }
  }
}