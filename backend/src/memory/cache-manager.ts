/**
 * Advanced Cache Manager for T-Developer
 * Provides multi-layer caching with TTL, LRU eviction, and intelligent prefetching
 */

import { EventEmitter } from 'events';

export interface CacheOptions {
  maxSize?: number;
  defaultTTL?: number; // in milliseconds
  checkPeriod?: number; // TTL check interval in milliseconds
  enableStats?: boolean;
  enableEvents?: boolean;
  strategy?: 'lru' | 'lfu' | 'fifo';
}

export interface CacheEntry<T> {
  key: string;
  value: T;
  ttl: number;
  createdAt: number;
  accessedAt: number;
  accessCount: number;
  size: number;
}

export interface CacheStats {
  hits: number;
  misses: number;
  hitRate: number;
  size: number;
  maxSize: number;
  memoryUsage: number;
  evictions: number;
  expires: number;
  operations: number;
  averageAccessTime: number;
}

export interface CacheLayer {
  name: string;
  enabled: boolean;
  priority: number;
  options: CacheOptions;
  cache: Map<string, CacheEntry<any>>;
  stats: CacheStats;
}

export enum CacheEventType {
  HIT = 'hit',
  MISS = 'miss',
  SET = 'set',
  DELETE = 'delete',
  EXPIRE = 'expire',
  EVICT = 'evict',
  CLEAR = 'clear',
  FULL = 'full'
}

/**
 * Multi-layer cache manager with advanced features
 */
export class CacheManager extends EventEmitter {
  private layers: Map<string, CacheLayer> = new Map();
  private cleanupInterval?: NodeJS.Timeout;
  private globalStats: CacheStats;
  private prefetchQueue: Set<string> = new Set();
  private options: Required<CacheOptions>;

  constructor(options: CacheOptions = {}) {
    super();
    
    this.options = {
      maxSize: 1000,
      defaultTTL: 300000, // 5 minutes
      checkPeriod: 60000, // 1 minute
      enableStats: true,
      enableEvents: true,
      strategy: 'lru',
      ...options
    };

    this.globalStats = this.initializeStats();
    this.setupCleanup();
    this.initializeDefaultLayers();
  }

  /**
   * Initialize default cache layers
   */
  private initializeDefaultLayers(): void {
    // L1 Cache: In-memory fast cache
    this.addLayer('L1', {
      maxSize: 500,
      defaultTTL: 60000, // 1 minute
      strategy: 'lru'
    });

    // L2 Cache: Medium-term cache
    this.addLayer('L2', {
      maxSize: 2000,
      defaultTTL: 300000, // 5 minutes
      strategy: 'lru'
    });

    // L3 Cache: Long-term cache
    this.addLayer('L3', {
      maxSize: 5000,
      defaultTTL: 1800000, // 30 minutes
      strategy: 'lfu'
    });
  }

  /**
   * Add a cache layer
   */
  public addLayer(name: string, options: CacheOptions = {}): void {
    const layerOptions = { ...this.options, ...options };
    
    this.layers.set(name, {
      name,
      enabled: true,
      priority: this.layers.size,
      options: layerOptions,
      cache: new Map(),
      stats: this.initializeStats()
    });
  }

  /**
   * Remove a cache layer
   */
  public removeLayer(name: string): boolean {
    return this.layers.delete(name);
  }

  /**
   * Get value from cache (multi-layer lookup)
   */
  public async get<T>(key: string, layerName?: string): Promise<T | null> {
    const startTime = Date.now();
    
    try {
      // If specific layer requested
      if (layerName) {
        return await this.getFromLayer<T>(key, layerName);
      }

      // Multi-layer lookup (L1 -> L2 -> L3)
      const sortedLayers = Array.from(this.layers.values())
        .filter(layer => layer.enabled)
        .sort((a, b) => a.priority - b.priority);

      for (const layer of sortedLayers) {
        const value = await this.getFromLayer<T>(key, layer.name);
        if (value !== null) {
          // Promote to higher layers (cache warming)
          await this.promoteToHigherLayers(key, value, layer.priority);
          return value;
        }
      }

      // Cache miss
      this.updateGlobalStats('miss', Date.now() - startTime);
      this.emit(CacheEventType.MISS, { key, layers: sortedLayers.map(l => l.name) });
      
      return null;
    } catch (error) {
      console.error(`Cache get error for key ${key}:`, error);
      return null;
    }
  }

  /**
   * Get value from specific layer
   */
  private async getFromLayer<T>(key: string, layerName: string): Promise<T | null> {
    const layer = this.layers.get(layerName);
    if (!layer || !layer.enabled) {
      return null;
    }

    const entry = layer.cache.get(key);
    if (!entry) {
      layer.stats.misses++;
      return null;
    }

    // Check TTL
    if (Date.now() > entry.ttl) {
      layer.cache.delete(key);
      layer.stats.expires++;
      this.emit(CacheEventType.EXPIRE, { key, layer: layerName });
      return null;
    }

    // Update access stats
    entry.accessedAt = Date.now();
    entry.accessCount++;
    layer.stats.hits++;
    
    this.updateGlobalStats('hit');
    this.emit(CacheEventType.HIT, { key, layer: layerName });
    
    return entry.value as T;
  }

  /**
   * Set value in cache
   */
  public async set<T>(
    key: string,
    value: T,
    ttl?: number,
    layerName?: string
  ): Promise<void> {
    const actualTTL = ttl || this.options.defaultTTL;
    
    if (layerName) {
      await this.setInLayer(key, value, actualTTL, layerName);
    } else {
      // Set in all layers with appropriate TTLs
      const layers = Array.from(this.layers.values())
        .filter(layer => layer.enabled)
        .sort((a, b) => a.priority - b.priority);

      for (const layer of layers) {
        const layerTTL = Math.min(actualTTL, layer.options.defaultTTL!);
        await this.setInLayer(key, value, layerTTL, layer.name);
      }
    }

    this.emit(CacheEventType.SET, { key, layerName, ttl: actualTTL });
  }

  /**
   * Set value in specific layer
   */
  private async setInLayer<T>(
    key: string,
    value: T,
    ttl: number,
    layerName: string
  ): Promise<void> {
    const layer = this.layers.get(layerName);
    if (!layer || !layer.enabled) {
      return;
    }

    const now = Date.now();
    const size = this.calculateSize(value);
    
    const entry: CacheEntry<T> = {
      key,
      value,
      ttl: now + ttl,
      createdAt: now,
      accessedAt: now,
      accessCount: 1,
      size
    };

    // Check if cache is full and evict if necessary
    if (layer.cache.size >= layer.options.maxSize! && !layer.cache.has(key)) {
      await this.evictFromLayer(layer);
    }

    layer.cache.set(key, entry);
    layer.stats.size = layer.cache.size;
    layer.stats.memoryUsage += size;
    
    this.updateGlobalStats('set');
  }

  /**
   * Delete from cache
   */
  public async delete(key: string, layerName?: string): Promise<boolean> {
    let deleted = false;

    if (layerName) {
      deleted = await this.deleteFromLayer(key, layerName);
    } else {
      // Delete from all layers
      for (const layer of this.layers.values()) {
        const layerDeleted = await this.deleteFromLayer(key, layer.name);
        deleted = deleted || layerDeleted;
      }
    }

    if (deleted) {
      this.emit(CacheEventType.DELETE, { key, layerName });
    }

    return deleted;
  }

  /**
   * Delete from specific layer
   */
  private async deleteFromLayer(key: string, layerName: string): Promise<boolean> {
    const layer = this.layers.get(layerName);
    if (!layer) {
      return false;
    }

    const entry = layer.cache.get(key);
    if (entry) {
      layer.cache.delete(key);
      layer.stats.size = layer.cache.size;
      layer.stats.memoryUsage -= entry.size;
      return true;
    }

    return false;
  }

  /**
   * Clear cache
   */
  public async clear(layerName?: string): Promise<void> {
    if (layerName) {
      const layer = this.layers.get(layerName);
      if (layer) {
        layer.cache.clear();
        layer.stats = this.initializeStats();
      }
    } else {
      // Clear all layers
      for (const layer of this.layers.values()) {
        layer.cache.clear();
        layer.stats = this.initializeStats();
      }
      this.globalStats = this.initializeStats();
    }

    this.emit(CacheEventType.CLEAR, { layerName });
  }

  /**
   * Get cache statistics
   */
  public getStats(layerName?: string): CacheStats {
    if (layerName) {
      const layer = this.layers.get(layerName);
      if (layer) {
        return this.calculateStats(layer.stats);
      }
      throw new Error(`Layer ${layerName} not found`);
    }

    // Return global stats
    return this.calculateStats(this.globalStats);
  }

  /**
   * Get all layers statistics
   */
  public getAllStats(): Record<string, CacheStats> {
    const stats: Record<string, CacheStats> = {};
    
    for (const [name, layer] of this.layers) {
      stats[name] = this.calculateStats(layer.stats);
    }
    
    stats.global = this.calculateStats(this.globalStats);
    
    return stats;
  }

  /**
   * Prefetch data (background loading)
   */
  public async prefetch<T>(
    key: string,
    loader: () => Promise<T>,
    ttl?: number
  ): Promise<void> {
    if (this.prefetchQueue.has(key)) {
      return; // Already being prefetched
    }

    this.prefetchQueue.add(key);

    try {
      const value = await loader();
      await this.set(key, value, ttl);
    } catch (error) {
      console.error(`Prefetch error for key ${key}:`, error);
    } finally {
      this.prefetchQueue.delete(key);
    }
  }

  /**
   * Batch operations
   */
  public async mget<T>(keys: string[], layerName?: string): Promise<Map<string, T>> {
    const results = new Map<string, T>();
    
    await Promise.all(
      keys.map(async (key) => {
        const value = await this.get<T>(key, layerName);
        if (value !== null) {
          results.set(key, value);
        }
      })
    );

    return results;
  }

  public async mset<T>(
    entries: Map<string, T>,
    ttl?: number,
    layerName?: string
  ): Promise<void> {
    await Promise.all(
      Array.from(entries.entries()).map(([key, value]) =>
        this.set(key, value, ttl, layerName)
      )
    );
  }

  /**
   * Cache warming - preload frequently accessed data
   */
  public async warm<T>(
    keys: string[],
    loader: (key: string) => Promise<T>,
    ttl?: number
  ): Promise<void> {
    await Promise.all(
      keys.map(async (key) => {
        try {
          const value = await loader(key);
          await this.set(key, value, ttl);
        } catch (error) {
          console.error(`Cache warming error for key ${key}:`, error);
        }
      })
    );
  }

  /**
   * Get cache keys matching pattern
   */
  public getKeys(pattern?: RegExp, layerName?: string): string[] {
    const keys: Set<string> = new Set();

    const layers = layerName 
      ? [this.layers.get(layerName)].filter(Boolean) as CacheLayer[]
      : Array.from(this.layers.values());

    for (const layer of layers) {
      for (const key of layer.cache.keys()) {
        if (!pattern || pattern.test(key)) {
          keys.add(key);
        }
      }
    }

    return Array.from(keys);
  }

  /**
   * Enable/disable layer
   */
  public setLayerEnabled(layerName: string, enabled: boolean): void {
    const layer = this.layers.get(layerName);
    if (layer) {
      layer.enabled = enabled;
    }
  }

  /**
   * Private helper methods
   */
  private initializeStats(): CacheStats {
    return {
      hits: 0,
      misses: 0,
      hitRate: 0,
      size: 0,
      maxSize: this.options.maxSize,
      memoryUsage: 0,
      evictions: 0,
      expires: 0,
      operations: 0,
      averageAccessTime: 0
    };
  }

  private calculateStats(stats: CacheStats): CacheStats {
    const total = stats.hits + stats.misses;
    return {
      ...stats,
      hitRate: total > 0 ? (stats.hits / total) * 100 : 0
    };
  }

  private updateGlobalStats(operation: 'hit' | 'miss' | 'set', accessTime?: number): void {
    this.globalStats.operations++;
    
    if (operation === 'hit') {
      this.globalStats.hits++;
    } else if (operation === 'miss') {
      this.globalStats.misses++;
    }

    if (accessTime !== undefined) {
      this.globalStats.averageAccessTime = 
        (this.globalStats.averageAccessTime + accessTime) / 2;
    }
  }

  private calculateSize(value: any): number {
    try {
      return JSON.stringify(value).length;
    } catch {
      return 0;
    }
  }

  private async evictFromLayer(layer: CacheLayer): Promise<void> {
    const strategy = layer.options.strategy || 'lru';
    
    let keyToEvict: string | undefined;

    switch (strategy) {
      case 'lru':
        keyToEvict = this.findLRUKey(layer);
        break;
      case 'lfu':
        keyToEvict = this.findLFUKey(layer);
        break;
      case 'fifo':
        keyToEvict = this.findFIFOKey(layer);
        break;
    }

    if (keyToEvict) {
      const entry = layer.cache.get(keyToEvict);
      if (entry) {
        layer.cache.delete(keyToEvict);
        layer.stats.evictions++;
        layer.stats.memoryUsage -= entry.size;
        this.emit(CacheEventType.EVICT, { key: keyToEvict, layer: layer.name });
      }
    }
  }

  private findLRUKey(layer: CacheLayer): string | undefined {
    let oldestKey: string | undefined;
    let oldestTime = Date.now();

    for (const [key, entry] of layer.cache) {
      if (entry.accessedAt < oldestTime) {
        oldestTime = entry.accessedAt;
        oldestKey = key;
      }
    }

    return oldestKey;
  }

  private findLFUKey(layer: CacheLayer): string | undefined {
    let leastUsedKey: string | undefined;
    let leastCount = Infinity;

    for (const [key, entry] of layer.cache) {
      if (entry.accessCount < leastCount) {
        leastCount = entry.accessCount;
        leastUsedKey = key;
      }
    }

    return leastUsedKey;
  }

  private findFIFOKey(layer: CacheLayer): string | undefined {
    let oldestKey: string | undefined;
    let oldestTime = Date.now();

    for (const [key, entry] of layer.cache) {
      if (entry.createdAt < oldestTime) {
        oldestTime = entry.createdAt;
        oldestKey = key;
      }
    }

    return oldestKey;
  }

  private async promoteToHigherLayers<T>(
    key: string,
    value: T,
    currentPriority: number
  ): Promise<void> {
    const higherLayers = Array.from(this.layers.values())
      .filter(layer => layer.enabled && layer.priority < currentPriority)
      .sort((a, b) => a.priority - b.priority);

    for (const layer of higherLayers) {
      if (!layer.cache.has(key)) {
        await this.setInLayer(key, value, layer.options.defaultTTL!, layer.name);
      }
    }
  }

  private setupCleanup(): void {
    this.cleanupInterval = setInterval(() => {
      this.cleanupExpired();
    }, this.options.checkPeriod);
  }

  private cleanupExpired(): void {
    const now = Date.now();

    for (const layer of this.layers.values()) {
      const expiredKeys: string[] = [];

      for (const [key, entry] of layer.cache) {
        if (now > entry.ttl) {
          expiredKeys.push(key);
        }
      }

      for (const key of expiredKeys) {
        const entry = layer.cache.get(key);
        if (entry) {
          layer.cache.delete(key);
          layer.stats.expires++;
          layer.stats.memoryUsage -= entry.size;
          this.emit(CacheEventType.EXPIRE, { key, layer: layer.name });
        }
      }

      layer.stats.size = layer.cache.size;
    }
  }

  /**
   * Cleanup and destroy
   */
  public destroy(): void {
    if (this.cleanupInterval) {
      clearInterval(this.cleanupInterval);
    }
    
    this.clear();
    this.removeAllListeners();
  }
}

// Export singleton instance for global use
export const cacheManager = new CacheManager();