/**
 * T-Developer Session Management System
 * AWS Bedrock AgentCore 8시간 세션 관리
 */

import { EventEmitter } from 'events';
import { Logger } from '../utils/logger';
import { v4 as uuidv4 } from 'uuid';

export interface Session {
  id: string;
  userId: string;
  projectId: string;
  startTime: Date;
  lastActivity: Date;
  expiresAt: Date;
  status: 'active' | 'idle' | 'expired' | 'terminated';
  context: SessionContext;
  metadata: SessionMetadata;
}

export interface SessionContext {
  agentIds: string[];
  workflowId?: string;
  currentTask?: string;
  variables: Map<string, any>;
  history: SessionEvent[];
}

export interface SessionMetadata {
  ipAddress?: string;
  userAgent?: string;
  environment: 'development' | 'staging' | 'production';
  features: string[];
  permissions: string[];
}

export interface SessionEvent {
  id: string;
  timestamp: Date;
  type: 'created' | 'updated' | 'extended' | 'expired' | 'terminated';
  data?: any;
}

export interface SessionConfig {
  maxDuration: number;        // Maximum session duration (8 hours = 28800000 ms)
  idleTimeout: number;         // Idle timeout (30 minutes = 1800000 ms)
  warningThreshold: number;    // Warning before expiry (10 minutes = 600000 ms)
  maxConcurrentSessions: number;
  enableAutoExtend: boolean;
}

/**
 * Session Manager
 */
export class SessionManager extends EventEmitter {
  private logger: Logger;
  private sessions: Map<string, Session>;
  private userSessions: Map<string, Set<string>>;
  private config: SessionConfig;
  private cleanupInterval: NodeJS.Timeout | null;
  private readonly DEFAULT_CONFIG: SessionConfig = {
    maxDuration: 8 * 60 * 60 * 1000,  // 8 hours
    idleTimeout: 30 * 60 * 1000,      // 30 minutes
    warningThreshold: 10 * 60 * 1000,  // 10 minutes
    maxConcurrentSessions: 100,
    enableAutoExtend: true
  };
  
  constructor(config?: Partial<SessionConfig>) {
    super();
    this.logger = new Logger('SessionManager');
    this.sessions = new Map();
    this.userSessions = new Map();
    this.config = { ...this.DEFAULT_CONFIG, ...config };
    this.cleanupInterval = null;
    
    this.startCleanupProcess();
  }
  
  /**
   * Create a new session
   */
  async createSession(
    userId: string,
    projectId: string,
    metadata?: Partial<SessionMetadata>
  ): Promise<Session> {
    // Check concurrent session limit
    const userSessionCount = this.userSessions.get(userId)?.size || 0;
    if (userSessionCount >= this.config.maxConcurrentSessions) {
      throw new Error(`User ${userId} has reached maximum concurrent sessions`);
    }
    
    const now = new Date();
    const session: Session = {
      id: uuidv4(),
      userId,
      projectId,
      startTime: now,
      lastActivity: now,
      expiresAt: new Date(now.getTime() + this.config.maxDuration),
      status: 'active',
      context: {
        agentIds: [],
        variables: new Map(),
        history: []
      },
      metadata: {
        environment: 'development',
        features: [],
        permissions: [],
        ...metadata
      }
    };
    
    // Add creation event
    this.addSessionEvent(session, 'created');
    
    // Store session
    this.sessions.set(session.id, session);
    
    // Track user sessions
    if (!this.userSessions.has(userId)) {
      this.userSessions.set(userId, new Set());
    }
    this.userSessions.get(userId)!.add(session.id);
    
    this.logger.info(`Session created: ${session.id} for user ${userId}`);
    this.emit('session:created', session);
    
    // Schedule expiry warning
    this.scheduleExpiryWarning(session);
    
    return session;
  }
  
  /**
   * Get session by ID
   */
  getSession(sessionId: string): Session | null {
    const session = this.sessions.get(sessionId);
    
    if (!session) {
      return null;
    }
    
    // Check if expired
    if (this.isSessionExpired(session)) {
      this.expireSession(sessionId);
      return null;
    }
    
    return session;
  }
  
  /**
   * Update session activity
   */
  updateActivity(sessionId: string): boolean {
    const session = this.sessions.get(sessionId);
    
    if (!session || session.status !== 'active') {
      return false;
    }
    
    session.lastActivity = new Date();
    
    // Auto-extend if enabled and nearing expiry
    if (this.config.enableAutoExtend) {
      const timeRemaining = session.expiresAt.getTime() - Date.now();
      
      if (timeRemaining < this.config.warningThreshold) {
        this.extendSession(sessionId);
      }
    }
    
    return true;
  }
  
  /**
   * Extend session duration
   */
  extendSession(sessionId: string, duration?: number): boolean {
    const session = this.sessions.get(sessionId);
    
    if (!session || session.status !== 'active') {
      return false;
    }
    
    const extensionDuration = duration || this.config.maxDuration;
    const now = new Date();
    const newExpiry = new Date(now.getTime() + extensionDuration);
    
    // Check if within maximum allowed duration
    const totalDuration = newExpiry.getTime() - session.startTime.getTime();
    if (totalDuration > this.config.maxDuration * 2) {
      this.logger.warn(`Cannot extend session ${sessionId} beyond maximum duration`);
      return false;
    }
    
    session.expiresAt = newExpiry;
    session.lastActivity = now;
    
    this.addSessionEvent(session, 'extended', { newExpiry });
    
    this.logger.info(`Session ${sessionId} extended until ${newExpiry.toISOString()}`);
    this.emit('session:extended', session);
    
    // Reschedule expiry warning
    this.scheduleExpiryWarning(session);
    
    return true;
  }
  
  /**
   * Terminate session
   */
  terminateSession(sessionId: string, reason?: string): boolean {
    const session = this.sessions.get(sessionId);
    
    if (!session) {
      return false;
    }
    
    session.status = 'terminated';
    
    this.addSessionEvent(session, 'terminated', { reason });
    
    // Clean up user sessions
    const userSessions = this.userSessions.get(session.userId);
    if (userSessions) {
      userSessions.delete(sessionId);
      
      if (userSessions.size === 0) {
        this.userSessions.delete(session.userId);
      }
    }
    
    // Remove from active sessions
    this.sessions.delete(sessionId);
    
    this.logger.info(`Session ${sessionId} terminated${reason ? `: ${reason}` : ''}`);
    this.emit('session:terminated', session);
    
    return true;
  }
  
  /**
   * Get all sessions for a user
   */
  getUserSessions(userId: string): Session[] {
    const sessionIds = this.userSessions.get(userId);
    
    if (!sessionIds) {
      return [];
    }
    
    const sessions: Session[] = [];
    
    for (const sessionId of sessionIds) {
      const session = this.getSession(sessionId);
      if (session) {
        sessions.push(session);
      }
    }
    
    return sessions;
  }
  
  /**
   * Get active sessions count
   */
  getActiveSessionCount(): number {
    return Array.from(this.sessions.values())
      .filter(s => s.status === 'active').length;
  }
  
  /**
   * Get session statistics
   */
  getStatistics(): {
    totalSessions: number;
    activeSessions: number;
    idleSessions: number;
    expiredSessions: number;
    avgSessionDuration: number;
    userCount: number;
  } {
    const sessions = Array.from(this.sessions.values());
    const activeSessions = sessions.filter(s => s.status === 'active').length;
    const idleSessions = sessions.filter(s => s.status === 'idle').length;
    const expiredSessions = sessions.filter(s => s.status === 'expired').length;
    
    // Calculate average duration
    let totalDuration = 0;
    let completedSessions = 0;
    
    for (const session of sessions) {
      if (session.status === 'terminated' || session.status === 'expired') {
        const duration = session.lastActivity.getTime() - session.startTime.getTime();
        totalDuration += duration;
        completedSessions++;
      }
    }
    
    const avgSessionDuration = completedSessions > 0 
      ? totalDuration / completedSessions 
      : 0;
    
    return {
      totalSessions: sessions.length,
      activeSessions,
      idleSessions,
      expiredSessions,
      avgSessionDuration,
      userCount: this.userSessions.size
    };
  }
  
  /**
   * Update session context
   */
  updateSessionContext(
    sessionId: string,
    updates: Partial<SessionContext>
  ): boolean {
    const session = this.sessions.get(sessionId);
    
    if (!session || session.status !== 'active') {
      return false;
    }
    
    // Merge updates
    if (updates.agentIds) {
      session.context.agentIds = updates.agentIds;
    }
    
    if (updates.workflowId) {
      session.context.workflowId = updates.workflowId;
    }
    
    if (updates.currentTask) {
      session.context.currentTask = updates.currentTask;
    }
    
    if (updates.variables) {
      for (const [key, value] of updates.variables) {
        session.context.variables.set(key, value);
      }
    }
    
    this.updateActivity(sessionId);
    
    this.emit('session:context:updated', { sessionId, updates });
    
    return true;
  }
  
  /**
   * Get session variable
   */
  getSessionVariable(sessionId: string, key: string): any {
    const session = this.sessions.get(sessionId);
    
    if (!session) {
      return undefined;
    }
    
    return session.context.variables.get(key);
  }
  
  /**
   * Set session variable
   */
  setSessionVariable(sessionId: string, key: string, value: any): boolean {
    const session = this.sessions.get(sessionId);
    
    if (!session || session.status !== 'active') {
      return false;
    }
    
    session.context.variables.set(key, value);
    this.updateActivity(sessionId);
    
    return true;
  }
  
  /**
   * Clean up expired sessions
   */
  private cleanupExpiredSessions(): void {
    const now = Date.now();
    const sessionsToExpire: string[] = [];
    
    for (const [sessionId, session] of this.sessions) {
      // Check for expiry
      if (session.expiresAt.getTime() <= now) {
        sessionsToExpire.push(sessionId);
        continue;
      }
      
      // Check for idle timeout
      if (session.status === 'active') {
        const idleTime = now - session.lastActivity.getTime();
        
        if (idleTime > this.config.idleTimeout) {
          session.status = 'idle';
          this.emit('session:idle', session);
        }
      }
    }
    
    // Expire sessions
    for (const sessionId of sessionsToExpire) {
      this.expireSession(sessionId);
    }
  }
  
  /**
   * Expire a session
   */
  private expireSession(sessionId: string): void {
    const session = this.sessions.get(sessionId);
    
    if (!session) {
      return;
    }
    
    session.status = 'expired';
    
    this.addSessionEvent(session, 'expired');
    
    this.logger.info(`Session ${sessionId} expired`);
    this.emit('session:expired', session);
    
    // Keep expired sessions for a while before removing
    setTimeout(() => {
      this.terminateSession(sessionId, 'expired');
    }, 60000); // Remove after 1 minute
  }
  
  /**
   * Check if session is expired
   */
  private isSessionExpired(session: Session): boolean {
    return session.expiresAt.getTime() <= Date.now();
  }
  
  /**
   * Add session event
   */
  private addSessionEvent(
    session: Session,
    type: SessionEvent['type'],
    data?: any
  ): void {
    const event: SessionEvent = {
      id: uuidv4(),
      timestamp: new Date(),
      type,
      data
    };
    
    session.context.history.push(event);
    
    // Limit history size
    if (session.context.history.length > 100) {
      session.context.history.shift();
    }
  }
  
  /**
   * Schedule expiry warning
   */
  private scheduleExpiryWarning(session: Session): void {
    const warningTime = session.expiresAt.getTime() - this.config.warningThreshold;
    const delay = warningTime - Date.now();
    
    if (delay > 0) {
      setTimeout(() => {
        if (this.sessions.has(session.id) && session.status === 'active') {
          this.logger.warn(`Session ${session.id} expiring soon`);
          this.emit('session:expiring', session);
        }
      }, delay);
    }
  }
  
  /**
   * Start cleanup process
   */
  private startCleanupProcess(): void {
    // Run cleanup every minute
    this.cleanupInterval = setInterval(() => {
      this.cleanupExpiredSessions();
    }, 60000);
    
    this.logger.info('Session cleanup process started');
  }
  
  /**
   * Stop cleanup process
   */
  stopCleanupProcess(): void {
    if (this.cleanupInterval) {
      clearInterval(this.cleanupInterval);
      this.cleanupInterval = null;
      this.logger.info('Session cleanup process stopped');
    }
  }
  
  /**
   * Destroy manager
   */
  destroy(): void {
    this.stopCleanupProcess();
    
    // Terminate all sessions
    for (const sessionId of this.sessions.keys()) {
      this.terminateSession(sessionId, 'manager destroyed');
    }
    
    this.sessions.clear();
    this.userSessions.clear();
    
    this.removeAllListeners();
  }
}

// Export singleton instance
export const sessionManager = new SessionManager();