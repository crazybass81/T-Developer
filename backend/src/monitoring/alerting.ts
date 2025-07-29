import { logger } from '../config/logger';
import { apmService } from './apm';

interface Alert {
  id: string;
  level: 'info' | 'warning' | 'critical' | 'emergency';
  type: string;
  title: string;
  message: string;
  metadata?: Record<string, any>;
  timestamp: Date;
}

interface AlertChannel {
  send(alert: Alert): Promise<void>;
}

class ConsoleAlertChannel implements AlertChannel {
  async send(alert: Alert): Promise<void> {
    const levelColors = {
      info: '\x1b[36m',
      warning: '\x1b[33m',
      critical: '\x1b[31m',
      emergency: '\x1b[41m'
    };
    
    console.log(`${levelColors[alert.level]}[${alert.level.toUpperCase()}] ${alert.title}\x1b[0m`);
    console.log(`Type: ${alert.type}`);
    console.log(`Message: ${alert.message}`);
    console.log(`Time: ${alert.timestamp.toISOString()}`);
    if (alert.metadata) {
      console.log('Metadata:', JSON.stringify(alert.metadata, null, 2));
    }
    console.log('---');
  }
}

export class AlertManager {
  private channels: Map<string, AlertChannel> = new Map();
  private alertHistory: Alert[] = [];
  private alertCooldowns: Map<string, number> = new Map();
  private maxAlerts = 100;
  
  constructor() {
    this.initializeChannels();
    this.setupAlertHandlers();
  }
  
  private initializeChannels(): void {
    this.channels.set('console', new ConsoleAlertChannel());
  }
  
  private setupAlertHandlers(): void {
    apmService.on('alert', (alert) => {
      this.sendAlert({
        level: alert.level as Alert['level'],
        type: alert.type,
        title: `Performance Alert: ${alert.type}`,
        message: alert.message,
        metadata: { value: alert.value }
      });
    });
  }
  
  async sendAlert(alert: Omit<Alert, 'id' | 'timestamp'>): Promise<void> {
    const fullAlert: Alert = {
      ...alert,
      id: `alert_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      timestamp: new Date()
    };
    
    const cooldownKey = `${alert.type}:${alert.level}`;
    const lastAlert = this.alertCooldowns.get(cooldownKey);
    
    if (lastAlert && Date.now() - lastAlert < 300000) {
      logger.debug('Alert suppressed due to cooldown', { cooldownKey });
      return;
    }
    
    this.alertHistory.unshift(fullAlert);
    if (this.alertHistory.length > this.maxAlerts) {
      this.alertHistory = this.alertHistory.slice(0, this.maxAlerts);
    }
    
    this.alertCooldowns.set(cooldownKey, Date.now());
    
    logger.warn('Alert triggered', fullAlert);
    
    const channelsToUse = this.selectChannels(fullAlert.level);
    
    const sendPromises = channelsToUse.map(channelName => {
      const channel = this.channels.get(channelName);
      if (channel) {
        return channel.send(fullAlert).catch(error => {
          logger.error(`Failed to send alert via ${channelName}`, error);
        });
      }
    });
    
    await Promise.all(sendPromises);
  }
  
  private selectChannels(level: Alert['level']): string[] {
    switch (level) {
      case 'info':
        return ['console'];
      case 'warning':
        return ['console'];
      case 'critical':
        return ['console'];
      case 'emergency':
        return ['console'];
      default:
        return ['console'];
    }
  }
  
  getRecentAlerts(limit: number = 20): Alert[] {
    return this.alertHistory.slice(0, limit);
  }
  
  getCriticalAlerts(): Alert[] {
    return this.alertHistory.filter(alert => alert.level === 'critical' || alert.level === 'emergency');
  }
  
  clearAlertHistory(): void {
    this.alertHistory = [];
    this.alertCooldowns.clear();
  }
}

export const alertManager = new AlertManager();

export const alertTemplates = {
  highCPU: (usage: number) => ({
    level: usage > 90 ? 'critical' as const : 'warning' as const,
    type: 'performance',
    title: 'High CPU Usage Detected',
    message: `CPU usage is at ${usage}%. This may impact system performance.`,
    metadata: { cpuUsage: usage }
  }),
  
  highMemory: (usage: number) => ({
    level: usage > 95 ? 'critical' as const : 'warning' as const,
    type: 'performance',
    title: 'High Memory Usage Detected',
    message: `Memory usage is at ${usage}%. Consider scaling or optimizing memory usage.`,
    metadata: { memoryUsage: usage }
  }),
  
  agentFailure: (agentName: string, error: string) => ({
    level: 'critical' as const,
    type: 'agent',
    title: `Agent Failure: ${agentName}`,
    message: `Agent ${agentName} has failed with error: ${error}`,
    metadata: { agentName, error }
  })
};