import v8 from 'v8';
import { performance, PerformanceObserver } from 'perf_hooks';
import { EventEmitter } from 'events';

const MEMORY_THRESHOLDS = {
  WARNING: 1024,
  CRITICAL: 1536,
  MAX: 2048
};

export class MemoryManager extends EventEmitter {
  private monitoringInterval: NodeJS.Timeout | null = null;
  private gcForceThreshold = 0.85;
  private memoryLeakDetector: MemoryLeakDetector;
  
  constructor() {
    super();
    this.memoryLeakDetector = new MemoryLeakDetector();
    this.setupGCEvents();
  }
  
  startMonitoring(intervalMs: number = 30000): void {
    if (this.monitoringInterval) return;
    
    this.monitoringInterval = setInterval(() => {
      this.checkMemoryUsage();
    }, intervalMs);
    
    console.log('Memory monitoring started');
  }
  
  stopMonitoring(): void {
    if (this.monitoringInterval) {
      clearInterval(this.monitoringInterval);
      this.monitoringInterval = null;
      console.log('Memory monitoring stopped');
    }
  }
  
  getMemoryStatus(): MemoryStatus {
    const memUsage = process.memoryUsage();
    const heapStats = v8.getHeapStatistics();
    
    const heapUsedMB = memUsage.heapUsed / 1024 / 1024;
    const heapTotalMB = memUsage.heapTotal / 1024 / 1024;
    const rssMB = memUsage.rss / 1024 / 1024;
    const externalMB = memUsage.external / 1024 / 1024;
    
    const heapUsagePercent = (heapStats.used_heap_size / heapStats.heap_size_limit) * 100;
    
    return {
      rss: rssMB,
      heapUsed: heapUsedMB,
      heapTotal: heapTotalMB,
      external: externalMB,
      heapUsagePercent,
      heapSizeLimit: heapStats.heap_size_limit / 1024 / 1024,
      totalPhysicalSize: heapStats.total_physical_size / 1024 / 1024,
      totalAvailableSize: heapStats.total_available_size / 1024 / 1024,
      usedHeapSize: heapStats.used_heap_size / 1024 / 1024,
      heapSpaces: this.getHeapSpaceInfo()
    };
  }
  
  private getHeapSpaceInfo(): HeapSpaceInfo[] {
    const spaces = v8.getHeapSpaceStatistics();
    return spaces.map(space => ({
      spaceName: space.space_name,
      spaceSize: space.space_size / 1024 / 1024,
      spaceUsedSize: space.space_used_size / 1024 / 1024,
      spaceAvailableSize: space.space_available_size / 1024 / 1024,
      physicalSpaceSize: space.physical_space_size / 1024 / 1024
    }));
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
    console.error('Critical memory usage detected', status);
    
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
      const entries = list.getEntries();
      entries.forEach((entry) => {
        if (entry.entryType === 'gc') {
          this.handleGCEvent(entry as any);
        }
      });
    });
    
    obs.observe({ entryTypes: ['gc'] });
  }
  
  private handleGCEvent(gcEntry: any): void {
    const gcInfo = {
      type: gcEntry.detail?.kind || 'unknown',
      duration: gcEntry.duration,
      timestamp: gcEntry.startTime
    };
    
    this.emit('gc', gcInfo);
    
    if (gcEntry.duration > 100) {
      console.warn('Long GC detected', gcInfo);
    }
  }
  
  async createHeapSnapshot(filename?: string): Promise<string> {
    const snapshotPath = filename || `heapdump-${Date.now()}.heapsnapshot`;
    
    return new Promise((resolve, reject) => {
      try {
        v8.writeHeapSnapshot(snapshotPath);
        console.log(`Heap snapshot created: ${snapshotPath}`);
        resolve(snapshotPath);
      } catch (error) {
        reject(error);
      }
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
        r2: trend.r2,
        currentHeap: recentSamples[recentSamples.length - 1].heapUsed
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
    const intercept = (sumY - slope * sumX) / n;
    
    const yMean = sumY / n;
    const ssTotal = y.reduce((sum, yi) => sum + Math.pow(yi - yMean, 2), 0);
    const ssResidual = y.reduce((sum, yi, i) => {
      const prediction = slope * x[i] + intercept;
      return sum + Math.pow(yi - prediction, 2);
    }, 0);
    
    const r2 = 1 - (ssResidual / ssTotal);
    
    return { slope: slope / yMean, r2 };
  }
}

export class MemoryPoolManager<T> {
  private pool: T[] = [];
  private inUse: Set<T> = new Set();
  private factory: () => T;
  private reset: (obj: T) => void;
  private maxSize: number;
  
  constructor(options: {
    factory: () => T;
    reset: (obj: T) => void;
    initialSize?: number;
    maxSize?: number;
  }) {
    this.factory = options.factory;
    this.reset = options.reset;
    this.maxSize = options.maxSize || 100;
    
    const initialSize = options.initialSize || 10;
    for (let i = 0; i < initialSize; i++) {
      this.pool.push(this.factory());
    }
  }
  
  acquire(): T {
    let obj = this.pool.pop();
    
    if (!obj) {
      obj = this.factory();
    }
    
    this.inUse.add(obj);
    return obj;
  }
  
  release(obj: T): void {
    if (!this.inUse.has(obj)) {
      return;
    }
    
    this.inUse.delete(obj);
    this.reset(obj);
    
    if (this.pool.length < this.maxSize) {
      this.pool.push(obj);
    }
  }
  
  getStats(): { poolSize: number; inUse: number } {
    return {
      poolSize: this.pool.length,
      inUse: this.inUse.size
    };
  }
  
  clear(): void {
    this.pool = [];
    this.inUse.clear();
  }
}

export class WeakCache<K extends object, V> {
  private cache = new WeakMap<K, { value: V; timestamp: number }>();
  private ttl: number;
  
  constructor(ttlMs: number = 60000) {
    this.ttl = ttlMs;
  }
  
  set(key: K, value: V): void {
    this.cache.set(key, {
      value,
      timestamp: Date.now()
    });
  }
  
  get(key: K): V | undefined {
    const entry = this.cache.get(key);
    
    if (!entry) {
      return undefined;
    }
    
    if (Date.now() - entry.timestamp > this.ttl) {
      this.cache.delete(key);
      return undefined;
    }
    
    return entry.value;
  }
  
  has(key: K): boolean {
    return this.get(key) !== undefined;
  }
  
  delete(key: K): boolean {
    return this.cache.delete(key);
  }
}

interface MemoryStatus {
  rss: number;
  heapUsed: number;
  heapTotal: number;
  external: number;
  heapUsagePercent: number;
  heapSizeLimit: number;
  totalPhysicalSize: number;
  totalAvailableSize: number;
  usedHeapSize: number;
  heapSpaces: HeapSpaceInfo[];
}

interface HeapSpaceInfo {
  spaceName: string;
  spaceSize: number;
  spaceUsedSize: number;
  spaceAvailableSize: number;
  physicalSpaceSize: number;
}