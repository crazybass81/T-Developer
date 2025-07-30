// Task 1.15.4: 알림 시스템
import { SNSClient, PublishCommand } from '@aws-sdk/client-sns';

interface Alert {
  level: 'info' | 'warning' | 'critical';
  title: string;
  message: string;
  metadata?: any;
}

export class AlertManager {
  private snsClient: SNSClient;
  private topicArn: string;

  constructor(topicArn?: string) {
    this.snsClient = new SNSClient({ region: process.env.AWS_REGION });
    this.topicArn = topicArn || process.env.ALERT_TOPIC_ARN || '';
  }

  async sendAlert(alert: Alert): Promise<void> {
    const message = {
      level: alert.level,
      title: alert.title,
      message: alert.message,
      timestamp: new Date().toISOString(),
      service: 't-developer',
      environment: process.env.NODE_ENV,
      metadata: alert.metadata
    };

    // Console output for development
    if (process.env.NODE_ENV === 'development') {
      console.log(`🚨 [${alert.level.toUpperCase()}] ${alert.title}: ${alert.message}`);
      return;
    }

    // SNS for production
    if (this.topicArn) {
      try {
        await this.snsClient.send(new PublishCommand({
          TopicArn: this.topicArn,
          Subject: `T-Developer Alert: ${alert.title}`,
          Message: JSON.stringify(message, null, 2)
        }));
      } catch (error) {
        console.error('Failed to send alert:', error);
      }
    }
  }

  info(title: string, message: string, metadata?: any): Promise<void> {
    return this.sendAlert({ level: 'info', title, message, metadata });
  }

  warning(title: string, message: string, metadata?: any): Promise<void> {
    return this.sendAlert({ level: 'warning', title, message, metadata });
  }

  critical(title: string, message: string, metadata?: any): Promise<void> {
    return this.sendAlert({ level: 'critical', title, message, metadata });
  }
}

// Global alert manager
export const alertManager = new AlertManager();

// Auto-alerting based on health checks
export class HealthAlerter {
  private lastStatus: string = 'healthy';

  async checkAndAlert(healthStatus: any): Promise<void> {
    if (healthStatus.status !== this.lastStatus) {
      if (healthStatus.status === 'unhealthy') {
        await alertManager.critical(
          'System Unhealthy',
          'Multiple health checks are failing',
          { checks: healthStatus.checks }
        );
      } else if (healthStatus.status === 'degraded') {
        await alertManager.warning(
          'System Degraded',
          'Some health checks are failing',
          { checks: healthStatus.checks }
        );
      } else if (healthStatus.status === 'healthy' && this.lastStatus !== 'healthy') {
        await alertManager.info(
          'System Recovered',
          'All health checks are now passing'
        );
      }

      this.lastStatus = healthStatus.status;
    }
  }
}

export const healthAlerter = new HealthAlerter();