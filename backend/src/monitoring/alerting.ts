import { logger } from '../config/logger';
import { apmService } from './apm';

interface Alert {
  level: 'warning' | 'critical';
  type: string;
  message: string;
  value: number;
  timestamp: Date;
}

export class AlertManager {
  private alerts: Alert[] = [];
  private maxAlerts = 100;
  
  constructor() {
    this.setupAlertHandlers();
  }
  
  private setupAlertHandlers(): void {
    apmService.on('alert', (alert) => {
      this.handleAlert({
        ...alert,
        timestamp: new Date()
      });
    });
  }
  
  private handleAlert(alert: Alert): void {
    this.alerts.unshift(alert);
    
    if (this.alerts.length > this.maxAlerts) {
      this.alerts = this.alerts.slice(0, this.maxAlerts);
    }
    
    if (alert.level === 'critical') {
      logger.error(`CRITICAL ALERT: ${alert.message}`, {
        type: alert.type,
        value: alert.value,
        timestamp: alert.timestamp
      });
    } else {
      logger.warn(`WARNING ALERT: ${alert.message}`, {
        type: alert.type,
        value: alert.value,
        timestamp: alert.timestamp
      });
    }
  }
  
  getRecentAlerts(limit: number = 20): Alert[] {
    return this.alerts.slice(0, limit);
  }
  
  getCriticalAlerts(): Alert[] {
    return this.alerts.filter(alert => alert.level === 'critical');
  }
}

export const alertManager = new AlertManager();