interface GCPolicy {
  maxMemoryMB: number;
  maxAge: number;  // days
  minRelevance: number;
  gcInterval: number;  // seconds
}

interface GCStats {
  itemsChecked: number;
  itemsRemoved: number;
  memoryFreed: number;
  duration: number;
  timestamp: Date;
}

interface MemoryItem {
  timestamp: number;
  relevance: number;
  accessCount: number;
  size: number;
  data: any;
}

class MemoryGarbageCollector {
  private policy: GCPolicy;
  private isRunning: boolean = false;
  private gcTimer: NodeJS.Timer | null = null;
  private memoryStore: Map<string, MemoryItem> = new Map();

  constructor(policy: GCPolicy) {
    this.policy = policy;
  }

  start(): void {
    if (this.isRunning) return;

    this.isRunning = true;
    this.gcTimer = setInterval(
      () => this.runGarbageCollection(),
      this.policy.gcInterval * 1000
    );

    console.log('Memory garbage collector started');
  }

  stop(): void {
    if (this.gcTimer) {
      clearInterval(this.gcTimer);
      this.gcTimer = null;
    }
    this.isRunning = false;
    console.log('Memory garbage collector stopped');
  }

  addMemoryItem(key: string, data: any, relevance: number = 0.5): void {
    const size = this.calculateItemSize(data);
    this.memoryStore.set(key, {
      timestamp: Date.now(),
      relevance,
      accessCount: 0,
      size,
      data
    });
  }

  getMemoryItem(key: string): any {
    const item = this.memoryStore.get(key);
    if (item) {
      item.accessCount++;
      return item.data;
    }
    return null;
  }

  private async runGarbageCollection(): Promise<void> {
    const startTime = Date.now();
    const stats: GCStats = {
      itemsChecked: 0,
      itemsRemoved: 0,
      memoryFreed: 0,
      duration: 0,
      timestamp: new Date()
    };

    try {
      // Check memory usage
      const memoryUsage = await this.getMemoryUsage();
      if (memoryUsage < this.policy.maxMemoryMB * 0.8) {
        return; // Skip if below threshold
      }

      // Clean memory items
      await this.cleanMemoryItems(stats);

      // Compact memory
      await this.compactMemory();

      stats.duration = Date.now() - startTime;
      
      if (stats.itemsRemoved > 0) {
        console.log(`GC completed: removed ${stats.itemsRemoved} items, ` +
                   `freed ${stats.memoryFreed}MB in ${stats.duration}ms`);
      }

    } catch (error) {
      console.error('Garbage collection failed:', error);
    }
  }

  private async cleanMemoryItems(stats: GCStats): Promise<void> {
    const itemsToRemove: string[] = [];

    for (const [key, item] of this.memoryStore) {
      stats.itemsChecked++;

      if (this.shouldRemove(item)) {
        itemsToRemove.push(key);
        stats.memoryFreed += item.size / (1024 * 1024); // Convert to MB
      }
    }

    // Remove items
    for (const key of itemsToRemove) {
      this.memoryStore.delete(key);
      stats.itemsRemoved++;
    }
  }

  private shouldRemove(item: MemoryItem): boolean {
    const age = Date.now() - item.timestamp;
    const maxAgeMs = this.policy.maxAge * 24 * 60 * 60 * 1000;

    // Remove if too old
    if (age > maxAgeMs) {
      return true;
    }

    // Remove if relevance too low
    if (item.relevance < this.policy.minRelevance) {
      return true;
    }

    // Remove if rarely accessed
    const accessRate = item.accessCount / (age / 1000 / 60); // per minute
    if (accessRate < 0.01) {
      return true;
    }

    return false;
  }

  private async getMemoryUsage(): Promise<number> {
    // Calculate total memory usage in MB
    let totalSize = 0;
    for (const item of this.memoryStore.values()) {
      totalSize += item.size;
    }
    return totalSize / (1024 * 1024);
  }

  private calculateItemSize(data: any): number {
    // Rough estimation of object size in bytes
    const jsonString = JSON.stringify(data);
    return new Blob([jsonString]).size;
  }

  private async compactMemory(): Promise<void> {
    // Force garbage collection if available
    if (global.gc) {
      global.gc();
    }

    // Reorganize memory store for better performance
    const entries = Array.from(this.memoryStore.entries());
    this.memoryStore.clear();
    
    // Re-add entries (this helps with memory fragmentation)
    for (const [key, item] of entries) {
      this.memoryStore.set(key, item);
    }
  }

  getStats(): {
    totalItems: number;
    totalMemoryMB: number;
    oldestItem: Date | null;
    avgRelevance: number;
  } {
    if (this.memoryStore.size === 0) {
      return {
        totalItems: 0,
        totalMemoryMB: 0,
        oldestItem: null,
        avgRelevance: 0
      };
    }

    let totalSize = 0;
    let totalRelevance = 0;
    let oldestTimestamp = Date.now();

    for (const item of this.memoryStore.values()) {
      totalSize += item.size;
      totalRelevance += item.relevance;
      if (item.timestamp < oldestTimestamp) {
        oldestTimestamp = item.timestamp;
      }
    }

    return {
      totalItems: this.memoryStore.size,
      totalMemoryMB: totalSize / (1024 * 1024),
      oldestItem: new Date(oldestTimestamp),
      avgRelevance: totalRelevance / this.memoryStore.size
    };
  }
}

export { MemoryGarbageCollector, GCPolicy, GCStats, MemoryItem };