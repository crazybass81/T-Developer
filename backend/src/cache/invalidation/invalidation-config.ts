import { CacheManager } from '../cache-manager';
import { InvalidationEngine } from './invalidation-engine';
import { CacheEventBus } from './event-bus';
import { TTLManager } from './ttl-manager';
import { InvalidationMiddleware, TDeveloperInvalidationMiddleware } from './invalidation-middleware';

export function createInvalidationSystem(cacheManager: CacheManager) {
  // Create invalidation engine
  const invalidationEngine = new InvalidationEngine(cacheManager);
  
  // Create event bus
  const eventBus = new CacheEventBus(invalidationEngine);
  
  // Create TTL manager
  const ttlManager = new TTLManager();
  
  // Create middleware
  const invalidationMiddleware = new InvalidationMiddleware(eventBus);
  const tdevMiddleware = new TDeveloperInvalidationMiddleware(invalidationMiddleware);

  return {
    invalidationEngine,
    eventBus,
    ttlManager,
    invalidationMiddleware,
    tdevMiddleware
  };
}

// Performance-optimized invalidation settings for Agno Framework
export const AGNO_INVALIDATION_CONFIG = {
  // Immediate invalidation for agent sessions (3μs target)
  agentSessionInvalidation: {
    delay: 0,
    batchSize: 1
  },
  
  // Delayed invalidation for less critical data
  backgroundInvalidation: {
    delay: 1000, // 1 second
    batchSize: 100
  },
  
  // Smart invalidation thresholds
  smartInvalidation: {
    highFrequencyThreshold: 100,
    lowFrequencyDelay: 5000
  }
};