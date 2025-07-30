import { CacheManager } from './cache-manager';

export interface CacheStrategy {
  get<T>(key: string): Promise<T | null>;
  set<T>(key: string, value: T, ttl?: number): Promise<void>;
  invalidate(key: string): Promise<void>;
}

// Write-through cache
export class WriteThroughCache implements CacheStrategy {
  constructor(
    private cache: CacheManager,
    private dataStore: any
  ) {}
  
  async get<T>(key: string): Promise<T | null> {
    return await this.cache.get<T>(key);
  }
  
  async set<T>(key: string, value: T, ttl?: number): Promise<void> {
    // Write to both cache and data store
    await Promise.all([
      this.cache.set(key, value, { ttl }),
      this.dataStore.set(key, value)
    ]);
  }
  
  async invalidate(key: string): Promise<void> {
    await this.cache.del(key);
  }
}

// Write-behind cache
export class WriteBehindCache implements CacheStrategy {
  private writeQueue: Map<string, any> = new Map();
  private flushInterval!: NodeJS.Timer;
  
  constructor(
    private cache: CacheManager,
    private dataStore: any,
    private flushIntervalMs: number = 5000
  ) {
    this.startFlushTimer();
  }
  
  async get<T>(key: string): Promise<T | null> {
    return await this.cache.get<T>(key);
  }
  
  async set<T>(key: string, value: T, ttl?: number): Promise<void> {
    // Write to cache immediately
    await this.cache.set(key, value, { ttl });
    
    // Queue for later write to data store
    this.writeQueue.set(key, value);
  }
  
  async invalidate(key: string): Promise<void> {
    await this.cache.del(key);
    this.writeQueue.delete(key);
  }
  
  private startFlushTimer(): void {
    this.flushInterval = setInterval(async () => {
      await this.flushWrites();
    }, this.flushIntervalMs);
  }
  
  private async flushWrites(): Promise<void> {
    if (this.writeQueue.size === 0) return;
    
    const writes = Array.from(this.writeQueue.entries());
    this.writeQueue.clear();
    
    // Batch write to data store
    await Promise.all(
      writes.map(([key, value]) => this.dataStore.set(key, value))
    );
  }
  
  destroy(): void {
    if (this.flushInterval) {
      clearInterval(this.flushInterval as any);
    }
  }
}

// Cache-aside pattern
export class CacheAsideStrategy implements CacheStrategy {
  constructor(
    private cache: CacheManager,
    private dataStore: any
  ) {}
  
  async get<T>(key: string): Promise<T | null> {
    // Try cache first
    let value = await this.cache.get<T>(key);
    
    if (value === null) {
      // Cache miss - fetch from data store
      value = await this.dataStore.get(key);
      
      if (value !== null) {
        // Update cache
        await this.cache.set(key, value);
      }
    }
    
    return value;
  }
  
  async set<T>(key: string, value: T, ttl?: number): Promise<void> {
    // Update data store first
    await this.dataStore.set(key, value);
    
    // Then update cache
    await this.cache.set(key, value, { ttl });
  }
  
  async invalidate(key: string): Promise<void> {
    await this.cache.del(key);
  }
}

// Distributed cache invalidation
export class DistributedCacheInvalidation {
  private subscribers: Set<string> = new Set();
  
  constructor(private cache: CacheManager) {}
  
  async subscribe(pattern: string): Promise<void> {
    this.subscribers.add(pattern);
  }
  
  async invalidatePattern(pattern: string): Promise<void> {
    const deleted = await this.cache.deletePattern(pattern);
    console.log(`Invalidated ${deleted} keys matching pattern: ${pattern}`);
    
    // Notify other instances (in real implementation, use Redis pub/sub)
    await this.notifyOtherInstances(pattern);
  }
  
  private async notifyOtherInstances(pattern: string): Promise<void> {
    // Implementation would use Redis pub/sub or message queue
    console.log(`Notifying other instances about invalidation: ${pattern}`);
  }
}

// Time-based cache invalidation
export class TimeBasedInvalidation {
  private timers: Map<string, NodeJS.Timer> = new Map();
  
  constructor(private cache: CacheManager) {}
  
  scheduleInvalidation(key: string, delayMs: number): void {
    // Clear existing timer
    const existingTimer = this.timers.get(key);
    if (existingTimer) {
      clearTimeout(existingTimer as any);
    }
    
    // Set new timer
    const timer = setTimeout(async () => {
      await this.cache.del(key);
      this.timers.delete(key);
    }, delayMs) as any;
    
    this.timers.set(key, timer);
  }
  
  cancelInvalidation(key: string): void {
    const timer = this.timers.get(key);
    if (timer) {
      clearTimeout(timer as any);
      this.timers.delete(key);
    }
  }
  
  destroy(): void {
    for (const timer of this.timers.values()) {
      clearTimeout(timer as any);
    }
    this.timers.clear();
  }
}