interface RoutingMetrics {
  totalRequests: number;
  routingLatency: number[];
  agentUtilization: Map<string, number>;
  queueDepth: number;
  errorRate: number;
}

interface TimeRange {
  start: Date;
  end: Date;
}

export class RoutingMonitor {
  private metrics: RoutingMetrics;
  private metricsHistory: RoutingMetrics[] = [];
  private latencyBuffer: number[] = [];
  
  constructor() {
    this.metrics = {
      totalRequests: 0,
      routingLatency: [],
      agentUtilization: new Map(),
      queueDepth: 0,
      errorRate: 0
    };
    
    this.startPeriodicCollection();
  }
  
  async collectMetrics(): Promise<void> {
    this.metrics = {
      totalRequests: await this.getTotalRequests(),
      routingLatency: await this.getLatencyPercentiles(),
      agentUtilization: await this.getAgentUtilization(),
      queueDepth: await this.getQueueDepth(),
      errorRate: await this.getErrorRate()
    };
    
    // CloudWatch에 메트릭 전송 (시뮬레이션)
    await this.publishToCloudWatch(this.metrics);
    
    // 이상 감지
    await this.detectAnomalies(this.metrics);
    
    // 히스토리에 저장
    this.metricsHistory.push({ ...this.metrics });
    
    // 히스토리 크기 제한 (최근 100개)
    if (this.metricsHistory.length > 100) {
      this.metricsHistory.shift();
    }
  }
  
  recordRoutingLatency(latency: number): void {
    this.latencyBuffer.push(latency);
    
    // 버퍼 크기 제한
    if (this.latencyBuffer.length > 1000) {
      this.latencyBuffer.shift();
    }
  }
  
  private async getTotalRequests(): Promise<number> {
    return this.metrics.totalRequests + 1;
  }
  
  private async getLatencyPercentiles(): Promise<number[]> {
    if (this.latencyBuffer.length === 0) return [0, 0, 0, 0, 0];
    
    const sorted = [...this.latencyBuffer].sort((a, b) => a - b);
    const len = sorted.length;
    
    return [
      sorted[Math.floor(len * 0.5)],  // P50
      sorted[Math.floor(len * 0.75)], // P75
      sorted[Math.floor(len * 0.9)],  // P90
      sorted[Math.floor(len * 0.95)], // P95
      sorted[Math.floor(len * 0.99)]  // P99
    ];
  }
  
  private async getAgentUtilization(): Promise<Map<string, number>> {
    const utilization = new Map<string, number>();
    
    // 시뮬레이션 데이터
    utilization.set('code-agent', Math.random() * 0.8);
    utilization.set('test-agent', Math.random() * 0.6);
    utilization.set('design-agent', Math.random() * 0.4);
    
    return utilization;
  }
  
  private async getQueueDepth(): Promise<number> {
    // 모든 큐의 깊이 합계
    return Math.floor(Math.random() * 10);
  }
  
  private async getErrorRate(): Promise<number> {
    // 에러율 계산 (0-1 사이)
    return Math.random() * 0.05; // 최대 5%
  }
  
  private async publishToCloudWatch(metrics: RoutingMetrics): Promise<void> {
    // CloudWatch 메트릭 전송 시뮬레이션
    console.log('📊 Publishing metrics to CloudWatch:', {
      totalRequests: metrics.totalRequests,
      p95Latency: metrics.routingLatency[3],
      errorRate: metrics.errorRate,
      queueDepth: metrics.queueDepth
    });
  }
  
  private async detectAnomalies(metrics: RoutingMetrics): Promise<void> {
    const alerts: string[] = [];
    
    // 지연 시간 이상
    const p99Latency = metrics.routingLatency[4];
    if (p99Latency > 1000) { // 1초 초과
      alerts.push(`High routing latency detected: P99=${p99Latency}ms`);
    }
    
    // 에러율 이상
    if (metrics.errorRate > 0.05) { // 5% 초과
      alerts.push(`High error rate in routing: ${(metrics.errorRate * 100).toFixed(2)}%`);
    }
    
    // 큐 깊이 이상
    if (metrics.queueDepth > 50) {
      alerts.push(`High queue depth: ${metrics.queueDepth} tasks`);
    }
    
    // 에이전트 과부하
    for (const [agent, utilization] of metrics.agentUtilization) {
      if (utilization > 0.9) {
        alerts.push(`Agent ${agent} overloaded: ${(utilization * 100).toFixed(1)}%`);
      }
    }
    
    if (alerts.length > 0) {
      await this.sendAlerts(alerts);
    }
  }
  
  private async sendAlerts(alerts: string[]): Promise<void> {
    console.warn('🚨 Routing Alerts:', alerts);
    
    // 실제 구현에서는 SNS, Slack 등으로 알림 전송
    alerts.forEach(alert => {
      console.warn(`ALERT: ${alert}`);
    });
  }
  
  private startPeriodicCollection(): void {
    // 30초마다 메트릭 수집
    setInterval(() => {
      this.collectMetrics().catch(console.error);
    }, 30000);
  }
  
  getMetricsSummary(): any {
    return {
      current: {
        totalRequests: this.metrics.totalRequests,
        p95Latency: this.metrics.routingLatency[3] || 0,
        errorRate: this.metrics.errorRate,
        queueDepth: this.metrics.queueDepth,
        agentUtilization: Object.fromEntries(this.metrics.agentUtilization)
      },
      trend: this.calculateTrend()
    };
  }
  
  private calculateTrend(): any {
    if (this.metricsHistory.length < 2) return null;
    
    const recent = this.metricsHistory.slice(-5); // 최근 5개
    const older = this.metricsHistory.slice(-10, -5); // 이전 5개
    
    if (older.length === 0) return null;
    
    const recentAvgLatency = recent.reduce((sum, m) => sum + (m.routingLatency[3] || 0), 0) / recent.length;
    const olderAvgLatency = older.reduce((sum, m) => sum + (m.routingLatency[3] || 0), 0) / older.length;
    
    return {
      latencyTrend: recentAvgLatency > olderAvgLatency ? 'increasing' : 'decreasing',
      latencyChange: ((recentAvgLatency - olderAvgLatency) / olderAvgLatency * 100).toFixed(1) + '%'
    };
  }
}