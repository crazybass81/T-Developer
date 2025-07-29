import { EventEmitter } from 'events';
import os from 'os';
import v8 from 'v8';
import { Express } from 'express';

interface PerformanceMetrics {
  cpu: {
    usage: number;
    loadAverage: number[];
  };
  memory: {
    heapUsed: number;
    heapTotal: number;
    external: number;
    rss: number;
  };
  eventLoop: {
    delay: number;
  };
  gc: {
    count: number;
    duration: number;
    type: string;
  }[];
}

export class APMService extends EventEmitter {
  private metrics: PerformanceMetrics;
  private thresholds = {
    cpu: { warning: 70, critical: 90 },
    memory: { warning: 80, critical: 95 },
    eventLoopDelay: { warning: 100, critical: 500 }
  };
  private monitoringInterval: NodeJS.Timer | null = null;
  
  constructor() {
    super();
    this.initializeMetrics();
  }
  
  private initializeMetrics(): void {
    this.metrics = {
      cpu: { usage: 0, loadAverage: [0, 0, 0] },
      memory: { heapUsed: 0, heapTotal: 0, external: 0, rss: 0 },
      eventLoop: { delay: 0 },
      gc: []
    };
  }
  
  start(intervalMs: number = 5000): void {
    if (this.monitoringInterval) return;
    
    this.monitoringInterval = setInterval(() => {
      this.collectMetrics();
      this.checkThresholds();
      this.emit('metrics', this.metrics);
    }, intervalMs);
    
    this.measureEventLoopDelay();
  }
  
  stop(): void {
    if (this.monitoringInterval) {
      clearInterval(this.monitoringInterval);
      this.monitoringInterval = null;
    }
  }
  
  private collectMetrics(): void {
    const cpus = os.cpus();
    const cpuUsage = cpus.reduce((acc, cpu) => {
      const total = Object.values(cpu.times).reduce((a, b) => a + b, 0);
      const idle = cpu.times.idle;
      return acc + ((total - idle) / total) * 100;
    }, 0) / cpus.length;
    
    this.metrics.cpu = {
      usage: Math.round(cpuUsage),
      loadAverage: os.loadavg()
    };
    
    const memUsage = process.memoryUsage();
    this.metrics.memory = {
      heapUsed: memUsage.heapUsed,
      heapTotal: memUsage.heapTotal,
      external: memUsage.external,
      rss: memUsage.rss
    };
    
    const heapStats = v8.getHeapStatistics();
    const heapUsedPercent = (heapStats.used_heap_size / heapStats.heap_size_limit) * 100;
    
    if (heapUsedPercent > this.thresholds.memory.critical) {
      this.emit('alert', {
        level: 'critical',
        type: 'memory',
        message: `Memory usage critical: ${heapUsedPercent.toFixed(2)}%`,
        value: heapUsedPercent
      });
    }
  }
  
  private measureEventLoopDelay(): void {
    const lastCheck = process.hrtime.bigint();
    
    setImmediate(() => {
      const delay = Number(process.hrtime.bigint() - lastCheck) / 1e6;
      this.metrics.eventLoop.delay = delay;
      
      if (delay > this.thresholds.eventLoopDelay.critical) {
        this.emit('alert', {
          level: 'critical',
          type: 'eventLoop',
          message: `Event loop delay critical: ${delay.toFixed(2)}ms`,
          value: delay
        });
      }
      
      if (this.monitoringInterval) {
        this.measureEventLoopDelay();
      }
    });
  }
  
  private checkThresholds(): void {
    if (this.metrics.cpu.usage > this.thresholds.cpu.critical) {
      this.emit('alert', {
        level: 'critical',
        type: 'cpu',
        message: `CPU usage critical: ${this.metrics.cpu.usage}%`,
        value: this.metrics.cpu.usage
      });
    } else if (this.metrics.cpu.usage > this.thresholds.cpu.warning) {
      this.emit('alert', {
        level: 'warning',
        type: 'cpu',
        message: `CPU usage warning: ${this.metrics.cpu.usage}%`,
        value: this.metrics.cpu.usage
      });
    }
  }
  
  getMetrics(): PerformanceMetrics {
    return { ...this.metrics };
  }
  
  getHealthStatus(): { healthy: boolean; issues: string[] } {
    const issues: string[] = [];
    
    if (this.metrics.cpu.usage > this.thresholds.cpu.warning) {
      issues.push(`High CPU usage: ${this.metrics.cpu.usage}%`);
    }
    
    const heapUsedPercent = (this.metrics.memory.heapUsed / this.metrics.memory.heapTotal) * 100;
    if (heapUsedPercent > this.thresholds.memory.warning) {
      issues.push(`High memory usage: ${heapUsedPercent.toFixed(2)}%`);
    }
    
    if (this.metrics.eventLoop.delay > this.thresholds.eventLoopDelay.warning) {
      issues.push(`High event loop delay: ${this.metrics.eventLoop.delay.toFixed(2)}ms`);
    }
    
    return {
      healthy: issues.length === 0,
      issues
    };
  }
}

export const apmService = new APMService();

export function apmEndpoints(app: Express): void {
  app.get('/api/monitoring/metrics', (req, res) => {
    res.json(apmService.getMetrics());
  });
  
  app.get('/api/monitoring/health', (req, res) => {
    const health = apmService.getHealthStatus();
    res.status(health.healthy ? 200 : 503).json(health);
  });
  
  app.get('/api/monitoring/stream', (req, res) => {
    res.writeHead(200, {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive'
    });
    
    const sendMetrics = (metrics: PerformanceMetrics) => {
      res.write(`data: ${JSON.stringify(metrics)}\n\n`);
    };
    
    apmService.on('metrics', sendMetrics);
    
    req.on('close', () => {
      apmService.removeListener('metrics', sendMetrics);
    });
  });
}