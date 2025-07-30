// SubTask 1.18.3: 메모리 및 리소스 프로파일링
interface MemorySnapshot {
  timestamp: number;
  heapUsed: number;
  heapTotal: number;
  external: number;
  rss: number;
  arrayBuffers: number;
}

interface ProfileResult {
  duration: number;
  snapshots: MemorySnapshot[];
  leaks: MemoryLeak[];
  peaks: MemoryPeak[];
  summary: {
    maxHeapUsed: number;
    avgHeapUsed: number;
    memoryGrowth: number;
    gcCount: number;
  };
}

interface MemoryLeak {
  type: string;
  size: number;
  location: string;
  severity: 'low' | 'medium' | 'high';
}

interface MemoryPeak {
  timestamp: number;
  heapUsed: number;
  trigger: string;
}

export class MemoryProfiler {
  private snapshots: MemorySnapshot[] = [];
  private isRunning = false;
  private interval?: NodeJS.Timer;
  
  start(intervalMs: number = 1000): void {
    if (this.isRunning) return;
    
    this.isRunning = true;
    this.snapshots = [];
    
    this.interval = setInterval(() => {
      this.takeSnapshot();
    }, intervalMs);
  }
  
  stop(): ProfileResult {
    if (!this.isRunning) {
      throw new Error('Profiler not running');
    }
    
    this.isRunning = false;
    if (this.interval) {
      clearInterval(this.interval);
    }
    
    return this.analyzeProfile();
  }
  
  private takeSnapshot(): void {
    const memUsage = process.memoryUsage();
    
    this.snapshots.push({
      timestamp: Date.now(),
      heapUsed: memUsage.heapUsed,
      heapTotal: memUsage.heapTotal,
      external: memUsage.external,
      rss: memUsage.rss,
      arrayBuffers: memUsage.arrayBuffers || 0
    });
  }
  
  private analyzeProfile(): ProfileResult {
    if (this.snapshots.length === 0) {
      throw new Error('No snapshots available');
    }
    
    const duration = this.snapshots[this.snapshots.length - 1].timestamp - this.snapshots[0].timestamp;
    const heapValues = this.snapshots.map(s => s.heapUsed);
    
    return {
      duration,
      snapshots: this.snapshots,
      leaks: this.detectMemoryLeaks(),
      peaks: this.detectMemoryPeaks(),
      summary: {
        maxHeapUsed: Math.max(...heapValues),
        avgHeapUsed: heapValues.reduce((a, b) => a + b, 0) / heapValues.length,
        memoryGrowth: this.calculateMemoryGrowth(),
        gcCount: this.estimateGCCount()
      }
    };
  }
  
  private detectMemoryLeaks(): MemoryLeak[] {
    const leaks: MemoryLeak[] = [];
    
    // Simple leak detection based on memory growth
    const growth = this.calculateMemoryGrowth();
    
    if (growth > 50 * 1024 * 1024) { // 50MB growth
      leaks.push({
        type: 'heap_growth',
        size: growth,
        location: 'unknown',
        severity: growth > 100 * 1024 * 1024 ? 'high' : 'medium'
      });
    }
    
    return leaks;
  }
  
  private detectMemoryPeaks(): MemoryPeak[] {
    const peaks: MemoryPeak[] = [];
    const threshold = this.calculatePeakThreshold();
    
    for (let i = 1; i < this.snapshots.length - 1; i++) {
      const current = this.snapshots[i];
      const prev = this.snapshots[i - 1];
      const next = this.snapshots[i + 1];
      
      if (current.heapUsed > threshold &&
          current.heapUsed > prev.heapUsed &&
          current.heapUsed > next.heapUsed) {
        peaks.push({
          timestamp: current.timestamp,
          heapUsed: current.heapUsed,
          trigger: 'unknown'
        });
      }
    }
    
    return peaks;
  }
  
  private calculateMemoryGrowth(): number {
    if (this.snapshots.length < 2) return 0;
    
    const first = this.snapshots[0].heapUsed;
    const last = this.snapshots[this.snapshots.length - 1].heapUsed;
    
    return last - first;
  }
  
  private calculatePeakThreshold(): number {
    const heapValues = this.snapshots.map(s => s.heapUsed);
    const avg = heapValues.reduce((a, b) => a + b, 0) / heapValues.length;
    const stdDev = Math.sqrt(
      heapValues.reduce((sum, val) => sum + Math.pow(val - avg, 2), 0) / heapValues.length
    );
    
    return avg + (2 * stdDev);
  }
  
  private estimateGCCount(): number {
    // Estimate GC events based on heap decreases
    let gcCount = 0;
    
    for (let i = 1; i < this.snapshots.length; i++) {
      const current = this.snapshots[i];
      const prev = this.snapshots[i - 1];
      
      // Significant heap decrease indicates GC
      if (prev.heapUsed - current.heapUsed > 10 * 1024 * 1024) { // 10MB decrease
        gcCount++;
      }
    }
    
    return gcCount;
  }
  
  // Heap dump analysis
  async analyzeHeapDump(): Promise<HeapAnalysis> {
    // Mock heap analysis
    return {
      totalSize: process.memoryUsage().heapUsed,
      objectCount: 0,
      topObjects: [],
      retainedSize: 0
    };
  }
}

interface HeapAnalysis {
  totalSize: number;
  objectCount: number;
  topObjects: any[];
  retainedSize: number;
}

export class ResourceMonitor {
  private cpuUsage: number[] = [];
  private isMonitoring = false;
  
  startMonitoring(intervalMs: number = 1000): void {
    if (this.isMonitoring) return;
    
    this.isMonitoring = true;
    this.cpuUsage = [];
    
    setInterval(() => {
      const usage = process.cpuUsage();
      const cpuPercent = (usage.user + usage.system) / 1000000; // Convert to seconds
      this.cpuUsage.push(cpuPercent);
    }, intervalMs);
  }
  
  stopMonitoring(): ResourceReport {
    this.isMonitoring = false;
    
    return {
      cpu: {
        avg: this.cpuUsage.reduce((a, b) => a + b, 0) / this.cpuUsage.length,
        max: Math.max(...this.cpuUsage),
        min: Math.min(...this.cpuUsage)
      },
      memory: process.memoryUsage(),
      uptime: process.uptime()
    };
  }
}

interface ResourceReport {
  cpu: {
    avg: number;
    max: number;
    min: number;
  };
  memory: NodeJS.MemoryUsage;
  uptime: number;
}