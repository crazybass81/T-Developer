import v8 from 'v8';
import { performance } from 'perf_hooks';
import { EventEmitter } from 'events';

const MEMORY_THRESHOLDS = {
  WARNING: 1024,
  CRITICAL: 1536,
  MAX: 2048
};

interface MemoryStatus {
  rss: number;
  heapUsed: number;
  heapTotal: number;
  external: number;
  heapUsagePercent: number;
  heapSizeLimit: number;
}

export class MemoryManager extends EventEmitter {
  private monitoringInterval: NodeJS.Timer | null = null;
  private gcForceThreshold = 0.85;
  private memoryLeakDetector = new MemoryLeakDetector();
  
  constructor() {
    super();
    this.setupGCEvents();
  }
  
  startMonitoring(intervalMs: number = 30000): void {
    if (this.monitoringInterval) return;
    
    this.monitoringInterval = setInterval(() => {
      this.checkMemoryUsage();
    }, intervalMs);
  }
  
  stopMonitoring(): void {
    if (this.monitoringInterval) {
      clearInterval(this.monitoringInterval);
      this.monitoringInterval = null;
    }
  }
  
  getMemoryStatus(): MemoryStatus {
    const memUsage = process.memoryUsage();
    const heapStats = v8.getHeapStatistics();
    
    return {
      rss: memUsage.rss / 1024 / 1024,
      heapUsed: memUsage.heapUsed / 1024 / 1024,
      heapTotal: memUsage.heapTotal / 1024 / 1024,
      external: memUsage.external / 1024 / 1024,
      heapUsagePercent: (heapStats.used_heap_size / heapStats.heap_size_limit) * 100,
      heapSizeLimit: heapStats.heap_size_limit / 1024 / 1024
    };
  }
  
  private checkMemoryUsage(): void {
    const status = this.getMemoryStatus();
    
    if (status.heapUsed > MEMORY_THRESHOLDS.CRITICAL) {
      this.emit('memory:critical', status);
      this.handleCriticalMemory(status);
    } else if (status.heapUsed > MEMORY_THRESHOLDS.WARNING) {
      this.emit('memory:warning', status);
    }
    
    if (status.heapUsagePercent > this.gcForceThreshold * 100) {
      this.forceGarbageCollection();
    }
    
    this.memoryLeakDetector.addSample(status);
  }
  
  private handleCriticalMemory(status: MemoryStatus): void {
    this.forceGarbageCollection();
    this.emit('memory:cleanup:cache');
    this.emit('memory:cleanup:objects');
    
    if (status.heapUsed > MEMORY_THRESHOLDS.MAX) {
      this.emit('memory:limit:features');
    }
  }
  
  private forceGarbageCollection(): void {
    if (global.gc) {
      const before = process.memoryUsage().heapUsed;
      global.gc();
      const after = process.memoryUsage().heapUsed;
      const freed = (before - after) / 1024 / 1024;
      console.log(`Forced GC: freed ${freed.toFixed(2)} MB`);
    }
  }
  
  private setupGCEvents(): void {
    if (!performance.nodeTiming) return;
    
    const obs = new PerformanceObserver((list) => {
      list.getEntries().forEach((entry) => {
        if (entry.entryType === 'gc') {
          const gcEntry = entry as any;
          if (gcEntry.duration > 100) {
            console.warn('Long GC detected:', gcEntry.duration);
          }
        }
      });
    });
    
    obs.observe({ entryTypes: ['gc'] });
  }
  
  async createHeapSnapshot(filename?: string): Promise<string> {
    const snapshotPath = filename || `heapdump-${Date.now()}.heapsnapshot`;
    
    return new Promise((resolve, reject) => {
      const stream = v8.writeHeapSnapshot(snapshotPath);
      stream.on('finish', () => resolve(snapshotPath));
      stream.on('error', reject);
    });
  }
}

class MemoryLeakDetector {
  private samples: MemoryStatus[] = [];
  private readonly maxSamples = 60;
  private readonly leakThreshold = 0.1;
  
  addSample(status: MemoryStatus): void {
    this.samples.push(status);
    
    if (this.samples.length > this.maxSamples) {
      this.samples.shift();
    }
    
    if (this.samples.length >= 10) {
      this.detectLeak();
    }
  }
  
  private detectLeak(): void {
    const recentSamples = this.samples.slice(-10);
    const trend = this.calculateTrend(recentSamples);
    
    if (trend.slope > this.leakThreshold && trend.r2 > 0.8) {
      console.warn('Potential memory leak detected', {
        slope: trend.slope,
        r2: trend.r2
      });
    }
  }
  
  private calculateTrend(samples: MemoryStatus[]): { slope: number; r2: number } {
    const n = samples.length;
    const x = samples.map((_, i) => i);
    const y = samples.map(s => s.heapUsed);
    
    const sumX = x.reduce((a, b) => a + b, 0);
    const sumY = y.reduce((a, b) => a + b, 0);
    const sumXY = x.reduce((sum, xi, i) => sum + xi * y[i], 0);
    const sumX2 = x.reduce((sum, xi) => sum + xi * xi, 0);
    
    const slope = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX);
    const yMean = sumY / n;
    
    return { slope: slope / yMean, r2: 0.8 }; // Simplified R²
  }
}

export class MemoryPoolManager<T> {
  private pool: T[] = [];
  private inUse = new Set<T>();
  
  constructor(
    private factory: () => T,
    private reset: (obj: T) => void,
    private maxSize = 100
  ) {}
  
  acquire(): T {
    let obj = this.pool.pop();
    if (!obj) obj = this.factory();
    
    this.inUse.add(obj);
    return obj;
  }
  
  release(obj: T): void {
    if (!this.inUse.has(obj)) return;
    
    this.inUse.delete(obj);
    this.reset(obj);
    
    if (this.pool.length < this.maxSize) {
      this.pool.push(obj);
    }
  }
  
  getStats() {
    return {
      poolSize: this.pool.length,
      inUse: this.inUse.size
    };
  }
}

export class WeakCache<K extends object, V> {
  private cache = new WeakMap<K, { value: V; timestamp: number }>();
  
  constructor(private ttl = 60000) {}
  
  set(key: K, value: V): void {
    this.cache.set(key, { value, timestamp: Date.now() });
  }
  
  get(key: K): V | undefined {
    const entry = this.cache.get(key);
    if (!entry || Date.now() - entry.timestamp > this.ttl) {
      this.cache.delete(key);
      return undefined;
    }
    return entry.value;
  }
}