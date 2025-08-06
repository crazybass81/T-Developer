import Redis from 'ioredis';

interface FallbackChain {
  [key: string]: string[];
}

interface ModelHealth {
  model: string;
  isHealthy: boolean;
  lastCheck: Date;
  errorCount: number;
  responseTime: number;
}

export class ModelFallbackManager {
  private redis: Redis;
  private healthChecker: ModelHealthChecker;
  private loadBalancer: ModelLoadBalancer;
  private fallbackChains: FallbackChain;

  constructor() {
    this.redis = new Redis({
      host: process.env.REDIS_HOST || 'localhost',
      port: parseInt(process.env.REDIS_PORT || '6379'),
    });
    
    this.healthChecker = new ModelHealthChecker();
    this.loadBalancer = new ModelLoadBalancer(this.redis);
    this.fallbackChains = this.defineFallbackChains();
  }

  private defineFallbackChains(): FallbackChain {
    return {
      'gpt-4': ['gpt-4-turbo', 'claude-3-opus', 'gpt-3.5-turbo'],
      'claude-3-opus': ['claude-3-sonnet', 'gpt-4', 'claude-2.1'],
      'bedrock-claude': ['bedrock-titan', 'claude-3-opus', 'gpt-4'],
      'gpt-3.5-turbo': ['claude-3-haiku', 'gpt-4'],
      'claude-3-sonnet': ['claude-3-haiku', 'gpt-3.5-turbo'],
    };
  }

  async executeWithFallback(
    primaryModel: string,
    prompt: string,
    options: any = {}
  ): Promise<any> {
    const fallbackChain = [primaryModel, ...(this.fallbackChains[primaryModel] || [])];
    let lastError: Error | null = null;

    for (const model of fallbackChain) {
      try {
        if (!(await this.healthChecker.isHealthy(model))) {
          continue;
        }

        if (!(await this.loadBalancer.canHandleRequest(model))) {
          continue;
        }

        const response = await this.executeModel(model, prompt, options);
        await this.recordSuccess(model);
        return response;

      } catch (error) {
        lastError = error as Error;
        await this.recordFailure(model, error as Error);

        if (!this.isRetryableError(error as Error)) {
          throw error;
        }
      }
    }

    throw new Error(`All models failed. Last error: ${lastError?.message}`);
  }

  private async executeModel(model: string, prompt: string, options: any): Promise<any> {
    // Mock implementation - replace with actual model execution
    await new Promise(resolve => setTimeout(resolve, 100));
    return { content: `Response from ${model}: ${prompt.substring(0, 50)}...` };
  }

  private isRetryableError(error: Error): boolean {
    const retryableErrors = [
      'rate_limit', 'timeout', 'service_unavailable', 'internal_server_error'
    ];
    return retryableErrors.some(err => error.message.toLowerCase().includes(err));
  }

  private async recordSuccess(model: string): Promise<void> {
    await this.redis.hincrby('model:success', model, 1);
    await this.redis.hset('model:last_success', model, Date.now());
  }

  private async recordFailure(model: string, error: Error): Promise<void> {
    await this.redis.hincrby('model:failures', model, 1);
    await this.redis.hset('model:last_error', model, error.message);
  }
}

class ModelHealthChecker {
  private healthCache = new Map<string, ModelHealth>();
  private checkInterval = 60000; // 1분

  async isHealthy(model: string): Promise<boolean> {
    const cached = this.healthCache.get(model);
    
    if (cached && Date.now() - cached.lastCheck.getTime() < this.checkInterval) {
      return cached.isHealthy;
    }

    const health = await this.checkModelHealth(model);
    this.healthCache.set(model, health);
    return health.isHealthy;
  }

  private async checkModelHealth(model: string): Promise<ModelHealth> {
    const startTime = Date.now();
    
    try {
      // Mock health check - replace with actual implementation
      await new Promise(resolve => setTimeout(resolve, 50));
      
      return {
        model,
        isHealthy: true,
        lastCheck: new Date(),
        errorCount: 0,
        responseTime: Date.now() - startTime,
      };
    } catch (error) {
      return {
        model,
        isHealthy: false,
        lastCheck: new Date(),
        errorCount: 1,
        responseTime: Date.now() - startTime,
      };
    }
  }
}

class ModelLoadBalancer {
  private rateLimits: Map<string, number>;

  constructor(private redis: Redis) {
    this.rateLimits = new Map([
      ['gpt-4', 100],
      ['gpt-3.5-turbo', 1000],
      ['claude-3-opus', 50],
      ['claude-3-sonnet', 200],
      ['bedrock-claude', 500],
    ]);
  }

  async canHandleRequest(model: string): Promise<boolean> {
    const rateLimit = this.rateLimits.get(model) || 100;
    const currentCount = await this.getDistributedCount(model);
    
    return currentCount < rateLimit * 0.8; // 80% 임계값
  }

  private async getDistributedCount(model: string): Promise<number> {
    const key = `model_request_count:${model}`;
    const count = await this.redis.get(key);
    return parseInt(count || '0');
  }

  async incrementRequestCount(model: string): Promise<void> {
    const key = `model_request_count:${model}`;
    await this.redis.incr(key);
    await this.redis.expire(key, 60); // 1분 TTL
  }
}