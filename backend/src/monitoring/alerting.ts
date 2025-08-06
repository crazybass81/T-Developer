import nodemailer from 'nodemailer';
import { WebClient } from '@slack/web-api';
import twilio from 'twilio';
import { logger } from '../utils/monitoring';

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

class EmailAlertChannel implements AlertChannel {
  private transporter: nodemailer.Transporter;
  
  constructor() {
    this.transporter = nodemailer.createTransporter({
      host: process.env.SMTP_HOST,
      port: parseInt(process.env.SMTP_PORT || '587'),
      secure: process.env.SMTP_SECURE === 'true',
      auth: {
        user: process.env.SMTP_USER,
        pass: process.env.SMTP_PASS
      }
    });
  }
  
  async send(alert: Alert): Promise<void> {
    const levelColors = {
      info: '#0066cc',
      warning: '#ff9900', 
      critical: '#ff0000',
      emergency: '#660000'
    };
    
    await this.transporter.sendMail({
      from: process.env.ALERT_FROM_EMAIL,
      to: process.env.ALERT_TO_EMAILS?.split(','),
      subject: `[${alert.level.toUpperCase()}] T-Developer: ${alert.title}`,
      html: `
        <div style="font-family: Arial, sans-serif; max-width: 600px;">
          <div style="background-color: ${levelColors[alert.level]}; color: white; padding: 20px;">
            <h2 style="margin: 0;">T-Developer Alert: ${alert.title}</h2>
          </div>
          <div style="padding: 20px; background-color: #f5f5f5;">
            <p><strong>Level:</strong> ${alert.level.toUpperCase()}</p>
            <p><strong>Type:</strong> ${alert.type}</p>
            <p><strong>Time:</strong> ${alert.timestamp.toISOString()}</p>
            <p><strong>Message:</strong></p>
            <p style="background-color: white; padding: 15px; border-left: 4px solid ${levelColors[alert.level]};">
              ${alert.message}
            </p>
          </div>
        </div>
      `
    });
  }
}

class SlackAlertChannel implements AlertChannel {
  private client: WebClient;
  private channel: string;
  
  constructor() {
    this.client = new WebClient(process.env.SLACK_BOT_TOKEN);
    this.channel = process.env.SLACK_ALERT_CHANNEL || '#alerts';
  }
  
  async send(alert: Alert): Promise<void> {
    const levelEmojis = {
      info: ':information_source:',
      warning: ':warning:',
      critical: ':rotating_light:',
      emergency: ':fire:'
    };
    
    await this.client.chat.postMessage({
      channel: this.channel,
      attachments: [{
        color: alert.level === 'critical' || alert.level === 'emergency' ? '#ff0000' : '#ff9900',
        title: `${levelEmojis[alert.level]} ${alert.title}`,
        text: alert.message,
        fields: [
          { title: 'Level', value: alert.level.toUpperCase(), short: true },
          { title: 'Type', value: alert.type, short: true }
        ],
        footer: 'T-Developer Monitoring',
        ts: Math.floor(alert.timestamp.getTime() / 1000).toString()
      }]
    });
  }
}

class SMSAlertChannel implements AlertChannel {
  private client: twilio.Twilio;
  
  constructor() {
    this.client = twilio(
      process.env.TWILIO_ACCOUNT_SID,
      process.env.TWILIO_AUTH_TOKEN
    );
  }
  
  async send(alert: Alert): Promise<void> {
    if (alert.level !== 'critical' && alert.level !== 'emergency') return;
    
    const recipients = process.env.SMS_ALERT_NUMBERS?.split(',') || [];
    
    for (const to of recipients) {
      await this.client.messages.create({
        body: `T-Developer ${alert.level.toUpperCase()}: ${alert.title}\n${alert.message}`,
        from: process.env.TWILIO_PHONE_NUMBER,
        to
      });
    }
  }
}

export class AlertManager {
  private channels: Map<string, AlertChannel> = new Map();
  private alertHistory: Alert[] = [];
  private alertCooldowns: Map<string, number> = new Map();
  
  constructor() {
    this.initializeChannels();
  }
  
  private initializeChannels(): void {
    if (process.env.SMTP_HOST) {
      this.channels.set('email', new EmailAlertChannel());
    }
    
    if (process.env.SLACK_BOT_TOKEN) {
      this.channels.set('slack', new SlackAlertChannel());
    }
    
    if (process.env.TWILIO_ACCOUNT_SID) {
      this.channels.set('sms', new SMSAlertChannel());
    }
  }
  
  async sendAlert(alert: Omit<Alert, 'id' | 'timestamp'>): Promise<void> {
    const fullAlert: Alert = {
      ...alert,
      id: `alert_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      timestamp: new Date()
    };
    
    // 중복 알림 방지 (5분 쿨다운)
    const cooldownKey = `${alert.type}:${alert.level}`;
    const lastAlert = this.alertCooldowns.get(cooldownKey);
    
    if (lastAlert && Date.now() - lastAlert < 300000) {
      logger.debug('Alert suppressed due to cooldown', { cooldownKey });
      return;
    }
    
    this.alertHistory.push(fullAlert);
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
      case 'info': return ['slack'];
      case 'warning': return ['slack', 'email'];
      case 'critical': return ['slack', 'email', 'sms'];
      case 'emergency': return ['slack', 'email', 'sms'];
      default: return ['slack'];
    }
  }
  
  getRecentAlerts(limit: number = 50): Alert[] {
    return this.alertHistory
      .slice(-limit)
      .sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime());
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