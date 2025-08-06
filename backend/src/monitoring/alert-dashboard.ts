import { Request, Response } from 'express';
import { alertManager } from './alerting';
import { escalationManager } from './escalation';

export class AlertDashboard {
  
  // 알림 대시보드 데이터 조회
  async getDashboardData(req: Request, res: Response): Promise<void> {
    try {
      const limit = parseInt(req.query.limit as string) || 50;
      const recentAlerts = alertManager.getRecentAlerts(limit);
      
      // 알림 통계 계산
      const stats = this.calculateAlertStats(recentAlerts);
      
      // 에스컬레이션 규칙 및 히스토리
      const escalationRules = escalationManager.getRules();
      const escalationHistory = escalationManager.getEscalationHistory();
      
      res.json({
        alerts: recentAlerts,
        statistics: stats,
        escalation: {
          rules: escalationRules,
          history: escalationHistory
        },
        timestamp: new Date().toISOString()
      });
    } catch (error) {
      res.status(500).json({
        error: 'Failed to fetch dashboard data',
        message: error.message
      });
    }
  }
  
  // 알림 통계 계산
  private calculateAlertStats(alerts: any[]) {
    const now = new Date();
    const oneHourAgo = new Date(now.getTime() - 60 * 60 * 1000);
    const oneDayAgo = new Date(now.getTime() - 24 * 60 * 60 * 1000);
    
    const recentAlerts = alerts.filter(a => new Date(a.timestamp) >= oneHourAgo);
    const dailyAlerts = alerts.filter(a => new Date(a.timestamp) >= oneDayAgo);
    
    // 레벨별 통계
    const levelStats = alerts.reduce((acc, alert) => {
      acc[alert.level] = (acc[alert.level] || 0) + 1;
      return acc;
    }, {});
    
    // 타입별 통계
    const typeStats = alerts.reduce((acc, alert) => {
      acc[alert.type] = (acc[alert.type] || 0) + 1;
      return acc;
    }, {});
    
    return {
      total: alerts.length,
      lastHour: recentAlerts.length,
      lastDay: dailyAlerts.length,
      byLevel: levelStats,
      byType: typeStats,
      criticalCount: alerts.filter(a => a.level === 'critical' || a.level === 'emergency').length
    };
  }
  
  // 수동 알림 전송
  async sendManualAlert(req: Request, res: Response): Promise<void> {
    try {
      const { level, type, title, message, metadata } = req.body;
      
      if (!level || !type || !title || !message) {
        return res.status(400).json({
          error: 'Missing required fields',
          required: ['level', 'type', 'title', 'message']
        });
      }
      
      await alertManager.sendAlert({
        level,
        type,
        title,
        message,
        metadata
      });
      
      res.json({
        success: true,
        message: 'Alert sent successfully'
      });
    } catch (error) {
      res.status(500).json({
        error: 'Failed to send alert',
        message: error.message
      });
    }
  }
  
  // 알림 히스토리 정리
  async clearAlertHistory(req: Request, res: Response): Promise<void> {
    try {
      alertManager.clearAlertHistory();
      
      res.json({
        success: true,
        message: 'Alert history cleared'
      });
    } catch (error) {
      res.status(500).json({
        error: 'Failed to clear alert history',
        message: error.message
      });
    }
  }
}

export const alertDashboard = new AlertDashboard();