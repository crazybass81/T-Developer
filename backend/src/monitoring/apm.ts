import { EventEmitter } from 'events';
import os from 'os';
import v8 from 'v8';
import { Express, Request, Response } from 'express';

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

interface Alert {
  level: 'warning' | 'critical';
  type: string;
  message: string;
  value: number;
  timestamp: Date;
}

export class APMService extends EventEmitter {
  private metrics: PerformanceMetrics = {
    cpu: { usage: 0, loadAverage: [0, 0, 0] },
    memory: { heapUsed: 0, heapTotal: 0, external: 0, rss: 0 },
    eventLoop: { delay: 0 },
    gc: []
  };
  private thresholds = {
    cpu: { warning: 70, critical: 90 },
    memory: { warning: 80, critical: 95 },
    eventLoopDelay: { warning: 100, critical: 500 }
  };
  private monitoringInterval: NodeJS.Timeout | null = null;
  
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
    // CPU metrics
    const cpus = os.cpus();
    let totalIdle = 0;
    let totalTick = 0;
    
    cpus.forEach(cpu => {
      for (const type in cpu.times) {
        totalTick += cpu.times[type as keyof typeof cpu.times];
      }
      totalIdle += cpu.times.idle;
    });
    
    const idle = totalIdle / cpus.length;
    const total = totalTick / cpus.length;
    const usage = 100 - ~~(100 * idle / total);
    
    this.metrics.cpu = {
      usage,
      loadAverage: os.loadavg()
    };
    
    // Memory metrics
    const memUsage = process.memoryUsage();
    this.metrics.memory = {
      heapUsed: memUsage.heapUsed,
      heapTotal: memUsage.heapTotal,
      external: memUsage.external,
      rss: memUsage.rss
    };
    
    // Clear old GC data
    this.metrics.gc = [];
  }
  
  private measureEventLoopDelay(): void {
    const start = process.hrtime.bigint();
    
    setImmediate(() => {
      const delay = Number(process.hrtime.bigint() - start) / 1e6;
      this.metrics.eventLoop.delay = delay;
      
      if (this.monitoringInterval) {
        this.measureEventLoopDelay();
      }
    });
  }
  
  private checkThresholds(): void {
    const alerts: Alert[] = [];
    
    // CPU threshold check
    if (this.metrics.cpu.usage > this.thresholds.cpu.critical) {
      alerts.push({
        level: 'critical',
        type: 'cpu',
        message: `CPU usage critical: ${this.metrics.cpu.usage}%`,
        value: this.metrics.cpu.usage,
        timestamp: new Date()
      });
    } else if (this.metrics.cpu.usage > this.thresholds.cpu.warning) {
      alerts.push({
        level: 'warning',
        type: 'cpu',
        message: `CPU usage warning: ${this.metrics.cpu.usage}%`,
        value: this.metrics.cpu.usage,
        timestamp: new Date()
      });
    }
    
    // Memory threshold check
    const heapUsedPercent = (this.metrics.memory.heapUsed / this.metrics.memory.heapTotal) * 100;
    if (heapUsedPercent > this.thresholds.memory.critical) {
      alerts.push({
        level: 'critical',
        type: 'memory',
        message: `Memory usage critical: ${heapUsedPercent.toFixed(2)}%`,
        value: heapUsedPercent,
        timestamp: new Date()
      });
    } else if (heapUsedPercent > this.thresholds.memory.warning) {
      alerts.push({
        level: 'warning',
        type: 'memory',
        message: `Memory usage warning: ${heapUsedPercent.toFixed(2)}%`,
        value: heapUsedPercent,
        timestamp: new Date()
      });
    }
    
    // Event loop delay check
    if (this.metrics.eventLoop.delay > this.thresholds.eventLoopDelay.critical) {
      alerts.push({
        level: 'critical',
        type: 'eventLoop',
        message: `Event loop delay critical: ${this.metrics.eventLoop.delay.toFixed(2)}ms`,
        value: this.metrics.eventLoop.delay,
        timestamp: new Date()
      });
    } else if (this.metrics.eventLoop.delay > this.thresholds.eventLoopDelay.warning) {
      alerts.push({
        level: 'warning',
        type: 'eventLoop',
        message: `Event loop delay warning: ${this.metrics.eventLoop.delay.toFixed(2)}ms`,
        value: this.metrics.eventLoop.delay,
        timestamp: new Date()
      });
    }
    
    // Emit alerts
    alerts.forEach(alert => this.emit('alert', alert));
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

// APM service instance
export const apmService = new APMService();

// Express endpoints
export function apmEndpoints(app: Express): void {
  // Real-time metrics
  app.get('/api/monitoring/metrics', (req: Request, res: Response) => {
    res.json(apmService.getMetrics());
  });
  
  // Health check
  app.get('/api/monitoring/health', (req: Request, res: Response) => {
    const health = apmService.getHealthStatus();
    res.status(health.healthy ? 200 : 503).json(health);
  });
  
  // Metrics streaming (SSE)
  app.get('/api/monitoring/stream', (req: Request, res: Response) => {
    res.writeHead(200, {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive',
      'Access-Control-Allow-Origin': '*'
    });
    
    const sendMetrics = (metrics: PerformanceMetrics) => {
      res.write(`data: ${JSON.stringify(metrics)}\n\n`);
    };
    
    const sendAlert = (alert: Alert) => {
      res.write(`event: alert\ndata: ${JSON.stringify(alert)}\n\n`);
    };
    
    apmService.on('metrics', sendMetrics);
    apmService.on('alert', sendAlert);
    
    // Send initial metrics
    sendMetrics(apmService.getMetrics());
    
    req.on('close', () => {
      apmService.removeListener('metrics', sendMetrics);
      apmService.removeListener('alert', sendAlert);
    });
  });
}