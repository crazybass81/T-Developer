export { MemoryGarbageCollector, GCPolicy, GCStats, MemoryItem } from './garbage-collector';

// Memory management utilities
export class MemoryManager {
  private static instance: MemoryManager;
  private garbageCollector: MemoryGarbageCollector;

  private constructor() {
    const policy = {
      maxMemoryMB: parseInt(process.env.MAX_MEMORY_MB || '512'),
      maxAge: parseInt(process.env.MAX_MEMORY_AGE_DAYS || '7'),
      minRelevance: parseFloat(process.env.MIN_RELEVANCE || '0.1'),
      gcInterval: parseInt(process.env.GC_INTERVAL_SECONDS || '300') // 5 minutes
    };

    this.garbageCollector = new MemoryGarbageCollector(policy);
  }

  static getInstance(): MemoryManager {
    if (!MemoryManager.instance) {
      MemoryManager.instance = new MemoryManager();
    }
    return MemoryManager.instance;
  }

  startGarbageCollection(): void {
    this.garbageCollector.start();
  }

  stopGarbageCollection(): void {
    this.garbageCollector.stop();
  }

  addMemoryItem(key: string, data: any, relevance?: number): void {
    this.garbageCollector.addMemoryItem(key, data, relevance);
  }

  getMemoryItem(key: string): any {
    return this.garbageCollector.getMemoryItem(key);
  }

  getMemoryStats() {
    return this.garbageCollector.getStats();
  }
}