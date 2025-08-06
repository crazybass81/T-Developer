export interface RoutingMetrics {
  totalRequests: number;
  routingLatency: number[];
  agentUtilization: Map<string, number>;
  queueDepth: number;
  errorRate: number;
  timestamp: number;
}

export interface Alert {
  type: string;
  message: string;
  data: any;
  timestamp: number;
}

export class RoutingMonitor {
  private metrics: RoutingMetrics;
  private metricsHistory: RoutingMetrics[] = [];
  private latencyBuffer: number[] = [];
  private requestCount = 0;
  private errorCount = 0;
  private agentStats = new Map<string, { requests: number; errors: number; totalTime: number }>();
  private queueSize = 0;
  private alerts: Alert[] = [];

  constructor() {
    this.metrics = this.createEmptyMetrics();
    this.startMetricsCollection();
  }

  private createEmptyMetrics(): RoutingMetrics {
    return {
      totalRequests: 0,
      routingLatency: [],
      agentUtilization: new Map(),
      queueDepth: 0,
      errorRate: 0,
      timestamp: Date.now()
    };
  }

  recordRequest(agentId: string, latency: number, success: boolean): void {
    this.requestCount++;
    this.latencyBuffer.push(latency);
    
    if (!this.agentStats.has(agentId)) {
      this.agentStats.set(agentId, { requests: 0, errors: 0, totalTime: 0 });
    }
    
    const stats = this.agentStats.get(agentId)!;
    stats.requests++;
    stats.totalTime += latency;
    
    if (!success) {
      this.errorCount++;
      stats.errors++;
    }

    // 버퍼 크기 제한 (최근 1000개)
    if (this.latencyBuffer.length > 1000) {
      this.latencyBuffer = this.latencyBuffer.slice(-1000);
    }
  }

  updateQueueDepth(depth: number): void {
    this.queueSize = depth;
  }

  async collectMetrics(): Promise<RoutingMetrics> {
    this.metrics = {
      totalRequests: this.requestCount,
      routingLatency: this.calculateLatencyPercentiles(),
      agentUtilization: this.calculateAgentUtilization(),
      queueDepth: this.queueSize,
      errorRate: this.requestCount > 0 ? this.errorCount / this.requestCount : 0,
      timestamp: Date.now()
    };

    // 히스토리 저장 (최근 100개)
    this.metricsHistory.push(this.metrics);
    if (this.metricsHistory.length > 100) {
      this.metricsHistory = this.metricsHistory.slice(-100);
    }

    // CloudWatch에 메트릭 전송
    await this.publishToCloudWatch(this.metrics);

    // 이상 감지
    await this.detectAnomalies(this.metrics);

    return this.metrics;
  }

  private calculateLatencyPercentiles(): number[] {
    if (this.latencyBuffer.length === 0) return [];

    const sorted = [...this.latencyBuffer].sort((a, b) => a - b);
    const percentiles = [];

    for (let p = 0; p <= 100; p++) {
      const index = Math.ceil((p / 100) * sorted.length) - 1;
      percentiles[p] = sorted[Math.max(0, index)] || 0;
    }

    return percentiles;
  }

  private calculateAgentUtilization(): Map<string, number> {
    const utilization = new Map<string, number>();

    for (const [agentId, stats] of this.agentStats) {
      const avgResponseTime = stats.requests > 0 ? stats.totalTime / stats.requests : 0;
      const errorRate = stats.requests > 0 ? stats.errors / stats.requests : 0;
      
      // 활용률 = (1 - 에러율) * 응답시간 가중치
      const timeWeight = Math.max(0, 1 - (avgResponseTime / 1000)); // 1초 기준
      utilization.set(agentId, (1 - errorRate) * timeWeight);
    }

    return utilization;
  }

  private async publishToCloudWatch(metrics: RoutingMetrics): Promise<void> {
    // CloudWatch 메트릭 전송 (실제 구현에서는 AWS SDK 사용)
    const cloudWatchMetrics = {
      Namespace: 'T-Developer/Routing',
      MetricData: [
        {
          MetricName: 'TotalRequests',
          Value: metrics.totalRequests,
          Unit: 'Count',
          Timestamp: new Date(metrics.timestamp)
        },
        {
          MetricName: 'ErrorRate',
          Value: metrics.errorRate * 100,
          Unit: 'Percent',
          Timestamp: new Date(metrics.timestamp)
        },
        {
          MetricName: 'QueueDepth',
          Value: metrics.queueDepth,
          Unit: 'Count',
          Timestamp: new Date(metrics.timestamp)
        }
      ]
    };

    if (metrics.routingLatency.length > 0) {
      cloudWatchMetrics.MetricData.push(
        {
          MetricName: 'RoutingLatencyP50',
          Value: metrics.routingLatency[50] || 0,
          Unit: 'Milliseconds',
          Timestamp: new Date(metrics.timestamp)
        },
        {
          MetricName: 'RoutingLatencyP99',
          Value: metrics.routingLatency[99] || 0,
          Unit: 'Milliseconds',
          Timestamp: new Date(metrics.timestamp)
        }
      );
    }

    // 실제 CloudWatch 전송은 여기서 구현
    console.log('📊 CloudWatch 메트릭 전송:', cloudWatchMetrics);
  }

  private async detectAnomalies(metrics: RoutingMetrics): Promise<void> {
    const alerts: Alert[] = [];

    // 지연 시간 이상 감지
    if (metrics.routingLatency.length > 0) {
      const p99Latency = metrics.routingLatency[99];
      if (p99Latency > 1000) { // 1초 초과
        alerts.push({
          type: 'HIGH_LATENCY',
          message: 'High routing latency detected',
          data: { p99Latency, threshold: 1000 },
          timestamp: Date.now()
        });
      }
    }

    // 에러율 이상 감지
    if (metrics.errorRate > 0.05) { // 5% 초과
      alerts.push({
        type: 'HIGH_ERROR_RATE',
        message: 'High error rate in routing',
        data: { errorRate: metrics.errorRate, threshold: 0.05 },
        timestamp: Date.now()
      });
    }

    // 큐 깊이 이상 감지
    if (metrics.queueDepth > 100) {
      alerts.push({
        type: 'HIGH_QUEUE_DEPTH',
        message: 'High queue depth detected',
        data: { queueDepth: metrics.queueDepth, threshold: 100 },
        timestamp: Date.now()
      });
    }

    // 에이전트 활용률 이상 감지
    for (const [agentId, utilization] of metrics.agentUtilization) {
      if (utilization < 0.3) { // 30% 미만
        alerts.push({
          type: 'LOW_AGENT_UTILIZATION',
          message: `Low utilization for agent ${agentId}`,
          data: { agentId, utilization, threshold: 0.3 },
          timestamp: Date.now()
        });
      }
    }

    // 알림 처리
    for (const alert of alerts) {
      await this.alert(alert);
    }
  }

  private async alert(alert: Alert): Promise<void> {
    this.alerts.push(alert);
    
    // 최근 50개 알림만 유지
    if (this.alerts.length > 50) {
      this.alerts = this.alerts.slice(-50);
    }

    console.warn(`🚨 ${alert.type}: ${alert.message}`, alert.data);

    // 실제 구현에서는 SNS, Slack 등으로 알림 전송
  }

  private startMetricsCollection(): void {
    // 30초마다 메트릭 수집
    setInterval(async () => {
      await this.collectMetrics();
    }, 30000);
  }

  getMetrics(): RoutingMetrics {
    return { ...this.metrics };
  }

  getMetricsHistory(): RoutingMetrics[] {
    return [...this.metricsHistory];
  }

  getAlerts(): Alert[] {
    return [...this.alerts];
  }

  getAgentStats() {
    const stats: any = {};
    for (const [agentId, data] of this.agentStats) {
      stats[agentId] = {
        requests: data.requests,
        errors: data.errors,
        avgResponseTime: data.requests > 0 ? data.totalTime / data.requests : 0,
        errorRate: data.requests > 0 ? data.errors / data.requests : 0
      };
    }
    return stats;
  }

  reset(): void {
    this.requestCount = 0;
    this.errorCount = 0;
    this.latencyBuffer = [];
    this.agentStats.clear();
    this.queueSize = 0;
    this.alerts = [];
    this.metricsHistory = [];
    this.metrics = this.createEmptyMetrics();
  }
}