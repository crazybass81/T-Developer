import { EventEmitter } from 'events';

interface SessionEvent {
  sessionId: string;
  userId: string;
  event: 'created' | 'activity' | 'expired' | 'terminated';
  timestamp: Date;
  metadata?: Record<string, any>;
}

export class SessionTracker extends EventEmitter {
  private activeSessions: Map<string, any> = new Map();
  private sessionMetrics: Map<string, any> = new Map();

  trackSession(sessionId: string, userId: string): void {
    this.activeSessions.set(sessionId, {
      userId,
      startTime: Date.now(),
      lastActivity: Date.now(),
      activityCount: 0
    });

    this.emit('session:created', { sessionId, userId, timestamp: new Date() });
  }

  updateActivity(sessionId: string): void {
    const session = this.activeSessions.get(sessionId);
    if (session) {
      session.lastActivity = Date.now();
      session.activityCount++;
      
      this.emit('session:activity', { 
        sessionId, 
        userId: session.userId, 
        timestamp: new Date() 
      });
    }
  }

  expireSession(sessionId: string): void {
    const session = this.activeSessions.get(sessionId);
    if (session) {
      this.activeSessions.delete(sessionId);
      this.emit('session:expired', { 
        sessionId, 
        userId: session.userId, 
        timestamp: new Date() 
      });
    }
  }

  getActiveSessionCount(): number {
    return this.activeSessions.size;
  }

  getSessionMetrics(): any {
    return {
      activeSessions: this.activeSessions.size,
      totalSessions: this.sessionMetrics.size,
      averageSessionDuration: this.calculateAverageSessionDuration()
    };
  }

  private calculateAverageSessionDuration(): number {
    const sessions = Array.from(this.activeSessions.values());
    if (sessions.length === 0) return 0;
    
    const totalDuration = sessions.reduce((sum, session) => {
      return sum + (Date.now() - session.startTime);
    }, 0);
    
    return totalDuration / sessions.length;
  }
}