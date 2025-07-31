import { StreamEvent } from './event-stream';

export interface AnalyticsConfig {
  windowSize: number; // in milliseconds
  aggregationInterval: number;
  retentionPeriod: number;
}

export interface StreamMetrics {
  eventCount: number;
  eventsPerSecond: number;
  errorRate: number;
  latency: {
    avg: number;
    p95: number;
    p99: number;
  };
  topEventTypes: Array<{ type: string; count: number }>;
}

export class StreamAnalytics {
  private events: StreamEvent[] = [];
  private metrics: StreamMetrics = {
    eventCount: 0,
    eventsPerSecond: 0,
    errorRate: 0,
    latency: { avg: 0, p95: 0, p99: 0 },
    topEventTypes: []
  };
  private windowStart = Date.now();

  constructor(private config: AnalyticsConfig) {
    this.startAggregation();
    this.startCleanup();
  }

  recordEvent(event: StreamEvent, processingTime?: number): void {
    const enrichedEvent = {
      ...event,
      processingTime,
      recordedAt: Date.now()
    };
    
    this.events.push(enrichedEvent);
    this.metrics.eventCount++;
  }

  recordError(event: StreamEvent, error: Error): void {
    this.recordEvent({
      ...event,
      type: 'ERROR',
      data: { originalEvent: event, error: error.message }
    });
  }

  private startAggregation(): void {
    setInterval(() => {
      this.calculateMetrics();
    }, this.config.aggregationInterval);
  }

  private startCleanup(): void {
    setInterval(() => {
      const cutoff = Date.now() - this.config.retentionPeriod;
      this.events = this.events.filter(e => e.recordedAt > cutoff);
    }, this.config.retentionPeriod / 10);
  }

  private calculateMetrics(): void {
    const now = Date.now();
    const windowEvents = this.events.filter(
      e => e.recordedAt > now - this.config.windowSize
    );

    // Events per second
    this.metrics.eventsPerSecond = windowEvents.length / (this.config.windowSize / 1000);

    // Error rate
    const errorEvents = windowEvents.filter(e => e.type === 'ERROR');
    this.metrics.errorRate = windowEvents.length > 0 
      ? errorEvents.length / windowEvents.length 
      : 0;

    // Latency metrics
    const processingTimes = windowEvents
      .map(e => e.processingTime)
      .filter(t => t !== undefined)
      .sort((a, b) => a - b);

    if (processingTimes.length > 0) {
      this.metrics.latency.avg = processingTimes.reduce((a, b) => a + b, 0) / processingTimes.length;
      this.metrics.latency.p95 = processingTimes[Math.floor(processingTimes.length * 0.95)];
      this.metrics.latency.p99 = processingTimes[Math.floor(processingTimes.length * 0.99)];
    }

    // Top event types
    const eventTypeCounts = new Map<string, number>();
    windowEvents.forEach(e => {
      eventTypeCounts.set(e.type, (eventTypeCounts.get(e.type) || 0) + 1);
    });

    this.metrics.topEventTypes = Array.from(eventTypeCounts.entries())
      .map(([type, count]) => ({ type, count }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 10);
  }

  getMetrics(): StreamMetrics {
    return { ...this.metrics };
  }

  getEventsByType(type: string, limit = 100): StreamEvent[] {
    return this.events
      .filter(e => e.type === type)
      .slice(-limit);
  }

  getEventsInTimeRange(start: Date, end: Date): StreamEvent[] {
    return this.events.filter(e => 
      e.timestamp >= start && e.timestamp <= end
    );
  }
}

export class StreamHealthMonitor {
  private analytics: StreamAnalytics;
  private alerts: Array<{ condition: string; threshold: number; callback: Function }> = [];

  constructor(analytics: StreamAnalytics) {
    this.analytics = analytics;
    this.setupDefaultAlerts();
    this.startMonitoring();
  }

  private setupDefaultAlerts(): void {
    this.addAlert('high_error_rate', 0.05, () => {
      console.warn('High error rate detected in stream processing');
    });

    this.addAlert('low_throughput', 10, () => {
      console.warn('Low throughput detected in stream processing');
    });

    this.addAlert('high_latency', 5000, () => {
      console.warn('High latency detected in stream processing');
    });
  }

  addAlert(condition: string, threshold: number, callback: Function): void {
    this.alerts.push({ condition, threshold, callback });
  }

  private startMonitoring(): void {
    setInterval(() => {
      this.checkAlerts();
    }, 30000); // Check every 30 seconds
  }

  private checkAlerts(): void {
    const metrics = this.analytics.getMetrics();

    this.alerts.forEach(alert => {
      let value: number;
      
      switch (alert.condition) {
        case 'high_error_rate':
          value = metrics.errorRate;
          if (value > alert.threshold) alert.callback();
          break;
        case 'low_throughput':
          value = metrics.eventsPerSecond;
          if (value < alert.threshold) alert.callback();
          break;
        case 'high_latency':
          value = metrics.latency.p95;
          if (value > alert.threshold) alert.callback();
          break;
      }
    });
  }

  getHealthStatus(): { status: string; issues: string[] } {
    const metrics = this.analytics.getMetrics();
    const issues: string[] = [];

    if (metrics.errorRate > 0.05) {
      issues.push('High error rate');
    }
    if (metrics.eventsPerSecond < 1) {
      issues.push('Low throughput');
    }
    if (metrics.latency.p95 > 5000) {
      issues.push('High latency');
    }

    return {
      status: issues.length === 0 ? 'healthy' : 'degraded',
      issues
    };
  }
}