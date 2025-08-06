import { EventEmitter } from 'events';
import { logger } from '../config/logger';

interface MemoryStats {
  heapUsed: number;
  heapTotal: number;
  external: number;
  rss: number;
  arrayBuffers: number;
}

interface MemoryThresholds {
  warning: number;
  critical: number;
  gcTrigger: number;
}

export class MemoryOptimizer extends EventEmitter {
  private readonly thresholds: MemoryThresholds;
  private monitoringInterval?: NodeJS.Timer;
  private objectPools: Map<string, any[]> = new Map();
  private weakRefs: Set<WeakRef<any>> = new Set();
  
  constructor(thresholds: MemoryThresholds = {
    warning: 512 * 1024 * 1024,    // 512MB
    critical: 1024 * 1024 * 1024,  // 1GB
    gcTrigger: 768 * 1024 * 1024   // 768MB
  }) {
    super();
    this.thresholds = thresholds;
  }
  
  startMonitoring(intervalMs: number = 30000): void {
    this.monitoringInterval = setInterval(() => {
      this.checkMemoryUsage();
    }, intervalMs);
    
    logger.info('Memory monitoring started');
  }
  
  stopMonitoring(): void {
    if (this.monitoringInterval) {
      clearInterval(this.monitoringInterval);
      this.monitoringInterval = undefined;
    }
  }
  
  private checkMemoryUsage(): void {
    const stats = this.getMemoryStats();
    
    if (stats.heapUsed > this.thresholds.critical) {
      this.emit('critical', stats);
      this.performEmergencyCleanup();
    } else if (stats.heapUsed > this.thresholds.warning) {
      this.emit('warning', stats);
    }
    
    if (stats.heapUsed > this.thresholds.gcTrigger) {
      this.triggerGarbageCollection();
    }
  }
  
  getMemoryStats(): MemoryStats {
    const usage = process.memoryUsage();
    return {
      heapUsed: usage.heapUsed,
      heapTotal: usage.heapTotal,
      external: usage.external,
      rss: usage.rss,
      arrayBuffers: usage.arrayBuffers
    };
  }
  
  // 객체 풀링
  createPool<T>(name: string, factory: () => T, maxSize: number = 100): void {
    if (!this.objectPools.has(name)) {
      this.objectPools.set(name, []);
    }
  }
  
  getFromPool<T>(name: string, factory: () => T): T {
    const pool = this.objectPools.get(name);
    if (pool && pool.length > 0) {
      return pool.pop() as T;
    }
    return factory();
  }
  
  returnToPool<T>(name: string, obj: T): void {
    const pool = this.objectPools.get(name);
    if (pool && pool.length < 100) {
      // 객체 초기화
      if (typeof obj === 'object' && obj !== null) {
        Object.keys(obj).forEach(key => {
          delete (obj as any)[key];
        });
      }
      pool.push(obj);
    }
  }
  
  // WeakRef 관리
  addWeakRef<T extends object>(obj: T): WeakRef<T> {
    const ref = new WeakRef(obj);
    this.weakRefs.add(ref);
    return ref;
  }
  
  cleanupWeakRefs(): number {
    let cleaned = 0;
    for (const ref of this.weakRefs) {
      if (ref.deref() === undefined) {
        this.weakRefs.delete(ref);
        cleaned++;
      }
    }
    return cleaned;
  }
  
  private triggerGarbageCollection(): void {
    if (global.gc) {
      global.gc();
      logger.debug('Garbage collection triggered');
    }
  }
  
  private performEmergencyCleanup(): void {
    // 캐시 정리
    this.clearCaches();
    
    // WeakRef 정리
    this.cleanupWeakRefs();
    
    // 강제 GC
    this.triggerGarbageCollection();
    
    logger.warn('Emergency memory cleanup performed');
  }
  
  private clearCaches(): void {
    // 객체 풀 정리
    for (const [name, pool] of this.objectPools) {
      pool.length = Math.min(pool.length, 10);
    }
  }
}

// 메모리 효율적인 스트림 처리
export class MemoryEfficientStream {
  private readonly chunkSize: number;
  private buffer: Buffer[] = [];
  private bufferSize: number = 0;
  
  constructor(chunkSize: number = 64 * 1024) {
    this.chunkSize = chunkSize;
  }
  
  async *processLargeData<T>(
    data: T[],
    processor: (chunk: T[]) => Promise<any>
  ): AsyncGenerator<any, void, unknown> {
    for (let i = 0; i < data.length; i += this.chunkSize) {
      const chunk = data.slice(i, i + this.chunkSize);
      const result = await processor(chunk);
      yield result;
      
      // 메모리 압박 시 일시 정지
      if (process.memoryUsage().heapUsed > 500 * 1024 * 1024) {
        await new Promise(resolve => setTimeout(resolve, 100));
      }
    }
  }
}

// 메모리 프로파일러
export class MemoryProfiler {
  private snapshots: MemoryStats[] = [];
  private readonly maxSnapshots = 100;
  
  takeSnapshot(): MemoryStats {
    const stats = process.memoryUsage();
    const snapshot: MemoryStats = {
      heapUsed: stats.heapUsed,
      heapTotal: stats.heapTotal,
      external: stats.external,
      rss: stats.rss,
      arrayBuffers: stats.arrayBuffers
    };
    
    this.snapshots.push(snapshot);
    
    if (this.snapshots.length > this.maxSnapshots) {
      this.snapshots.shift();
    }
    
    return snapshot;
  }
  
  getMemoryTrend(): {
    trend: 'increasing' | 'decreasing' | 'stable';
    averageGrowth: number;
  } {
    if (this.snapshots.length < 2) {
      return { trend: 'stable', averageGrowth: 0 };
    }
    
    const recent = this.snapshots.slice(-10);
    const growthRates = [];
    
    for (let i = 1; i < recent.length; i++) {
      const growth = recent[i].heapUsed - recent[i-1].heapUsed;
      growthRates.push(growth);
    }
    
    const averageGrowth = growthRates.reduce((a, b) => a + b, 0) / growthRates.length;
    
    let trend: 'increasing' | 'decreasing' | 'stable';
    if (averageGrowth > 1024 * 1024) { // 1MB
      trend = 'increasing';
    } else if (averageGrowth < -1024 * 1024) {
      trend = 'decreasing';
    } else {
      trend = 'stable';
    }
    
    return { trend, averageGrowth };
  }
}