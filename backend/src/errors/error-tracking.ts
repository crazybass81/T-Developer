// Task 1.16.3: 에러 추적 및 분석
export interface ErrorMetrics {
  errorCount: number;
  errorRate: number;
  errorsByType: Record<string, number>;
  errorsByEndpoint: Record<string, number>;
  averageResponseTime: number;
  lastOccurrence: Date;
}

export class ErrorTracker {
  private errors: Map<string, ErrorEvent[]> = new Map();
  private readonly maxEvents = 1000;
  private readonly timeWindow = 3600000; // 1시간

  trackError(error: Error, context: any): void {
    const errorEvent: ErrorEvent = {
      id: this.generateId(),
      timestamp: new Date(),
      type: error.constructor.name,
      message: error.message,
      stack: error.stack,
      context,
      fingerprint: this.generateFingerprint(error)
    };

    const key = errorEvent.fingerprint;
    const events = this.errors.get(key) || [];
    events.push(errorEvent);

    // 시간 윈도우 내 이벤트만 유지
    const cutoff = Date.now() - this.timeWindow;
    const filtered = events.filter(e => e.timestamp.getTime() > cutoff);
    
    this.errors.set(key, filtered.slice(-this.maxEvents));
  }

  getMetrics(timeRange?: { start: Date; end: Date }): ErrorMetrics {
    const allEvents = Array.from(this.errors.values()).flat();
    const filteredEvents = timeRange 
      ? allEvents.filter(e => e.timestamp >= timeRange.start && e.timestamp <= timeRange.end)
      : allEvents;

    const errorsByType: Record<string, number> = {};
    const errorsByEndpoint: Record<string, number> = {};

    filteredEvents.forEach(event => {
      errorsByType[event.type] = (errorsByType[event.type] || 0) + 1;
      if (event.context?.endpoint) {
        errorsByEndpoint[event.context.endpoint] = (errorsByEndpoint[event.context.endpoint] || 0) + 1;
      }
    });

    return {
      errorCount: filteredEvents.length,
      errorRate: this.calculateErrorRate(filteredEvents),
      errorsByType,
      errorsByEndpoint,
      averageResponseTime: this.calculateAverageResponseTime(filteredEvents),
      lastOccurrence: filteredEvents.length > 0 
        ? new Date(Math.max(...filteredEvents.map(e => e.timestamp.getTime())))
        : new Date(0)
    };
  }

  getTopErrors(limit: number = 10): Array<{ fingerprint: string; count: number; lastSeen: Date }> {
    return Array.from(this.errors.entries())
      .map(([fingerprint, events]) => ({
        fingerprint,
        count: events.length,
        lastSeen: new Date(Math.max(...events.map(e => e.timestamp.getTime())))
      }))
      .sort((a, b) => b.count - a.count)
      .slice(0, limit);
  }

  private generateFingerprint(error: Error): string {
    const key = `${error.constructor.name}:${error.message}`;
    return Buffer.from(key).toString('base64').substring(0, 16);
  }

  private generateId(): string {
    return Date.now().toString(36) + Math.random().toString(36).substr(2);
  }

  private calculateErrorRate(events: ErrorEvent[]): number {
    if (events.length === 0) return 0;
    const timeSpan = Math.max(1, this.timeWindow / 1000); // seconds
    return events.length / timeSpan;
  }

  private calculateAverageResponseTime(events: ErrorEvent[]): number {
    const responseTimes = events
      .map(e => e.context?.responseTime)
      .filter(t => typeof t === 'number');
    
    return responseTimes.length > 0 
      ? responseTimes.reduce((sum, time) => sum + time, 0) / responseTimes.length
      : 0;
  }
}

interface ErrorEvent {
  id: string;
  timestamp: Date;
  type: string;
  message: string;
  stack?: string;
  context: any;
  fingerprint: string;
}

export class ErrorAnalyzer {
  private tracker: ErrorTracker;

  constructor(tracker: ErrorTracker) {
    this.tracker = tracker;
  }

  analyzePatterns(): ErrorPattern[] {
    const metrics = this.tracker.getMetrics();
    const patterns: ErrorPattern[] = [];

    // 스파이크 패턴 감지
    if (metrics.errorRate > 10) {
      patterns.push({
        type: 'spike',
        severity: 'high',
        description: `Error rate spike detected: ${metrics.errorRate.toFixed(2)} errors/sec`
      });
    }

    // 반복 에러 패턴
    const topErrors = this.tracker.getTopErrors(5);
    topErrors.forEach(error => {
      if (error.count > 50) {
        patterns.push({
          type: 'recurring',
          severity: 'medium',
          description: `Recurring error: ${error.fingerprint} (${error.count} occurrences)`
        });
      }
    });

    return patterns;
  }
}

interface ErrorPattern {
  type: 'spike' | 'recurring' | 'cascade';
  severity: 'low' | 'medium' | 'high';
  description: string;
}