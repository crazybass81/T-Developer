import crypto from 'crypto';

export interface FeatureFlagDefinition {
  key: string;
  name: string;
  description: string;
  enabled: boolean;
  defaultValue: boolean;
  rules: TargetingRule[];
  rollout?: RolloutConfig;
  cacheTTL?: number;
}

export interface FeatureFlag extends FeatureFlagDefinition {
  id: string;
  createdAt: Date;
  updatedAt: Date;
  version: number;
}

export interface EvaluationContext {
  userId: string;
  userSegments?: string[];
  environment?: string;
  [key: string]: any;
}

export interface TargetingRule {
  type: 'user' | 'segment' | 'percentage' | 'schedule';
  enabled: boolean;
  conditions: any;
}

export interface RolloutConfig {
  percentage: number;
  salt: string;
}

export interface Variant {
  key: string;
  value: any;
}

export interface FeatureFlagConfig {
  tableName: string;
  redis: any;
}

export class FeatureFlagManager {
  private flags: Map<string, FeatureFlag> = new Map();
  private cache: FlagCache;
  private storage: FlagStorage;

  constructor(config: FeatureFlagConfig) {
    this.storage = new DynamoDBFlagStorage(config.tableName);
    this.cache = new RedisFlagCache(config.redis);
    this.initialize();
  }

  private async initialize(): Promise<void> {
    // Load existing flags
    const flags = await this.storage.loadAll();
    flags.forEach(flag => this.flags.set(flag.key, flag));
  }

  async defineFlag(flag: FeatureFlagDefinition): Promise<void> {
    const featureFlag: FeatureFlag = {
      ...flag,
      id: crypto.randomUUID(),
      createdAt: new Date(),
      updatedAt: new Date(),
      version: 1
    };

    await this.storage.save(featureFlag);
    await this.cache.invalidate(flag.key);
    this.flags.set(flag.key, featureFlag);
  }

  async evaluate(key: string, context: EvaluationContext): Promise<boolean> {
    // Check cache first
    const cached = await this.cache.get(key, context);
    if (cached !== null) {
      return cached;
    }

    const flag = await this.getFlag(key);
    if (!flag) {
      return false;
    }

    const result = await this.evaluateFlag(flag, context);

    // Cache result
    await this.cache.set(key, context, result, flag.cacheTTL || 300);
    await this.recordEvaluation(key, context, result);

    return result;
  }

  private async getFlag(key: string): Promise<FeatureFlag | null> {
    return this.flags.get(key) || null;
  }

  private async evaluateFlag(flag: FeatureFlag, context: EvaluationContext): Promise<boolean> {
    if (!flag.enabled) {
      return false;
    }

    // Evaluate targeting rules
    for (const rule of flag.rules) {
      if (await this.matchesRule(rule, context)) {
        return rule.enabled;
      }
    }

    // Evaluate rollout
    if (flag.rollout) {
      return this.evaluateRollout(flag.rollout, context);
    }

    return flag.defaultValue;
  }

  private async matchesRule(rule: TargetingRule, context: EvaluationContext): Promise<boolean> {
    switch (rule.type) {
      case 'user':
        return rule.conditions.userIds?.includes(context.userId) || false;
      
      case 'segment':
        return context.userSegments?.some(segment => 
          rule.conditions.segments?.includes(segment)
        ) || false;
      
      case 'percentage':
        const hash = this.hashContext(context.userId);
        return (hash % 100) < rule.conditions.percentage;
      
      default:
        return false;
    }
  }

  private evaluateRollout(rollout: RolloutConfig, context: EvaluationContext): boolean {
    const hash = this.hashContext(rollout.salt + context.userId);
    return (hash % 100) < rollout.percentage;
  }

  private hashContext(input: string): number {
    const hash = crypto.createHash('md5').update(input).digest('hex');
    return parseInt(hash.substring(0, 8), 16);
  }

  private async recordEvaluation(key: string, context: EvaluationContext, result: boolean): Promise<void> {
    // Record evaluation metrics
    console.log(`Flag ${key} evaluated to ${result} for user ${context.userId}`);
  }

  async getVariant(experimentKey: string, context: EvaluationContext): Promise<Variant> {
    // Simplified A/B testing
    const hash = this.hashContext(context.userId);
    const variantIndex = hash % 2;
    
    return {
      key: variantIndex === 0 ? 'control' : 'treatment',
      value: variantIndex === 0 ? 'A' : 'B'
    };
  }
}

class FlagCache {
  async get(key: string, context: EvaluationContext): Promise<boolean | null> {
    // Simplified cache implementation
    return null;
  }

  async set(key: string, context: EvaluationContext, value: boolean, ttl: number): Promise<void> {
    // Simplified cache implementation
  }

  async invalidate(key: string): Promise<void> {
    // Simplified cache implementation
  }
}

class RedisFlagCache extends FlagCache {
  constructor(private redis: any) {
    super();
  }
}

class FlagStorage {
  async save(flag: FeatureFlag): Promise<void> {
    // Abstract storage
  }

  async loadAll(): Promise<FeatureFlag[]> {
    return [];
  }
}

class DynamoDBFlagStorage extends FlagStorage {
  constructor(private tableName: string) {
    super();
  }

  async save(flag: FeatureFlag): Promise<void> {
    // DynamoDB implementation would go here
    console.log(`Saving flag ${flag.key} to DynamoDB`);
  }

  async loadAll(): Promise<FeatureFlag[]> {
    // DynamoDB implementation would go here
    return [];
  }
}