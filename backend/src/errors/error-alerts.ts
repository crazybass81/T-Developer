// Task 1.16.4: 에러 알림 및 보고 시스템
export interface AlertRule {
  id: string;
  name: string;
  condition: (metrics: any) => boolean;
  severity: 'low' | 'medium' | 'high' | 'critical';
  channels: AlertChannel[];
  cooldown: number; // milliseconds
}

export interface AlertChannel {
  type: 'email' | 'slack' | 'webhook';
  config: any;
}

export class AlertManager {
  private rules: Map<string, AlertRule> = new Map();
  private lastAlerts: Map<string, number> = new Map();
  private channels: Map<string, AlertSender> = new Map();

  constructor() {
    this.initializeChannels();
    this.setupDefaultRules();
  }

  private initializeChannels(): void {
    this.channels.set('email', new EmailAlertSender());
    this.channels.set('slack', new SlackAlertSender());
    this.channels.set('webhook', new WebhookAlertSender());
  }

  private setupDefaultRules(): void {
    // Critical error rate rule
    this.addRule({
      id: 'critical-error-rate',
      name: 'Critical Error Rate',
      condition: (metrics) => metrics.errorRate > 50,
      severity: 'critical',
      channels: [
        { type: 'email', config: { recipients: ['admin@company.com'] } },
        { type: 'slack', config: { channel: '#alerts' } }
      ],
      cooldown: 300000 // 5분
    });

    // High error count rule
    this.addRule({
      id: 'high-error-count',
      name: 'High Error Count',
      condition: (metrics) => metrics.errorCount > 100,
      severity: 'high',
      channels: [
        { type: 'slack', config: { channel: '#monitoring' } }
      ],
      cooldown: 600000 // 10분
    });
  }

  addRule(rule: AlertRule): void {
    this.rules.set(rule.id, rule);
  }

  async checkAlerts(metrics: any): Promise<void> {
    for (const [ruleId, rule] of this.rules) {
      if (this.shouldSkipDueToCooldown(ruleId, rule.cooldown)) {
        continue;
      }

      if (rule.condition(metrics)) {
        await this.sendAlert(rule, metrics);
        this.lastAlerts.set(ruleId, Date.now());
      }
    }
  }

  private shouldSkipDueToCooldown(ruleId: string, cooldown: number): boolean {
    const lastAlert = this.lastAlerts.get(ruleId);
    return lastAlert ? (Date.now() - lastAlert) < cooldown : false;
  }

  private async sendAlert(rule: AlertRule, metrics: any): Promise<void> {
    const alert: Alert = {
      id: this.generateAlertId(),
      ruleId: rule.id,
      ruleName: rule.name,
      severity: rule.severity,
      timestamp: new Date(),
      message: this.generateAlertMessage(rule, metrics),
      metrics
    };

    const promises = rule.channels.map(async (channel) => {
      const sender = this.channels.get(channel.type);
      if (sender) {
        try {
          await sender.send(alert, channel.config);
        } catch (error) {
          console.error(`Failed to send alert via ${channel.type}:`, error);
        }
      }
    });

    await Promise.all(promises);
  }

  private generateAlertMessage(rule: AlertRule, metrics: any): string {
    return `Alert: ${rule.name}\n` +
           `Severity: ${rule.severity}\n` +
           `Error Rate: ${metrics.errorRate}/sec\n` +
           `Error Count: ${metrics.errorCount}\n` +
           `Time: ${new Date().toISOString()}`;
  }

  private generateAlertId(): string {
    return `alert_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
}

interface Alert {
  id: string;
  ruleId: string;
  ruleName: string;
  severity: string;
  timestamp: Date;
  message: string;
  metrics: any;
}

abstract class AlertSender {
  abstract send(alert: Alert, config: any): Promise<void>;
}

class EmailAlertSender extends AlertSender {
  async send(alert: Alert, config: { recipients: string[] }): Promise<void> {
    // Mock email sending
    console.log(`Email alert sent to ${config.recipients.join(', ')}: ${alert.message}`);
  }
}

class SlackAlertSender extends AlertSender {
  async send(alert: Alert, config: { channel: string }): Promise<void> {
    // Mock Slack sending
    console.log(`Slack alert sent to ${config.channel}: ${alert.message}`);
  }
}

class WebhookAlertSender extends AlertSender {
  async send(alert: Alert, config: { url: string }): Promise<void> {
    // Mock webhook sending
    console.log(`Webhook alert sent to ${config.url}: ${alert.message}`);
  }
}

export class ErrorReporter {
  private alertManager: AlertManager;

  constructor(alertManager: AlertManager) {
    this.alertManager = alertManager;
  }

  async generateReport(timeRange: { start: Date; end: Date }): Promise<ErrorReport> {
    // Mock report generation
    return {
      timeRange,
      summary: {
        totalErrors: 150,
        errorRate: 2.5,
        topErrors: [
          { type: 'ValidationError', count: 45 },
          { type: 'DatabaseError', count: 32 }
        ]
      },
      trends: {
        hourlyDistribution: [],
        errorTypeDistribution: {}
      },
      recommendations: [
        'Increase validation on user inputs',
        'Review database connection pool settings'
      ]
    };
  }
}

interface ErrorReport {
  timeRange: { start: Date; end: Date };
  summary: {
    totalErrors: number;
    errorRate: number;
    topErrors: Array<{ type: string; count: number }>;
  };
  trends: {
    hourlyDistribution: number[];
    errorTypeDistribution: Record<string, number>;
  };
  recommendations: string[];
}