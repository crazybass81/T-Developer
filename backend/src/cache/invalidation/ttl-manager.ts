export interface TTLStrategy {
  entityType: string;
  baseTTL: number;
  factors: {
    accessFrequency?: number;
    updateFrequency?: number;
    dataSize?: number;
  };
}

export class TTLManager {
  private strategies: Map<string, TTLStrategy> = new Map();

  constructor() {
    this.initializeStrategies();
  }

  private initializeStrategies(): void {
    // User data - stable, long TTL
    this.strategies.set('user', {
      entityType: 'user',
      baseTTL: 3600, // 1 hour
      factors: {
        accessFrequency: 1.5, // Increase TTL for frequently accessed users
        updateFrequency: 0.5   // Decrease TTL for frequently updated users
      }
    });

    // Project data - moderate TTL
    this.strategies.set('project', {
      entityType: 'project',
      baseTTL: 1800, // 30 minutes
      factors: {
        accessFrequency: 1.2,
        updateFrequency: 0.7
      }
    });

    // Agent data - short TTL (high volatility)
    this.strategies.set('agent', {
      entityType: 'agent',
      baseTTL: 300, // 5 minutes
      factors: {
        accessFrequency: 1.1,
        updateFrequency: 0.3
      }
    });

    // Session data - very short TTL
    this.strategies.set('session', {
      entityType: 'session',
      baseTTL: 60, // 1 minute
      factors: {
        accessFrequency: 1.0,
        updateFrequency: 0.8
      }
    });

    // Query results - medium TTL
    this.strategies.set('query', {
      entityType: 'query',
      baseTTL: 600, // 10 minutes
      factors: {
        accessFrequency: 1.3,
        dataSize: 0.8 // Decrease TTL for large result sets
      }
    });
  }

  calculateTTL(entityType: string, metadata: {
    accessCount?: number;
    updateCount?: number;
    sizeBytes?: number;
    lastAccessed?: Date;
  }): number {
    const strategy = this.strategies.get(entityType);
    if (!strategy) {
      return 3600; // Default 1 hour
    }

    let ttl = strategy.baseTTL;

    // Apply access frequency factor
    if (metadata.accessCount && strategy.factors.accessFrequency) {
      const accessFactor = Math.min(metadata.accessCount / 100, 2); // Cap at 2x
      ttl *= (1 + accessFactor * strategy.factors.accessFrequency);
    }

    // Apply update frequency factor
    if (metadata.updateCount && strategy.factors.updateFrequency) {
      const updateFactor = Math.min(metadata.updateCount / 10, 2); // Cap at 2x
      ttl *= (1 - updateFactor * strategy.factors.updateFrequency);
    }

    // Apply data size factor
    if (metadata.sizeBytes && strategy.factors.dataSize) {
      const sizeFactor = Math.min(metadata.sizeBytes / 1024, 10); // Per KB, cap at 10x
      ttl *= (1 - sizeFactor * strategy.factors.dataSize);
    }

    // Apply recency factor
    if (metadata.lastAccessed) {
      const hoursSinceAccess = (Date.now() - metadata.lastAccessed.getTime()) / (1000 * 60 * 60);
      if (hoursSinceAccess > 24) {
        ttl *= 0.5; // Reduce TTL for old data
      }
    }

    return Math.max(Math.floor(ttl), 60); // Minimum 1 minute TTL
  }

  // Adaptive TTL based on system load
  adaptTTLForLoad(baseTTL: number, systemLoad: number): number {
    if (systemLoad > 0.8) {
      // High load - increase TTL to reduce cache misses
      return Math.floor(baseTTL * 1.5);
    } else if (systemLoad < 0.3) {
      // Low load - decrease TTL for fresher data
      return Math.floor(baseTTL * 0.8);
    }
    return baseTTL;
  }

  // Time-based TTL adjustment
  getTimeBasedTTL(entityType: string, currentHour: number): number {
    const strategy = this.strategies.get(entityType);
    if (!strategy) return 3600;

    let ttl = strategy.baseTTL;

    // Peak hours (9 AM - 6 PM) - shorter TTL for fresher data
    if (currentHour >= 9 && currentHour <= 18) {
      ttl *= 0.7;
    }
    // Off-peak hours - longer TTL
    else {
      ttl *= 1.3;
    }

    return Math.floor(ttl);
  }

  // Predictive TTL based on access patterns
  predictiveTTL(entityType: string, accessPattern: {
    hourlyAccess: number[];
    weeklyPattern: number[];
    seasonality?: number;
  }): number {
    const strategy = this.strategies.get(entityType);
    if (!strategy) return 3600;

    const currentHour = new Date().getHours();
    const currentDay = new Date().getDay();

    // Predict next access based on patterns
    const hourlyPrediction = accessPattern.hourlyAccess[currentHour] || 1;
    const weeklyPrediction = accessPattern.weeklyPattern[currentDay] || 1;

    // Higher predicted access = longer TTL
    const predictionFactor = Math.min((hourlyPrediction + weeklyPrediction) / 2, 3);
    
    return Math.floor(strategy.baseTTL * predictionFactor);
  }
}