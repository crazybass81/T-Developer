// backend/src/bedrock/scaling-manager.ts
export interface ScalingMetrics {
  requestsPerMinute: number;
  averageResponseTime: number;
  errorRate: number;
  activeRuntimes: number;
}

export interface ScalingConfig {
  minRuntimes: number;
  maxRuntimes: number;
  targetUtilization: number;
  scaleUpThreshold: number;
  scaleDownThreshold: number;
}

export class ScalingManager {
  private config: ScalingConfig;
  private metrics: ScalingMetrics[] = [];
  private lastScaleAction: Date = new Date();

  constructor(config: ScalingConfig) {
    this.config = config;
  }

  recordMetrics(metrics: ScalingMetrics): void {
    this.metrics.push({
      ...metrics,
      timestamp: Date.now()
    } as any);

    // Keep only last 10 minutes of metrics
    const tenMinutesAgo = Date.now() - 600000;
    this.metrics = this.metrics.filter((m: any) => m.timestamp > tenMinutesAgo);
  }

  shouldScale(): {
    action: 'scale_up' | 'scale_down' | 'none';
    reason: string;
    targetRuntimes?: number;
  } {
    if (this.metrics.length < 3) {
      return { action: 'none', reason: 'Insufficient metrics' };
    }

    const recentMetrics = this.metrics.slice(-3);
    const avgUtilization = recentMetrics.reduce((sum, m) => sum + m.requestsPerMinute, 0) / recentMetrics.length;
    const avgErrorRate = recentMetrics.reduce((sum, m) => sum + m.errorRate, 0) / recentMetrics.length;
    const currentRuntimes = recentMetrics[recentMetrics.length - 1].activeRuntimes;

    // Prevent rapid scaling
    const timeSinceLastScale = Date.now() - this.lastScaleAction.getTime();
    if (timeSinceLastScale < 300000) { // 5 minutes
      return { action: 'none', reason: 'Cooldown period' };
    }

    // Scale up conditions
    if (avgUtilization > this.config.scaleUpThreshold || avgErrorRate > 0.05) {
      if (currentRuntimes < this.config.maxRuntimes) {
        return {
          action: 'scale_up',
          reason: `High utilization: ${avgUtilization.toFixed(2)} RPM`,
          targetRuntimes: Math.min(currentRuntimes + 1, this.config.maxRuntimes)
        };
      }
    }

    // Scale down conditions
    if (avgUtilization < this.config.scaleDownThreshold && avgErrorRate < 0.01) {
      if (currentRuntimes > this.config.minRuntimes) {
        return {
          action: 'scale_down',
          reason: `Low utilization: ${avgUtilization.toFixed(2)} RPM`,
          targetRuntimes: Math.max(currentRuntimes - 1, this.config.minRuntimes)
        };
      }
    }

    return { action: 'none', reason: 'Within normal parameters' };
  }

  recordScaleAction(): void {
    this.lastScaleAction = new Date();
  }

  getRecommendations(): string[] {
    const recommendations: string[] = [];
    
    if (this.metrics.length === 0) {
      return ['No metrics available for recommendations'];
    }

    const latest = this.metrics[this.metrics.length - 1];
    
    if (latest.errorRate > 0.1) {
      recommendations.push('High error rate detected - check agent configuration');
    }
    
    if (latest.averageResponseTime > 5000) {
      recommendations.push('High response time - consider optimizing prompts');
    }
    
    if (latest.activeRuntimes === this.config.maxRuntimes) {
      recommendations.push('At maximum runtime capacity - consider increasing limits');
    }

    return recommendations.length > 0 ? recommendations : ['System operating normally'];
  }
}