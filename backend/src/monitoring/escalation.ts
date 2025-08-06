import { alertManager, Alert } from './alerting';
import { logger } from '../config/logger';

interface EscalationRule {
  id: string;
  name: string;
  conditions: EscalationCondition[];
  actions: EscalationAction[];
  cooldownMinutes: number;
  enabled: boolean;
}

interface EscalationCondition {
  type: 'alert_count' | 'time_window' | 'alert_level' | 'alert_type';
  operator: 'equals' | 'greater_than' | 'less_than' | 'contains';
  value: any;
  timeWindowMinutes?: number;
}

interface EscalationAction {
  type: 'notify' | 'scale' | 'restart' | 'webhook';
  config: Record<string, any>;
}

export class EscalationManager {
  private rules: Map<string, EscalationRule> = new Map();
  private escalationHistory: Map<string, Date> = new Map();
  
  constructor() {
    this.initializeDefaultRules();
  }
  
  private initializeDefaultRules(): void {
    // 높은 CPU 사용률 에스컬레이션
    this.addRule({
      id: 'high-cpu-escalation',
      name: 'High CPU Usage Escalation',
      conditions: [
        {
          type: 'alert_count',
          operator: 'greater_than',
          value: 3,
          timeWindowMinutes: 15
        },
        {
          type: 'alert_type',
          operator: 'equals',
          value: 'performance'
        }
      ],
      actions: [
        {
          type: 'notify',
          config: {
            level: 'critical',
            channels: ['email', 'sms'],
            message: 'CPU usage has been consistently high for 15 minutes'
          }
        }
      ],
      cooldownMinutes: 60,
      enabled: true
    });
    
    // 에이전트 실패 에스컬레이션
    this.addRule({
      id: 'agent-failure-escalation',
      name: 'Agent Failure Escalation',
      conditions: [
        {
          type: 'alert_count',
          operator: 'greater_than',
          value: 2,
          timeWindowMinutes: 10
        },
        {
          type: 'alert_type',
          operator: 'equals',
          value: 'agent'
        }
      ],
      actions: [
        {
          type: 'notify',
          config: {
            level: 'emergency',
            channels: ['slack', 'email', 'sms'],
            message: 'Multiple agent failures detected - immediate attention required'
          }
        },
        {
          type: 'restart',
          config: {
            service: 'agent-orchestrator'
          }
        }
      ],
      cooldownMinutes: 30,
      enabled: true
    });
  }
  
  addRule(rule: EscalationRule): void {
    this.rules.set(rule.id, rule);
    logger.info('Escalation rule added', { ruleId: rule.id, ruleName: rule.name });
  }
  
  removeRule(ruleId: string): boolean {
    const removed = this.rules.delete(ruleId);
    if (removed) {
      logger.info('Escalation rule removed', { ruleId });
    }
    return removed;
  }
  
  async processAlert(alert: Alert): Promise<void> {
    for (const [ruleId, rule] of this.rules) {
      if (!rule.enabled) continue;
      
      // 쿨다운 확인
      const lastEscalation = this.escalationHistory.get(ruleId);
      if (lastEscalation) {
        const cooldownMs = rule.cooldownMinutes * 60 * 1000;
        if (Date.now() - lastEscalation.getTime() < cooldownMs) {
          continue;
        }
      }
      
      // 조건 확인
      const conditionsMet = await this.evaluateConditions(rule.conditions, alert);
      
      if (conditionsMet) {
        await this.executeActions(rule.actions, alert, rule);
        this.escalationHistory.set(ruleId, new Date());
        
        logger.warn('Escalation rule triggered', {
          ruleId,
          ruleName: rule.name,
          alertId: alert.id
        });
      }
    }
  }
  
  private async evaluateConditions(
    conditions: EscalationCondition[],
    currentAlert: Alert
  ): Promise<boolean> {
    for (const condition of conditions) {
      const result = await this.evaluateCondition(condition, currentAlert);
      if (!result) {
        return false; // 모든 조건이 만족되어야 함
      }
    }
    return true;
  }
  
  private async evaluateCondition(
    condition: EscalationCondition,
    currentAlert: Alert
  ): Promise<boolean> {
    switch (condition.type) {
      case 'alert_count':
        return this.evaluateAlertCount(condition, currentAlert);
      
      case 'alert_level':
        return this.evaluateAlertLevel(condition, currentAlert);
      
      case 'alert_type':
        return this.evaluateAlertType(condition, currentAlert);
      
      case 'time_window':
        return this.evaluateTimeWindow(condition, currentAlert);
      
      default:
        return false;
    }
  }
  
  private evaluateAlertCount(
    condition: EscalationCondition,
    currentAlert: Alert
  ): boolean {
    const timeWindowMs = (condition.timeWindowMinutes || 60) * 60 * 1000;
    const cutoffTime = new Date(Date.now() - timeWindowMs);
    
    const recentAlerts = alertManager.getRecentAlerts(100)
      .filter(alert => 
        alert.timestamp >= cutoffTime &&
        alert.type === currentAlert.type
      );
    
    switch (condition.operator) {
      case 'greater_than':
        return recentAlerts.length > condition.value;
      case 'equals':
        return recentAlerts.length === condition.value;
      case 'less_than':
        return recentAlerts.length < condition.value;
      default:
        return false;
    }
  }
  
  private evaluateAlertLevel(
    condition: EscalationCondition,
    currentAlert: Alert
  ): boolean {
    const levelPriority = {
      info: 1,
      warning: 2,
      critical: 3,
      emergency: 4
    };
    
    const currentPriority = levelPriority[currentAlert.level];
    const conditionPriority = levelPriority[condition.value as keyof typeof levelPriority];
    
    switch (condition.operator) {
      case 'equals':
        return currentPriority === conditionPriority;
      case 'greater_than':
        return currentPriority > conditionPriority;
      case 'less_than':
        return currentPriority < conditionPriority;
      default:
        return false;
    }
  }
  
  private evaluateAlertType(
    condition: EscalationCondition,
    currentAlert: Alert
  ): boolean {
    switch (condition.operator) {
      case 'equals':
        return currentAlert.type === condition.value;
      case 'contains':
        return currentAlert.type.includes(condition.value);
      default:
        return false;
    }
  }
  
  private evaluateTimeWindow(
    condition: EscalationCondition,
    currentAlert: Alert
  ): boolean {
    const timeWindowMs = (condition.timeWindowMinutes || 60) * 60 * 1000;
    const alertAge = Date.now() - currentAlert.timestamp.getTime();
    
    switch (condition.operator) {
      case 'greater_than':
        return alertAge > timeWindowMs;
      case 'less_than':
        return alertAge < timeWindowMs;
      default:
        return false;
    }
  }
  
  private async executeActions(
    actions: EscalationAction[],
    alert: Alert,
    rule: EscalationRule
  ): Promise<void> {
    for (const action of actions) {
      try {
        await this.executeAction(action, alert, rule);
      } catch (error) {
        logger.error('Failed to execute escalation action', {
          actionType: action.type,
          ruleId: rule.id,
          error: error.message
        });
      }
    }
  }
  
  private async executeAction(
    action: EscalationAction,
    alert: Alert,
    rule: EscalationRule
  ): Promise<void> {
    switch (action.type) {
      case 'notify':
        await this.executeNotifyAction(action, alert, rule);
        break;
      
      case 'webhook':
        await this.executeWebhookAction(action, alert, rule);
        break;
      
      case 'restart':
        await this.executeRestartAction(action, alert, rule);
        break;
      
      case 'scale':
        await this.executeScaleAction(action, alert, rule);
        break;
    }
  }
  
  private async executeNotifyAction(
    action: EscalationAction,
    alert: Alert,
    rule: EscalationRule
  ): Promise<void> {
    const escalationAlert = {
      level: action.config.level || 'critical',
      type: 'escalation',
      title: `Escalation: ${rule.name}`,
      message: action.config.message || `Rule "${rule.name}" has been triggered`,
      metadata: {
        originalAlert: alert,
        ruleId: rule.id,
        escalatedAt: new Date().toISOString()
      }
    };
    
    await alertManager.sendAlert(escalationAlert);
  }
  
  private async executeWebhookAction(
    action: EscalationAction,
    alert: Alert,
    rule: EscalationRule
  ): Promise<void> {
    const webhook = action.config.url;
    if (!webhook) return;
    
    const payload = {
      event: 'escalation',
      rule: rule.name,
      alert,
      timestamp: new Date().toISOString()
    };
    
    // Webhook 호출 구현 (실제 환경에서는 HTTP 클라이언트 사용)
    logger.info('Webhook escalation action executed', {
      webhook,
      ruleId: rule.id,
      alertId: alert.id
    });
  }
  
  private async executeRestartAction(
    action: EscalationAction,
    alert: Alert,
    rule: EscalationRule
  ): Promise<void> {
    const service = action.config.service;
    if (!service) return;
    
    // 서비스 재시작 로직 (실제 환경에서는 시스템 명령 실행)
    logger.warn('Service restart escalation action executed', {
      service,
      ruleId: rule.id,
      alertId: alert.id
    });
  }
  
  private async executeScaleAction(
    action: EscalationAction,
    alert: Alert,
    rule: EscalationRule
  ): Promise<void> {
    const scaleConfig = action.config;
    
    // 스케일링 로직 (실제 환경에서는 AWS Auto Scaling 등 사용)
    logger.info('Scale escalation action executed', {
      scaleConfig,
      ruleId: rule.id,
      alertId: alert.id
    });
  }
  
  getRules(): EscalationRule[] {
    return Array.from(this.rules.values());
  }
  
  getEscalationHistory(): Array<{ ruleId: string; lastTriggered: Date }> {
    return Array.from(this.escalationHistory.entries()).map(([ruleId, date]) => ({
      ruleId,
      lastTriggered: date
    }));
  }
}

export const escalationManager = new EscalationManager();