// backend/src/memory/session-manager.ts
export interface Session {
  id: string;
  userId?: string;
  agentId?: string;
  data: Record<string, any>;
  createdAt: Date;
  lastAccessedAt: Date;
  expiresAt?: Date;
}

export class SessionManager {
  private sessions: Map<string, Session> = new Map();
  private cleanupInterval!: NodeJS.Timer;

  constructor(private defaultTTL: number = 3600000) { // 1 hour
    this.startCleanup();
  }

  // Create new session
  createSession(userId?: string, agentId?: string, ttl?: number): string {
    const sessionId = this.generateSessionId();
    const now = new Date();
    
    const session: Session = {
      id: sessionId,
      userId,
      agentId,
      data: {},
      createdAt: now,
      lastAccessedAt: now,
      expiresAt: ttl ? new Date(now.getTime() + ttl) : new Date(now.getTime() + this.defaultTTL)
    };

    this.sessions.set(sessionId, session);
    return sessionId;
  }

  // Get session
  getSession(sessionId: string): Session | null {
    const session = this.sessions.get(sessionId);
    if (!session) return null;

    // Check expiration
    if (session.expiresAt && session.expiresAt < new Date()) {
      this.sessions.delete(sessionId);
      return null;
    }

    // Update last accessed
    session.lastAccessedAt = new Date();
    return session;
  }

  // Update session data
  updateSession(sessionId: string, data: Record<string, any>): boolean {
    const session = this.getSession(sessionId);
    if (!session) return false;

    session.data = { ...session.data, ...data };
    return true;
  }

  // Set session data
  setSessionData(sessionId: string, key: string, value: any): boolean {
    const session = this.getSession(sessionId);
    if (!session) return false;

    session.data[key] = value;
    return true;
  }

  // Get session data
  getSessionData(sessionId: string, key?: string): any {
    const session = this.getSession(sessionId);
    if (!session) return null;

    return key ? session.data[key] : session.data;
  }

  // Extend session
  extendSession(sessionId: string, additionalTime: number): boolean {
    const session = this.getSession(sessionId);
    if (!session) return false;

    if (session.expiresAt) {
      session.expiresAt = new Date(session.expiresAt.getTime() + additionalTime);
    }
    return true;
  }

  // Delete session
  deleteSession(sessionId: string): boolean {
    return this.sessions.delete(sessionId);
  }

  // Get sessions by user
  getUserSessions(userId: string): Session[] {
    return Array.from(this.sessions.values())
      .filter(session => session.userId === userId);
  }

  // Get sessions by agent
  getAgentSessions(agentId: string): Session[] {
    return Array.from(this.sessions.values())
      .filter(session => session.agentId === agentId);
  }

  // Cleanup expired sessions
  private cleanup(): void {
    const now = new Date();
    for (const [sessionId, session] of this.sessions) {
      if (session.expiresAt && session.expiresAt < now) {
        this.sessions.delete(sessionId);
      }
    }
  }

  private startCleanup(): void {
    this.cleanupInterval = setInterval(() => this.cleanup(), 300000); // 5 minutes
  }

  private generateSessionId(): string {
    return `sess_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  getStats(): {
    totalSessions: number;
    activeSessions: number;
    expiredSessions: number;
    userSessions: Record<string, number>;
  } {
    const now = new Date();
    let activeSessions = 0;
    let expiredSessions = 0;
    const userSessions: Record<string, number> = {};

    for (const session of this.sessions.values()) {
      if (session.expiresAt && session.expiresAt < now) {
        expiredSessions++;
      } else {
        activeSessions++;
      }

      if (session.userId) {
        userSessions[session.userId] = (userSessions[session.userId] || 0) + 1;
      }
    }

    return {
      totalSessions: this.sessions.size,
      activeSessions,
      expiredSessions,
      userSessions
    };
  }
}