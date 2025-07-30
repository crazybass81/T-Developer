// SubTask 1.20.3: Pipeline Monitoring
export interface PipelineMetrics {
  pipelineName: string;
  executionId: string;
  duration: number;
  success: boolean;
  timestamp: Date;
  stages: StageMetrics[];
}

export interface StageMetrics {
  name: string;
  duration: number;
  success: boolean;
  retries: number;
}

export class PipelineMonitor {
  private metrics: PipelineMetrics[] = [];
  private alerts: AlertRule[] = [];

  // Record pipeline execution
  recordExecution(metrics: PipelineMetrics): void {
    this.metrics.push(metrics);
    this.checkAlerts(metrics);
  }

  // Add alert rule
  addAlert(rule: AlertRule): void {
    this.alerts.push(rule);
  }

  // Check alerts
  private checkAlerts(metrics: PipelineMetrics): void {
    for (const rule of this.alerts) {
      if (this.evaluateRule(rule, metrics)) {
        this.triggerAlert(rule, metrics);
      }
    }
  }

  // Evaluate alert rule
  private evaluateRule(rule: AlertRule, metrics: PipelineMetrics): boolean {
    switch (rule.type) {
      case 'failure':
        return !metrics.success;
      case 'duration':
        return metrics.duration > rule.threshold;
      case 'success-rate':
        return this.getSuccessRate(metrics.pipelineName, rule.window || 60) < rule.threshold;
      default:
        return false;
    }
  }

  // Trigger alert
  private triggerAlert(rule: AlertRule, metrics: PipelineMetrics): void {
    const alert: Alert = {
      id: `alert_${Date.now()}`,
      rule: rule.name,
      message: rule.message,
      severity: rule.severity,
      pipeline: metrics.pipelineName,
      execution: metrics.executionId,
      timestamp: new Date()
    };

    console.log(`🚨 ALERT: ${alert.message}`);
    
    // Send notifications
    this.sendNotifications(alert, rule.notifications);
  }

  // Send notifications
  private async sendNotifications(alert: Alert, notifications: string[]): Promise<void> {
    for (const notification of notifications) {
      try {
        await this.sendNotification(notification, alert);
      } catch (error) {
        console.error(`Failed to send notification to ${notification}:`, error);
      }
    }
  }

  // Send single notification
  private async sendNotification(target: string, alert: Alert): Promise<void> {
    // Mock notification sending
    console.log(`📧 Notification sent to ${target}: ${alert.message}`);
  }

  // Get success rate
  private getSuccessRate(pipelineName: string, windowMinutes: number): number {
    const cutoff = new Date(Date.now() - windowMinutes * 60 * 1000);
    const recent = this.metrics.filter(m => 
      m.pipelineName === pipelineName && m.timestamp >= cutoff
    );
    
    if (recent.length === 0) return 1;
    
    const successful = recent.filter(m => m.success).length;
    return successful / recent.length;
  }

  // Get pipeline statistics
  getStats(pipelineName?: string): PipelineStats {
    const filtered = pipelineName 
      ? this.metrics.filter(m => m.pipelineName === pipelineName)
      : this.metrics;

    if (filtered.length === 0) {
      return {
        totalExecutions: 0,
        successRate: 0,
        averageDuration: 0,
        failureRate: 0
      };
    }

    const successful = filtered.filter(m => m.success).length;
    const totalDuration = filtered.reduce((sum, m) => sum + m.duration, 0);

    return {
      totalExecutions: filtered.length,
      successRate: successful / filtered.length,
      averageDuration: totalDuration / filtered.length,
      failureRate: (filtered.length - successful) / filtered.length,
      recentExecutions: filtered.slice(-10)
    };
  }

  // Get trending data
  getTrends(pipelineName: string, days: number = 7): TrendData {
    const cutoff = new Date(Date.now() - days * 24 * 60 * 60 * 1000);
    const recent = this.metrics.filter(m => 
      m.pipelineName === pipelineName && m.timestamp >= cutoff
    );

    // Group by day
    const dailyStats = new Map<string, DailyStats>();
    
    for (const metric of recent) {
      const day = metric.timestamp.toISOString().split('T')[0];
      
      if (!dailyStats.has(day)) {
        dailyStats.set(day, {
          date: day,
          executions: 0,
          successes: 0,
          totalDuration: 0
        });
      }
      
      const stats = dailyStats.get(day)!;
      stats.executions++;
      if (metric.success) stats.successes++;
      stats.totalDuration += metric.duration;
    }

    return {
      pipeline: pipelineName,
      period: days,
      daily: Array.from(dailyStats.values()).map(stats => ({
        date: stats.date,
        executions: stats.executions,
        successRate: stats.successes / stats.executions,
        averageDuration: stats.totalDuration / stats.executions
      }))
    };
  }

  // Health check
  getHealth(): HealthStatus {
    const recent = this.metrics.filter(m => 
      m.timestamp >= new Date(Date.now() - 60 * 60 * 1000) // Last hour
    );

    const failures = recent.filter(m => !m.success).length;
    const failureRate = recent.length > 0 ? failures / recent.length : 0;

    return {
      status: failureRate > 0.5 ? 'unhealthy' : failureRate > 0.2 ? 'degraded' : 'healthy',
      recentExecutions: recent.length,
      failureRate,
      lastExecution: recent.length > 0 ? recent[recent.length - 1].timestamp : null
    };
  }
}

export interface AlertRule {
  name: string;
  type: 'failure' | 'duration' | 'success-rate';
  threshold: number;
  window?: number; // minutes
  message: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  notifications: string[];
}

export interface Alert {
  id: string;
  rule: string;
  message: string;
  severity: string;
  pipeline: string;
  execution: string;
  timestamp: Date;
}

export interface PipelineStats {
  totalExecutions: number;
  successRate: number;
  averageDuration: number;
  failureRate: number;
  recentExecutions?: PipelineMetrics[];
}

export interface TrendData {
  pipeline: string;
  period: number;
  daily: DailyTrend[];
}

export interface DailyTrend {
  date: string;
  executions: number;
  successRate: number;
  averageDuration: number;
}

export interface DailyStats {
  date: string;
  executions: number;
  successes: number;
  totalDuration: number;
}

export interface HealthStatus {
  status: 'healthy' | 'degraded' | 'unhealthy';
  recentExecutions: number;
  failureRate: number;
  lastExecution: Date | null;
}