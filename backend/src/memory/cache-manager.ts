// backend/src/memory/cache-manager.ts
export interface CacheEntry<T = any> {
  key: string;
  value: T;
  timestamp: Date;
  ttl?: number;
  hits: number;
}

export class CacheManager {
  private cache: Map<string, CacheEntry> = new Map();
  private maxSize: number;
  private cleanupInterval!: NodeJS.Timer;

  constructor(maxSize: number = 1000) {
    this.maxSize = maxSize;
    this.startCleanup();
  }

  // Set cache entry
  set<T>(key: string, value: T, ttl?: number): void {
    // Remove oldest entries if at capacity
    if (this.cache.size >= this.maxSize) {
      this.evictOldest();
    }

    const entry: CacheEntry<T> = {
      key,
      value,
      timestamp: new Date(),
      ttl,
      hits: 0
    };

    this.cache.set(key, entry);
  }

  // Get cache entry
  get<T>(key: string): T | null {
    const entry = this.cache.get(key);
    if (!entry) return null;

    // Check TTL
    if (entry.ttl && (Date.now() - entry.timestamp.getTime()) > entry.ttl) {
      this.cache.delete(key);
      return null;
    }

    // Update hit count
    entry.hits++;
    return entry.value as T;
  }

  // Check if key exists
  has(key: string): boolean {
    return this.get(key) !== null;
  }

  // Delete cache entry
  delete(key: string): boolean {
    return this.cache.delete(key);
  }

  // Clear all cache
  clear(): void {
    this.cache.clear();
  }

  // Get cache statistics
  getStats(): {
    size: number;
    maxSize: number;
    hitRate: number;
    entries: Array<{key: string; hits: number; age: number}>;
  } {
    const now = Date.now();
    const entries = Array.from(this.cache.values()).map(entry => ({
      key: entry.key,
      hits: entry.hits,
      age: now - entry.timestamp.getTime()
    }));

    const totalHits = entries.reduce((sum, entry) => sum + entry.hits, 0);
    const hitRate = entries.length > 0 ? totalHits / entries.length : 0;

    return {
      size: this.cache.size,
      maxSize: this.maxSize,
      hitRate,
      entries: entries.sort((a, b) => b.hits - a.hits)
    };
  }

  // Evict oldest entries
  private evictOldest(): void {
    const entries = Array.from(this.cache.entries());
    entries.sort((a, b) => a[1].timestamp.getTime() - b[1].timestamp.getTime());
    
    // Remove oldest 10% or at least 1
    const toRemove = Math.max(1, Math.floor(entries.length * 0.1));
    for (let i = 0; i < toRemove; i++) {
      this.cache.delete(entries[i][0]);
    }
  }

  // Cleanup expired entries
  private cleanup(): void {
    const now = Date.now();
    for (const [key, entry] of this.cache) {
      if (entry.ttl && (now - entry.timestamp.getTime()) > entry.ttl) {
        this.cache.delete(key);
      }
    }
  }

  private startCleanup(): void {
    this.cleanupInterval = setInterval(() => this.cleanup(), 60000); // 1 minute
  }
}